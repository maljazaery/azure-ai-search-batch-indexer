# Azure AI Document Intelligence  - Batch Processing
# This code demonstrates an example of using [LangChain](https://www.langchain.com/) to delvelop AI based PDF file processer and chunker using parallel processing with multi endpoints. It uses Azure AI Document Intelligence as document loader, which can extracts tables, paragraphs, and layout information from pdf, image, office and html files. The output markdown can be used in LangChain's markdown header splitter, which enables semantic chunking of the documents. 

# ## Prerequisites
from langchain_community.document_loaders import AzureAIDocumentIntelligenceLoader
from langchain.text_splitter import MarkdownHeaderTextSplitter,TokenTextSplitter
import concurrent.futures
import os
import random
import yaml
import argparse
from datetime import datetime, timedelta
import json
from openai import AzureOpenAI
from tenacity import retry, wait_random_exponential, stop_after_attempt 
import re
from azure.search.documents import SearchClient  
from azure.core.credentials import AzureKeyCredential 
from langchain_openai import AzureOpenAIEmbeddings


# Create the parser
parser = argparse.ArgumentParser(description="Process some files.")

# Add the arguments
parser.add_argument('input_dir', type=str, help="The directory containing the input files.")
parser.add_argument('output_dir', type=str, help="The directory to write the output files.")
parser.add_argument('config_file', type=str, help="The config file.")

# Parse the arguments
args = parser.parse_args()

# Get the directories from the arguments
input_dir = args.input_dir
OUTPUT_DIR = args.output_dir
config_file = args.config_file


if not os.path.exists(OUTPUT_DIR):
    # If not, create it
    os.makedirs(OUTPUT_DIR)


print("input_dir:", input_dir)
print("output_dir:", OUTPUT_DIR)

# Load configuration from YAML file
with open(config_file, 'r') as stream:
    config = yaml.safe_load(stream)


def normalize_text(s, sep_token = " \n "):
    s = re.sub(r'\s+',  ' ', s).strip()
    s = re.sub(r". ,","",s)
    # remove all instances of multiple spaces
    s = s.replace("..",".")
    s = s.replace(". .",".")
    s = s.replace("\n", "")
    s = s.strip()
    
    return s


# Create an instance of the AzureOpenAIEmbeddings class
embeddings = AzureOpenAIEmbeddings(
    azure_endpoint = config["openai_api_base"],
    azure_deployment=config["embeddings_model_name"],
    openai_api_version=config["openai_api_version"],
    openai_api_key= config["openai_api_key"]

)

@retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(6))
def generate_embeddings(text):
    return embeddings.embed_query(normalize_text(text))
 
azure_search_endpoint=config["azure_search_url"]
azure_search_key=config["azure_search_key"]
index_name=config["azure_search_index_name"]

search_client = SearchClient(endpoint=azure_search_endpoint, index_name=index_name, credential=AzureKeyCredential(azure_search_key))


headers_to_split_on = [
        ("#", "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3"),
        ]
markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)

text_splitter = TokenTextSplitter(chunk_size=config["chunk_size"], chunk_overlap=config["chunk_overlap"])




# Function to save the parsed text to a file
def save_parsed_text(file_path, doc_string):
    # Get the base name of the file
    ext = "." + file_path.split(".")[-1]
    base_name = file_path.replace(input_dir, "").replace(ext, ".txt")
    # Create the output file path
    output_file = OUTPUT_DIR +"/" + base_name
    print(output_file)
    # Write the doc_string to the output file
    with open(output_file, 'w') as f:
        f.write(doc_string)
    



# Function to process the document
def load_and_parse(file_path):
    # Choose a random endpoint-key pair
    endpoints_keys = config['doc_intel_endpoints_keys']
    endpoint_key = random.choice(endpoints_keys)
    endpoint = endpoint_key['endpoint']
    key = endpoint_key['key']
    print(f"processing {file_path}, Using endpoint: {endpoint}")
    try:
        loader = AzureAIDocumentIntelligenceLoader(file_path=file_path, api_key = key, api_endpoint = endpoint, api_model="prebuilt-layout")
        doc = loader.load()
        output_txt = doc[0].page_content
    except Exception as e:
        print(f"Error in doc intelligence loader, file {file_path}: {str(e)}")

    # Save the parsed text to a file
    try:
        save_parsed_text(file_path, output_txt)
    except Exception as e:
        print(f"Error in saving text from intelligence loader, file {file_path}: {str(e)}")

    # Split the output into chunks
    content = output_txt
    try:
        md_header_splits = markdown_splitter.split_text(content)
    except Exception as e:
        print(f"Error in markdown_splitter, file {file_path}: {str(e)}")

    documents = []
    section_counter = 0
    total_sections = len(md_header_splits)
    chunk_id = 0
    for s in md_header_splits:
        try:
            section_counter+=1
            section_content = s.page_content
            chunks = text_splitter.split_text(section_content)
            #print ('Processing Section:', section_counter, 'of', total_sections, 'with', len(chunks), 'chunks...')

            if chunks != []:
                for chunk in chunks:
                    json_data = {} 
                    json_data["file_name"] = os.path.basename(file_path)
                    json_data["last_updated"] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
                    json_data["chunk_id"] = str(chunk_id)
                    json_data["chunk"] = chunk
                    #json_data["title"] = generate_title(json_data['chunk'])
                    chunk_content = "File Name: " + json_data["file_name"] + "\n"
                    chunk_content += chunk
                    
                    json_data["vector"] = generate_embeddings(chunk_content)
                    chunk_id+=1
                    documents.append(json_data)
                    
            else:
                print (f'No content found for {file_path}')
        except Exception as e:
            print(f"Error in creating chunks and embedding, file {file_path}: {str(e)}")

    if len(documents) > 0:
        #print('Uploading ', len(documents), ' documents to Azure Search...')
        #upload the chunks to Azure Search
        try:
            search_client.upload_documents(documents)
        except Exception as e:
            print(f"Error in uploading doc to Azure AI Search index, file {file_path}: {str(e)}")

        # save as a json file
        try:
            ext = "." + file_path.split(".")[-1]
            base_name = os.path.basename(file_path).replace(ext, "")
            json_out_file = os.path.join(OUTPUT_DIR, base_name)+ ".json"
            with open(json_out_file, "w") as j_out:
                j_out.write(json.dumps(documents))
        except Exception as e:
            print(f"Error in saving json, file {file_path}: {str(e)}")

    
    return file_path





# List of files to process
files = [os.path.join(input_dir, file) for file in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, file))]

# Use ThreadPoolExecutor to process the files in parallel
with concurrent.futures.ThreadPoolExecutor() as executor:
    # Use list comprehension to get a list of futures
    futures = [executor.submit(load_and_parse, file) for file in files]
    
    for future in concurrent.futures.as_completed(futures):
        file_path = future.result()[0]
        print(f"Done processing: {file_path}")
        
        
        

