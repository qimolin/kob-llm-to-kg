# kob-llm-to-kg

# neo4j 

## Ontology Import
- start docker container
- run the following command in the neo4j browser
``` cypher
CALL n10s.graphconfig.init({ handleVocabUris: 'MAP'})
CALL n10s.onto.import.fetch("https://cidoc-crm.org/rdfs/7.1.3/CIDOC_CRM_v7.1.3.rdfs","RDF/XML");
```
- done

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