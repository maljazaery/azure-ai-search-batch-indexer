
# Azure Document Layout Parser - batch processing using multi endpoints
This script is designed to batch process documents using Azure Document Intelligence Service. It transforms unstructured text into a structured markdown format, which facilitates the identification of section breakpoints, as well as, generating a better text represetaions for table data. This is particularly useful in the development of RAG AI application.

## Requirements
- Azure AI Document Intelligence resources in one of the 3 preview regions: **East US**, **West US2**, **West Europe** - follow [this document](https://learn.microsoft.com/azure/ai-services/document-intelligence/create-document-intelligence-resource?view=doc-intel-4.0.0) to create one if you don't have.

## Installation
pip install requirements.txt

## Usage

You can run the script from the command line like this:

```bash
python main.py /path/to/input/directory /path/to/output/directory /path/to/config/file
```
## Arguments:
input_dir: The directory containing the input document files.
output_dir: The directory to write the output files.
config_file: The configuration file.

## Note:
This is unofficial Microsoft product.



