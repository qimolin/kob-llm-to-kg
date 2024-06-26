# kob-llm-to-kg
This repository is for converting [Kuching Old Bazaar](https://kcholdbazaar.com/) into a knowledge graph in Neo4j using Ollama and specifically the llama3 model.

## Table of Contents
- [Requirements](#requirements)
- [Usage of Web Scraper](#usage-of-web-scraper)
- [Features](#features-checklist)
- [neo4j](#neo4j)
  - [Automatic Setup](#automatic-setup)
  - [Ontology Import](#ontology-import)
  - [Data Import](#data-import)
- [Docker Compose](#docker-compose)
  - [Ollama](#ollama)

## Requirements
- Docker
- Python

## Usage of Web Scraper
To start the application, follow these steps:
1. Go into app folder
   ```sh
   cd app
   ```
3. Create venv
    ```sh
    python -m venv .venv
    ```
4. Activate venv \
    On Windows:
    ```sh
    .venv\Scripts\activate
    ```
   On macOS and Linux:
   ```sh
   source .venv/bin/activate
   ```
6. Install requirements
   ```sh
   python -r requirements.txt
   ```
7. Run scraper
    ```sh
    python main.py
    ```

The webscraper carries out the following steps:
1. User inputs a kcholdbazaar.com page URL (``get_inp_url``).
2. The page is retrieved (``get_url``) and the English text from the page is retrieved (``get_contents``)
3. The English page is fed into the LLM along with the ontology (``send_to_ollama``). The LLM then returns nodes and relationships, which have to be processed. For each node or relationship, the given label ID needs to be checked, as the LLM sometimes gives incorrect labels. If a label is not part of the ontology, it is checked without the ID and, if there is a match, is returned with the proper ID (``check_if_in_ontology``).
4. The nodes and relationships are written to a CSV file in the ``app/outputs/`` folder.
5. The nodes and relationships are stored in the Neo4j database (``load_content_to_database``)

The prompt that is currently used was arrived at through trial-and-error, and it is still far from perfect. So those that want to improve it do not have to start completely over, some attempted prompts and their outputs have been stored in ``app/outputs/prompts_in_out.md``.

## Features checklist
- [x] Dockerized application (neo4j, ollama, ollama ui, python webscraper)
- [x] Python web scraper
- [x] Allow user to use CLI to specify target website
- [x] Import existing ontology into neo4j
- [x] Import data into neo4j
- [x] Test prompts derived from [NaLLM](https://github.com/neo4j/NaLLM)
- [x] Output data into useful format (csv) 
- [ ] Test with bigger models for potentially better results
- [ ] Integrate knowledge graph into [Kuching Old Bazaar](https://kcholdbazaar.com/)

# neo4j 

In this section, the requriements and steps to setup the neo4j database are described. Further the loading of the Data into the database is described, as well as the constraint of these steps.

## Automatic Setup

When the neo4j container is started, the following steps are automatically executed:
- The APOC and neosemantics libraries are installed
- The unique uri constraint is created (if it does not exist)

The APOC library is used to load files into the database, while the neosemantics library enables neo4j to handle RDF data. To reproduce this in a docker environment, the plugins need to be named in the environment variable `NEO4J_PLUGINS`, and provided as a list. In a native install, the plugins need to be placed in the `plugins` folder of the neo4j installation, as jar files. See the [neo4j documentation](https://neo4j.com/docs/operations-manual/current/configuration/plugins/) for more information.  
The unique uri constraint is created to ensure that the uri of the nodes is unique. This is important for the data import, as the uri is used to identify the nodes.

## Ontology Import

To import the CIDOC-CRM ontology, follow these steps, it is required every time the data folder has been emptied:
- start docker container
- run the following command in the [neo4j browser](https://neo4j.com/docs/browser-manual/current/about-browser/)

``` cypher
CALL n10s.graphconfig.init({ handleVocabUris: 'MAP'})
CALL n10s.onto.import.fetch("https://cidoc-crm.org/rdfs/7.1.3/CIDOC_CRM_v7.1.3.rdfs","RDF/XML");
```

## Data Import

The data is imported at the execution of the python script, once the data has been extracted from the LLM. It is expected to have the data available in the csv format. The generated data is then split into 2 files, one for the nodes and one for the relationships. The rows with the nodes start with an integer value. The relationship rows are updated, so that the id of the node is used instad of the table row number.  
The data is then loaded into the neo4j database using the APOC library. First the nodes are loaded, then the relationships. The following cypher commands are used to load the data.  
The following settings need to be set in the neo4j.conf file (if the file does not exist in the conf folder, create it) to allow the import of csv files from the file system:

```conf
dbms.directories.import=import
dbms.security.allow_csv_import_from_file_urls=true
```

### Limitations
If the the script is executed multiple times, the data is appended to the database. This can be solved by bounding the UUID to a set of properties of each node, e.g. name, type, label. Additionally, are the nodes not properly labeled, which may be due to a not optimal formulated cypher query, may be solved by replacing :n with csvLine._labels. As indicated in the code the neo4j password should not be hardcoded.

# Docker Compose
## Ollama
Using CPU for ollama
``` bash
docker-compose up -d
```

Using AMD GPU for ollama
``` bash
docker compose -f docker-compose-amd.yml up -d
```

Using NVIDIA GPU for ollama
``` bash
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg \
  && curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
    sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
    sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit

# Configure NVIDIA Container Toolkit
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker

# Test GPU integration
docker run --gpus all nvidia/cuda:11.5.2-base-ubuntu20.04 nvidia-smi

docker compose -f docker-compose-nvidia.yml up -d
```
