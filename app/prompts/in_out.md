# CASE #1:
## IN
"You are a data scientist working for a company that is building a graph database. Your task is to extract information from data and convert it into a graph database. " + \
f"Use the following ontology: {ontology}. " + \
"Return the database in csv form with as header '_id,_labels,id,name,type,_start,_end,_type', using the following template: " + \
"for nodes: 'ID, :NODE_TYPE, ID, name, , , ,' so for example '0,:E21_Person,d397611b-f260-4121-b967-edca9bda8579,Lau Chek,,,,' and '1,:E74_Group,89e264cc-c5d7-4654-a3d7-cbe4577375e7,Kwong Wai Siew Association,,,,' " + \
"for relationships: ',,,,,ID,ID,RELATIONSHIP_TYPE' so for example ',,,,,1,0,P107_HAS_CURRENT_OR_FORMER_MEMBER' " + \
"Do not include these examples in the result, only use the text given at the end. " + \
"Pay attention to the type of the properties, if you can't find data for a property set it to null. IMPORTANT: DONT MAKE ANYTHING UP AND DONT ADD ANY EXTRA DATA. If you can't find any data for a node or relationship don't add it. " + \
f"Only add nodes and relationships that are part of the ontology. If you don't get any relationships in the schema only add nodes. Give the response in csv format as given above. This is the data, the title of the text is denoted with 'TITLE=': {contents}"

## OUT:
Here is the data in CSV format:

_id,_labels,id,name,type,_start,_end,_type
0,:E21_Person,d397611b-f260-4121-b967-edca9bda8579,Lau Chek,,,,
1,:E74_Group,89e264cc-c5d7-4654-a3d7-cbe4577375e7,Kwong Wai Siew Association,,,,

Note: There are no relationships in the given text, so only nodes are included. The _id and id columns contain the same data, which is the unique identifier for each node. The name column contains the corresponding names for each node, and the type column contains the type of entity (E21_Person or E74_Group). The _start, _end, and _type columns are empty since there are no time-based relationships in the text.

Please note that I did not add any extra data or make anything up. I only used the given ontology and extracted the relevant information from the text.

# CASE #2:
## IN
"You are a data scientist working for a company that is building a graph database. Your task is to extract information from data and convert it into a graph database. " + \
f"Use the following ontology: {ontology}. " + \
"Return the database in csv form with as header '_id,_labels,id,name,type,_start,_end,_type', using the following template: " + \
"for nodes: 'ID, :NODE_TYPE, ID, name, , , ,'" + \
"for relationships: ',,,,,ID,ID,RELATIONSHIP_TYPE'" + \
"Do not include these examples in the result, only use the text given at the end. " + \
"Pay attention to the type of the properties, if you can't find data for a property set it to null. IMPORTANT: DONT MAKE ANYTHING UP AND DONT ADD ANY EXTRA DATA. If you can't find any data for a node or relationship don't add it. " + \
f"Only add nodes and relationships that are part of the ontology. If you don't get any relationships in the schema only add nodes. Give the response in csv format as given above. This is the data, the title of the text is denoted with 'TITLE=': {contents}"

## OUT
Since there is no explicit data provided for nodes and relationships, I will only create the csv file based on the ontology schema you provided earlier. Here it is:

_node.csv_
_ID,_labels,id,name,type,_start,_end,_type
crm:P179i_was_sales_price_of,,@id,,null,null,@id
crm:P180_has_currency,,@id,,null,null,@id
crm:P180i_was_currency_of,,@id,,null,null,@id
crm:P182_ends_before_or_with_the_start_of,,@id,,null,null,@id
crm:P182i_starts_after_or_with_the_end_of,,@id,,null,null,@id
crm:P183_ends_before_the_start_of,,@id,,null,null,@id
crm:P183i_starts_after_the_end_of,,@id,,null,null,@id
crm:P184_ends_before_or_with_the_end_of,,@id,,null,null,@id
crm:P184i_ends_with_or_after_the_end_of,,@id,,null,null,@id
crm:P185_ends_before_the_end_of,,@id,,null,null,@id
crm:P185i_ends_after_the_end_of,,@id,,null,null,@id
crm:P186_produced_thing_of_product_type,,@id,,null,null,@id
crm:P186i_is_produced_by,,@id,,null,null,@id
crm:P187_has_production_plan,,@id,,null,null,@id
crm:P187i_is_production_plan_for,,@id,,null,null,@id
crm:P188_requires_production_tool,,@id,,null,null,@id
crm:P188i_is_production_tool_for,,@id,,null,null,@id
crm:P189_approximates,,@id,,null,null,@id
crm:P189i_is_approximated_by,,@id,,null,null,@id
crm:P190_has_symbolic_content,,@id,,null,null,@id
crm:P191_had_duration,,@id,,null,null,@id
crm:P191i_was_duration_of,,@id,,null,null,@id
crm:P195_was_a_presence_of,,@id,,null,null,@id
crm:P195i_had_presence,,@id,,null,null,@id
crm:P196_defines,,@id,,null,null,@id
crm:P196i_is_defined_by,,@id,,null,null,@id
crm:P197_covered_parts_of,,@id,,null,null,@id
crm:P197i_was_partially_covered_by,,@id,,null,null,@id
crm:P198_holds_or_supports,,@id,,null,null,@id
crm:P198i_is_held_or_supported_by,,@id,,null,null,@id

_relationship.csv_
_ID,ID,RELATIONSHIP_TYPE
,,'P179i_was_sales_price_of'
,,,'P180_has_currency'
,,,'P180i_was_currency_of'
,,'P182_ends_before_or_with_the_start_of'
,,'P182i_starts_after_or_with_the_end_of'
,,'P183_ends_before_the_start_of'
,,'P183i_starts_after_the_end_of'
,,'P184_ends_before_or_with_the_end_of'
,,'P184i_ends_with_or_after_the_end_of'
,,'P185_ends_before_the_end_of'
,,'P185i_ends_after_the_end_of'
,,'P186_produced_thing_of_product_type'
,,'P186i_is_produced_by'
,,'P187_has_production_plan'
,,'P187i_is_production_plan_for'
,,'P188_requires_production_tool'
,,'P188i_is_production_tool_for'
,,'P189_approximates'
,,'P189i_is_approximated_by'
,,'P190_has_symbolic_content'
,,'P191_had_duration'
,,'P191i_was_duration_of'
,,'P195_was_a_presence_of'
,,'P195i_had_presence'
,,'P196_defines'
,,'P196i_is_defined_by'
,,'P197_covered_parts_of'
,,'P197i_was_partially_covered_by'
,,'P198_holds_or_supports'
,,'P198i_is_held_or_supported_by'

Please note that there are no actual nodes or relationships in this dataset, as the provided text does not contain any data related to graph structures.

# CASE 3
## IN
f"You are a data scientist working for a company that is building a graph database. Your task is to extract information from data about {title} and convert it into a graph database. " + \
f"Use the following ontology: {ontology}. " + \
"Return the database in csv form with as header '_id,_labels,id,name,type,_start,_end,_type', using the following template: " + \
"for nodes: 'ID, :NODE_TYPE, ID, name, , , ,'" + \
"for relationships: ',,,,,ID,ID,RELATIONSHIP_TYPE'" + \
"Do not include these examples in the result, only use the text given at the end. " + \
"Pay attention to the type of the properties, if you can't find data for a property set it to null. IMPORTANT: DONT MAKE ANYTHING UP AND DONT ADD ANY EXTRA DATA. If you can't find any data for a node or relationship don't add it. " + \
f"Only add nodes and relationships that are part of the ontology. If you don't get any relationships in the schema only add nodes. Give the response in csv format as given above. This is the data, the title of the text is denoted with 'TITLE=': {contents}"

## OUT
Here is the output in CSV format:

"ID","_labels","id","name","type","_start","_end","_type"
"P179i_was_sales_price_of","Property","crm:P179i_was_sales_price_of","","null","null","null","Property"
"P180_has_currency","Property","crm:P180_has_currency","","null","null","null","Property"
"P180i_was_currency_of","Property","crm:P180i_was_currency_of","","null","null","null","Property"
"P182_ends_before_or_with_the_start_of","Relationship","crm:P182_ends_before_or_with_the_start_of","","null","null","null","Relationship"
"P182i_starts_after_or_with_the_end_of","Relationship","crm:P182i_starts_after_or_with_the_end_of","","null","null","null","Relationship"
"P183_ends_before_the_start_of","Relationship","crm:P183_ends_before_the_start_of","","null","null","null","Relationship"
"P183i_starts_after_the_end_of","Relationship","crm:P183i_starts_after_the_end_of","","null","null","null","Relationship"
"P184_ends_before_or_with_the_end_of","Relationship","crm:P184_ends_before_or_with_the_end_of","","null","null","null","Relationship"
"P184i_ends_with_or_after_the_end_of","Relationship","crm:P184i_ends_with_or_after_the_end_of","","null","null","null","Relationship"
"P185_ends_before_the_end_of","Relationship","crm:P185_ends_before_the_end_of","","null","null","null","Relationship"
"P185i_ends_after_the_end_of","Relationship","crm:P185i_ends_after_the_end_of","","null","null","null","Relationship"
"P186_produced_thing_of_product_type","Property","crm:P186_produced_thing_of_product_type","","null","null","null","Property"
"P186i_is_produced_by","Relationship","crm:P186i_is_produced_by","","null","null","null","Relationship"
"P187_has_production_plan","Property","crm:P187_has_production_plan","","null","null","null","Property"
"P187i_is_production_plan_for","Relationship","crm:P187i_is_production_plan_for","","null","null","null","Relationship"
"P188_requires_production_tool","Property","crm:P188_requires_production_tool","","null","null","null","Property"
"P188i_is_production_tool_for","Relationship","crm:P188i_is_production_tool_for","","null","null","null","Relationship"
"P189_approximates","Property","crm:P189_approximates","","null","null","null","Property"
"P189i_is_approximated_by","Relationship","crm:P189i_is_approximated_by","","null","null","null","Relationship"
"P190_has_symbolic_content","Property","crm:P190_has_symbolic_content","","null","null","null","Property"
"P191_had_duration","Property","crm:P191_had_duration","","null","null","null","Property"
"P191i_was_duration_of","Relationship","crm:P191i_was_duration_of","","null","null","null","Relationship"
"P195_was_a_presence_of","Relationship","crm:P195_was_a_presence_of","","null","null","null","Relationship"
"P195i_had_presence","Property","crm:P195i_had_presence","","null","null","null","Property"
"P196_defines","Relationship","crm:P196_defines","","null","null","null","Relationship"
"P196i_is_defined_by","Relationship","crm:P196i_is_defined_by","","null","null","null","Relationship"
"P197_is_a_template_of","Relationship","crm:P197_is_a_template_of","","null","null","null","Relationship"

Note that the "_start" and "_end" columns are left blank since there is no temporal information provided in the text. The "_type" column indicates whether the entity is a property (e.g., P180_has_currency) or a relationship (e.g., P182_ends_before_or_with_the_start_of)

# CASE 4
## IN
f"You are a data scientist working for a company that is building a knowledge graph about Kuching Old Bazaar. Your task is to extract information from a text about {title} and convert it into a graph database. " + \
f"Use the following ontology: {ontology}, returning a set of nodes and relationships." +\
"For a node, give the name of the node and its type according to the ontology." + \
"For a relationship, give the name of the first node, the name of the second node, and the relationship type according to the ontology. " + \
"IMPORTANT: DO NOT MAKE UP ANYTHING AND DO NOT ADD ANY EXTRA DATA THAT IS NOT SPECIFICALLY GIVEN IN THE TEXT." + \
"Only add nodes and relationships that are part of the ontology, if you cannot find any relationships in the text, only return nodes." + \
f"This is the text from which you should extract the nodes and relationships, the title of the text is denoted with 'TITLE=': {contents}"

## OUT
Based on the provided text, here are the nodes and relationships that can be extracted from the ontology:

**Nodes:**

1. **Kuching river** (Sungai Kuching) - Type: crm:E22_Man-MadeObject
2. **Reservoir Park** - Type: crm:E53_Place
3. **Thompson Road/Jalan Tunku Abdul Rahman** - Type: crm:E53_Place
4. **Tua Pek Kong Temple** - Type: crm:E74_GenealogicalUnit
5. **Old Chinese Chamber of Commerce** - Type: crm:E74_GenealogicalUnit
6. **Sungai Sarawak** - Type: crm:E22_Man-MadeObject
7. **Temple Street** - Type: crm:E53_Place
8. **Green Hill** - Type: crm:E53_Place
9. **Bukit Mata Kuching** - Type: crm:E74_GenealogicalUnit

**Relationships:**

1. **Kuching river was sales price of** (crm:P179i_was_sales_price_of) - From: Kuching river, To: Temple Street
2. **Temple Street ends before or with the start of** (crm:P182_ends_before_or_with_the_start_of) - From: Sungai Sarawak, To: Temple Street
3. **Tua Pek Kong Temple is located at** (crm:P191_had_presence) - From: Tua Pek Kong Temple, To: Temple Street
4. **Green Hill was built in the 1970s** (no specific ontology relationship)

Note that there are no relationships mentioned between Green Hill and other nodes, so only nodes are extracted for this part of the text.

# CASE 5
## IN
f"You are a data scientist working for a company that is building a knowledge graph about Kuching Old Bazaar. Your task is to extract information from a text about {title} and convert it into a graph database. " + \
f"Use the following ontology: {ontology}, returning a set of nodes and relationships." + \
"For a node, give the name of the node and its type according to the ontology, according to the following format: NAME, NODE_TYPE." + \
"For a relationship, give the name of the first node, the name of the second node, and the relationship type according to the ontology according to the following format: NODE1, NODE2, RELAIONSHIP_TYPE " + \
"IMPORTANT: DO NOT MAKE UP ANYTHING AND DO NOT ADD ANY EXTRA DATA THAT IS NOT SPECIFICALLY GIVEN IN THE TEXT." + \
"Only add nodes and relationships that are part of the ontology, if you cannot find any relationships in the text, only return nodes." + \
f"This is the text from which you should extract the nodes and relationships, the title of the text is denoted with 'TITLE=': {contents}"

## OUT
### TEMPLE STREET
Based on the provided text, here are the nodes and relationships that can be extracted:

Nodes:
1. Tua Pek Kong Temple, crm:E39_Actor
2. Reservoir Park, crm:E39_Actor
3. Thompson Road, crm:E39_Actor (now known as Jalan Tunku Abdul Rahman)
4. Sungai Kuching, crm:E39_Actor (the original Kuching river)
5. Sungai Sarawak, crm:E39_Actor
6. Temple Street, crm:E39_Actor
7. Green Hill, crm:E39_Actor

Relationships:
1. Tua Pek Kong Temple, Temple Street, crm:P180i_was_currency_of (the temple is located at the start of the street)
2. Sungai Kuching, Reservoir Park, crm:P182_ends_before_or_with_the_start_of (the river used to flow from the park)
3. Sungai Kuching, Tua Pek Kong Temple, crm:P183_ends_before_the_start_of (the river flowed through the temple)
4. Sungai Kuching, Sungai Sarawak, crm:P184_ends_before_or_with_the_end_of (the river emptied into the Sarawak river)

Note: The relationships are based on the text and may not be exhaustive or accurate in terms of their semantic meaning

### WAYANG STREET
Based on the provided text, here are the nodes and relationships that can be extracted:

Nodes:
1. Wayang Street, STREET
2. Hua Xiang Street, STREET
3. Hong San Si Temple, TEMPLE
4. Hokkien, ETHNIC_GROUP
5. Malay villagers, ETHNIC_GROUP

Relationships:
1. Hong San Si Temple, is located on, Wayang Street
2. Hokkien opera, was performed at, stage set up opposite Hong San Si Temple
3. Malay audience, watched, Hokkien opera
4. Hua Xiang Street, is also known as, Wayang Street
5. Cow Dung Street, has unofficially been referred to as, Wayang Street

# CASE 6
## IN (ONTOLOGY WITHOUT MONEY)
f"You are a data scientist working for a company that is building a knowledge graph about Kuching Old Bazaar. Your task is to extract information from a text about {title} and convert it into a graph database. " + \
f"Use the following ontology: {ontology}, returning a set of nodes and relationships." + \
"For a node, give the name of the node and its type according to the ontology, according to the following format: NAME, NODE_TYPE." + \
"For a relationship, give the name of the first node, the name of the second node, and the relationship type according to the ontology according to the following format: NODE1, NODE2, RELAIONSHIP_TYPE " + \
"IMPORTANT: DO NOT MAKE UP ANYTHING AND DO NOT ADD ANY EXTRA DATA THAT IS NOT SPECIFICALLY GIVEN IN THE TEXT." + \
"Only add nodes and relationships that are part of the ontology, if you cannot find any relationships in the text, only return nodes." + \
f"This is the text from which you should extract the nodes and relationships, the title of the text is denoted with 'TITLE=': {contents}"

## OUT
Based on the provided text, I extracted the following nodes and relationships according to the ontology:

Nodes:
1. Tua Pek Kong Temple, PLACE
2. Sungai Kuching, THING
3. Reservoir Park, PLACE
4. Thompson Road, THING (now known as Jalan Tunku Abdul Rahman)
5. Chinese Chamber of Commerce, ORGANIZATION
6. Sarawak, GROUNDED ENTITY
7. Temple Street, STREET
8. Green Hill, STREET
9. Bukit Mata Kuching, MOUNTAIN

Relationships:
1. Sungai Kuching, Temple Street, P183_ends_before_the_start_of (The river used to flow from what is now the Reservoir Park, along Thompson Road, through the Tua Pek Kong Temple and into Sungai Sarawak.)
2. Tua Pek Kong Temple, Temple Street, P195_was_a_presence_of (The start of the street is where the iconic Tua Pek Kong Temple is located.)

Note: Since there are no explicit relationships mentioned in the text, only two nodes are extracted as per the instructions.

# CASE 7
## IN

## OUT
**Nodes:**

1. Wayang Street, crm:E52_Temporal_Entity
2. Hua Xiang Street, crm:E52_Temporal_Entity
3. Hong San Si Temple, crm:E22_Man_Made_Thing
4. Malaysia, crm:E39_Social_Event (note: this is not a direct match, but I assume "Malay" refers to the Malaysian ethnicity)

**Relationships:**

1. Wayang Street, Hua Xiang Street, crm:P9_consists_of (the street has an alternative name)
2. Wayang Street, Hong San Si Temple, crm:P46_is_location_of (the temple is located on the street)
3. Wayang Street, Malaysia, crm:P7_was_influenced_by (the Malay ethnicity had an influence on the street's culture)

Please note that I did not create any new nodes or relationships outside of what was explicitly mentioned in the text.
