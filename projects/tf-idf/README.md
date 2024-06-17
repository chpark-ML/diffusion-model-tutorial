# Neurips-Keyword-Analysis (2018-2023)

## Overview
This project focuses on extracting and analyzing keywords from NeurIPS papers between 2018 and 2023. The primary objectives are to extract essential information such as titles and abstracts from PDF files and to identify significant keywords for individual papers and for each year using TF-IDF (Term Frequency-Inverse Document Frequency) analysis.

### Features
- Extract information (title, abstract, etc.) from PDF files.
- Identify keywords for each paper using TF-IDF on the abstract.
- Determine yearly keywords using TF-IDF on aggregated data.

## Usage

### 1. Extract Keywords Based on TF-IDF
To extract keywords using TF-IDF, run the following shell script:

```sh
sh projects/tf-idf/run_neurips_csv.sh
```

### 2. Analysis of Keywords
For analyzing the extracted keywords, open and execute the provided Jupyter notebook:
```python3
projects/tf-idf/main.ipynb
```





