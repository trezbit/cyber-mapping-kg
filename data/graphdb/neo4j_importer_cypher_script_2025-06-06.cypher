:param {
  // Define the file path root and the individual file names required for loading.
  // https://neo4j.com/docs/operations-manual/current/configuration/file-locations/
  file_path_root: 'file:///', // Change this to the folder your script can access the files at.
  file_0: 'n_standards.csv',
  file_1: 'n_controls.csv',
  file_2: 'n_hipaa_impl.csv',
  file_3: 'e_stdcontrols.csv',
  file_4: 'e_controlmap.csv',
  file_5: 'e_ctrl_hipaa_impl.csv'
};

// CONSTRAINT creation
// -------------------
//
// Create node uniqueness constraints, ensuring no duplicates for the given node label and ID property exist in the database. This also ensures no duplicates are introduced in future.
//
// NOTE: The following constraint creation syntax is generated based on the current connected database version 5.27.0.
CREATE CONSTRAINT `std_id_standard_uniq` IF NOT EXISTS
FOR (n: `standard`)
REQUIRE (n.`std_id`) IS UNIQUE;
CREATE CONSTRAINT `ctrlid_control_uniq` IF NOT EXISTS
FOR (n: `control`)
REQUIRE (n.`ctrlid`) IS UNIQUE;
CREATE CONSTRAINT `chunk_id_hipaaimpl_uniq` IF NOT EXISTS
FOR (n: `hipaaimpl`)
REQUIRE (n.`chunk_id`) IS UNIQUE;


// INDEX creation
// -------------------
//
// Create node indexes
//
CREATE INDEX `label_standard` IF NOT EXISTS
FOR (n: `standard`)
ON (n.`label`);
CREATE INDEX `label_control` IF NOT EXISTS
FOR (n: `control`)
ON (n.`label`);
CREATE INDEX `label_hipaaimpl` IF NOT EXISTS
FOR (n: `hipaaimpl`)
ON (n.`label`);

:param {
  idsToSkip: []
};

// NODE load
// ---------
//
// Load nodes in batches, one node label at a time. Nodes will be created using a MERGE statement to ensure a node with the same label and ID property remains unique. Pre-existing nodes found by a MERGE statement will have their other properties set to the latest values encountered in a load file.
//
// NOTE: Any nodes with IDs in the 'idsToSkip' list parameter will not be loaded.
LOAD CSV WITH HEADERS FROM ($file_path_root + $file_0) AS row
WITH row
WHERE NOT row.`std_id` IN $idsToSkip AND NOT toInteger(trim(row.`std_id`)) IS NULL
CALL {
  WITH row
  MERGE (n: `standard` { `std_id`: toInteger(trim(row.`std_id`)) })
  SET n.`std_id` = toInteger(trim(row.`std_id`))
  SET n.`label` = row.`label`
  SET n.`title` = row.`title`
  SET n.`type` = row.`type`
} IN TRANSACTIONS OF 10000 ROWS;

LOAD CSV WITH HEADERS FROM ($file_path_root + $file_1) AS row
WITH row
WHERE NOT row.`ctrlid` IN $idsToSkip AND NOT toInteger(trim(row.`ctrlid`)) IS NULL
CALL {
  WITH row
  MERGE (n: `control` { `ctrlid`: toInteger(trim(row.`ctrlid`)) })
  SET n.`ctrlid` = toInteger(trim(row.`ctrlid`))
  SET n.`label` = row.`label`
  SET n.`content` = row.`content`
} IN TRANSACTIONS OF 10000 ROWS;

LOAD CSV WITH HEADERS FROM ($file_path_root + $file_2) AS row
WITH row
WHERE NOT row.`chunk_id` IN $idsToSkip AND NOT toInteger(trim(row.`chunk_id`)) IS NULL
CALL {
  WITH row
  MERGE (n: `hipaaimpl` { `chunk_id`: toInteger(trim(row.`chunk_id`)) })
  SET n.`chunk_id` = toInteger(trim(row.`chunk_id`))
  SET n.`label` = row.`label`
  SET n.`chunk` = row.`chunk`
  SET n.`chunk_n` = toInteger(trim(row.`chunk_n`))
} IN TRANSACTIONS OF 10000 ROWS;


// RELATIONSHIP load
// -----------------
//
// Load relationships in batches, one relationship type at a time. Relationships are created using a MERGE statement, meaning only one relationship of a given type will ever be created between a pair of nodes.
LOAD CSV WITH HEADERS FROM ($file_path_root + $file_3) AS row
WITH row 
CALL {
  WITH row
  MATCH (source: `standard` { `std_id`: toInteger(trim(row.`from_id`)) })
  MATCH (target: `control` { `ctrlid`: toInteger(trim(row.`to_id`)) })
  MERGE (source)-[r: `stdcontrol`]->(target)
  SET r.`from_id` = toInteger(trim(row.`from_id`))
  SET r.`to_id` = toInteger(trim(row.`to_id`))
} IN TRANSACTIONS OF 10000 ROWS;

LOAD CSV WITH HEADERS FROM ($file_path_root + $file_4) AS row
WITH row 
CALL {
  WITH row
  MATCH (source: `control` { `ctrlid`: toInteger(trim(row.`from_id`)) })
  MATCH (target: `control` { `ctrlid`: toInteger(trim(row.`to_id`)) })
  MERGE (source)-[r: `controlmap`]->(target)
  SET r.`from_id` = toInteger(trim(row.`from_id`))
  SET r.`to_id` = toInteger(trim(row.`to_id`))
  SET r.`set_type` = row.`set_type`
  SET r.`concept_type` = toInteger(trim(row.`concept_type`))
  SET r.`ref` = row.`ref`
  SET r.`hipaa` = toLower(trim(row.`hipaa`)) IN ['1','true','yes']
} IN TRANSACTIONS OF 10000 ROWS;

LOAD CSV WITH HEADERS FROM ($file_path_root + $file_5) AS row
WITH row 
CALL {
  WITH row
  MATCH (source: `control` { `ctrlid`: toInteger(trim(row.`from_id`)) })
  MATCH (target: `hipaaimpl` { `chunk_id`: toInteger(trim(row.`to_id`)) })
  MERGE (source)-[r: `controlimpl`]->(target)
  SET r.`from_id` = toInteger(trim(row.`from_id`))
  SET r.`to_id` = toInteger(trim(row.`to_id`))
} IN TRANSACTIONS OF 10000 ROWS;
