# kob-llm-to-kg

# neo4j 

manual docker command
``` cli
docker run --name testneo4j -p7474:7474 -p7687:7687 -d -v $HOME/neo4j/data:/data -v $HOME/neo4j/logs:/logs -v $HOME/neo4j/import:/var/lib/neo4j/import -v $HOME/neo4j/plugins:/plugins -v $HOME/neo4j/conf:/conf --env NEO4JLABS_PLUGINS='["apoc", "n10s"]' --env NEO4J_AUTH=neo4j/helloworld neo4j:latest
```
n10s install
- copy the n10s jar file to the plugins folder, that will be mounted into the container
- start docker container
- run the following command in the neo4j browser
``` cypher
CREATE CONSTRAINT n10s_unique_uri FOR (r:Resource) REQUIRE r.uri IS UNIQUE
CALL n10s.graphconfig.init({ handleVocabUris: 'MAP'})
CALL n10s.onto.import.fetch("https://cidoc-crm.org/rdfs/7.1.3/CIDOC_CRM_v7.1.3_JSON-LD_Context.jsonld","JSON-LD");
```
- done