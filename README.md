
# Azure Document Parser and Indexer - Batch Processing Using Multiple Endpoints
This script is designed to batch process documents using Azure Document Intelligence Service and ingest them into Azure AI search index. 

It transforms doc unstructured text into a **structured markdown** format, which facilitates the identification of section breakpoints, as well as, generating a better text represetaions for table data. This is particularly useful in the development of RAG AI application. Then it chunks and indexes the doc into Azure search service.


## Features
- [x] Multi-threading (parallel processing).
- [x] Support for multiple Doc Intelligence endpoints.
- [x] Access to intermediate outputs.
- [x] Error handling.
- [x] Easy to configure.
- [x] Easy to customize code (Add new meta data to your index).
- [ ] Multiple embedding endpoints.
- [ ] Support other file formats, currently only PDFs.


## Requirements
- Azure AI Document Intelligence resources in one of the 3 preview regions: **East US**, **West US2**, **West Europe** - follow [this document](https://learn.microsoft.com/azure/ai-services/document-intelligence/create-document-intelligence-resource?view=doc-intel-4.0.0) to create one if you don't have.
- Azure AI Search rescource.
- Azure OpenAI Embedding endpoint.



## Installation

```bash
pip install requirements.txt
```

## Usage
1- Create an index using schema.json file. Edit the index name and embedding endpoint before you import it to the AI search portal.

2- Create a config file similar to config.yaml.example, and add the Azure Doc Intelligance and Azure AI Search  endpoints  to it. 

3- You can run the script from the command line like this:

```bash
python main.py /path/to/input/directory /path/to/output/directory /path/to/config/file
```
## Arguments:
- input_dir: The directory containing the input document files.
- output_dir: The directory to write the output files.
- config_file: Azure AI Document Intelligence endpoints.

## Results:
 - txt file of the raw markdown content saved to the output folder. 
 - Json file of all chunks saved to the output folder.
 - Chunks uploaded into the Azure AI search Index.


## Example of parsed content:

- Input: 
![sample](https://github.com/maljazaery/azure-doc-batch-processor/blob/main/sample.png)
- Output:
```
## Recent Accounting Guidance


### Segment Reporting - Improvements to Reportable Segment Disclosures

In November 2023, the Financial Accounting Standards Board ("FASB") issued a new standard to improve reportable segment disclosures. The guidance expands the disclosures required for reportable segments in our annual and interim consolidated financial statements, primarily through enhanced disclosures about significant segment expenses. The standard will be effective for us beginning with our annual reporting for fiscal year 2025 and interim periods thereafter, with early adoption permitted. We are currently evaluating the impact of this standard on our segment disclosures.


#### Income Taxes - Improvements to Income Tax Disclosures

In December 2023, the FASB issued a new standard to improve income tax disclosures. The guidance requires disclosure of disaggregated income taxes paid, prescribes standardized categories for the components of the effective tax rate reconciliation, and modifies other income tax-related disclosures. The standard will be effective for us beginning with our annual reporting for fiscal year 2026, with early adoption permitted. We are currently evaluating the impact of this standard on our income tax disclosures.


## NOTE 2 - EARNINGS PER SHARE

Basic earnings per share ("EPS") is computed based on the weighted average number of shares of common stock outstanding during the period. Diluted EPS is computed based on the weighted average number of shares of common stock plus the effect of dilutive potential common shares outstanding during the period using the treasury stock method. Dilutive potential common shares include outstanding stock options and stock awards.

The components of basic and diluted EPS were as follows:

| (In millions, except per share amounts) | Three Months Ended Six Months Ended December 31, December 31, ||||
| | 2023 | 2022 | 2023 | 2022 |
| - | - | - | - | - |
| Net income available for common shareholders (A) | $ 21,870 | $ 16,425 | $ 44,161 | $ 33,981 |
| Weighted average outstanding shares of common stock (B) | 7,432 | 7,451 | 7,431 | 7,454 |
| Dilutive effect of stock-based awards | 36 | 22 | 34 | 25 |
| Common stock and common stock equivalents (C) | 7,468 | 7,473 | 7,465 | 7,479 |
| Earnings Per Share | | | | |
| Basic (A/B) | $ 2.94 | $ 2.20 | $ 5.94 | $ 4.56 |
| Diluted (A/C) | $ 2.93 | $ 2.20 | $ 5.92 | $ 4.54 |

Anti-dilutive stock-based awards excluded from the calculations of diluted EPS were immaterial during the periods presented.

<!-- PageNumber="10" -->
```

## Acknowledgement
Part of the code is borrowed from [Azure AI Search - Python Based Content Vectorization and Enrichment](https://github.com/liamca/azure-ai-search-vector-indexing).

## Disclaimer:
This is NOT an official Microsoft product. 



