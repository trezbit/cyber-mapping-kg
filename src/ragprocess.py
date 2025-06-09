from src.gdbi import NEO4JConnector
import src.includes as inc
import os
from os import path
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.graphs import Neo4jGraph
import pandas as pd
import json


# Chunk Processing Queries
CHUNK_NODE_MERGE_QUERY = """
    MERGE (h:hipaaimpl {label: $chunkLabel, chunk: $chunkContent, chunk_n: $chunkNum, chunk_id: $chunkId})
    """
CHUNK_NODE_UPDATE_QUERY = """
    MATCH (h:hipaaimpl {chunk_id: $chunkId})
    SET h.chunk = $chunkContent
    """
CHUNK_CREATE_ADD_REL_QUERY = """
    MATCH (c:control)
    MATCH (h:hipaaimpl)
    WHERE c.ctrlid in $ctrlIds and h.chunk_id= $chunkId
    MERGE (c)-[:controlimpl]->(h)
    """
CONTROL_VECTOR_INDEXING_QUERY = """
    CREATE VECTOR INDEX `controlContent` IF NOT EXISTS
    FOR (c:control) ON (c.content)
    OPTIONS { indexConfig: {
    `vector.dimensions`: 1536,
    `vector.similarity_function`: 'cosine'
    }}
"""
CONTROL_VECTOR_EMBEDDING_QUERY_CIS8 = """
    MATCH (c:control) WHERE c.contentEmbeddingOpenAI IS NULL and  c.ctrlid < 2000
    WITH c, genai.vector.encode(
      c.content,
      "OpenAI",
      {
        token: $openAiApiKey,
        endpoint: $openAiEndpoint
      }) AS vector
    CALL db.create.setNodeVectorProperty(c, 'contentEmbeddingOpenAI', vector)
    """
CONTROL_VECTOR_EMBEDDING_QUERY_CSF11 = """
    MATCH (c:control) WHERE c.contentEmbeddingOpenAI IS NULL and  c.ctrlid > 2000  and c.ctrlid < 3000
    WITH c, genai.vector.encode(
      c.content,
      "OpenAI",
      {
        token: $openAiApiKey,
        endpoint: $openAiEndpoint
      }) AS vector
    CALL db.create.setNodeVectorProperty(c, 'contentEmbeddingOpenAI', vector)
    """
CONTROL_VECTOR_EMBEDDING_QUERY_CSF2 = """
    MATCH (c:control) WHERE c.contentEmbeddingOpenAI IS NULL and  c.ctrlid > 3000  and c.ctrlid < 4000
    WITH c, genai.vector.encode(
      c.content,
      "OpenAI",
      {
        token: $openAiApiKey,
        endpoint: $openAiEndpoint
      }) AS vector
    CALL db.create.setNodeVectorProperty(c, 'contentEmbeddingOpenAI', vector)
    """
CONTROL_VECTOR_EMBEDDING_QUERY_CSF2 = """
    MATCH (c:control) WHERE c.contentEmbeddingOpenAI IS NULL and  c.ctrlid > 3000  and c.ctrlid < 4000
    WITH c, genai.vector.encode(
      c.content,
      "OpenAI",
      {
        token: $openAiApiKey,
        endpoint: $openAiEndpoint
      }) AS vector
    CALL db.create.setNodeVectorProperty(c, 'contentEmbeddingOpenAI', vector)
    """
CONTROL_VECTOR_EMBEDDING_QUERY_HIPAA = """
    MATCH (c:control) WHERE c.contentEmbeddingOpenAI IS NULL and  c.ctrlid > 4000  and c.ctrlid < 5000
    WITH c, genai.vector.encode(
      c.content,
      "OpenAI",
      {
        token: $openAiApiKey,
        endpoint: $openAiEndpoint
      }) AS vector
    CALL db.create.setNodeVectorProperty(c, 'contentEmbeddingOpenAI', vector)
    """
CONTROL_VECTOR_EMBEDDING_QUERY_SCF = """
    MATCH (c:control) WHERE c.contentEmbeddingOpenAI IS NULL and  c.ctrlid > 5000
    WITH c, genai.vector.encode(
      c.content,
      "OpenAI",
      {
        token: $openAiApiKey,
        endpoint: $openAiEndpoint
      }) AS vector
    CALL db.create.setNodeVectorProperty(c, 'contentEmbeddingOpenAI', vector)
    """
CHUNK_VECTOR_INDEXING_QUERY = """
    CREATE VECTOR INDEX `chunkContent` IF NOT EXISTS
    FOR (h:hipaaimpl) ON (h.chunk)
    OPTIONS { indexConfig: {
    `vector.dimensions`: 1536,
    `vector.similarity_function`: 'cosine'
    }}
"""
CHUNK_VECTOR_EMBEDDING_QUERY = """
    MATCH (h:hipaaimpl) WHERE h.chunkEmbeddingOpenAI IS NULL
    WITH h, genai.vector.encode(
      h.chunk,
      "OpenAI",
      {
        token: $openAiApiKey,
        endpoint: $openAiEndpoint
      }) AS vector
    CALL db.create.setNodeVectorProperty(h, 'contentEmbeddingOpenAI', vector)
    """


class GraphRAGProcessor:
    """Graph RAG preprocessing class"""

    def __init__(self):
        """Initialize RAG inference class"""
        self.neo4jconnector = NEO4JConnector()
        """Initialize the Neo4j graph via LangChain"""
        self.neo4jgraph = Neo4jGraph(
            url=self.neo4jconnector.getUri(),
            username=self.neo4jconnector.getAuthUser(),
            password=self.neo4jconnector.getAuthPassword(),
        )
        self.OPENAI_API_KEY = os.environ.get("OPEN_API_SECRET")
        self.OPENAI_ENDPOINT = os.getenv("OPENAI_BASE_URL") + "/embeddings"
        self.content_embed_queries = [CONTROL_VECTOR_EMBEDDING_QUERY_SCF,
                                      CONTROL_VECTOR_EMBEDDING_QUERY_CIS8,
                                      CONTROL_VECTOR_EMBEDDING_QUERY_CSF11,
                                      CONTROL_VECTOR_EMBEDDING_QUERY_CSF2,
                                      CONTROL_VECTOR_EMBEDDING_QUERY_HIPAA]

    def prep(self, init=False):
        """Initialize the graph for rag flows"""
        # Preliminary upload of chunks from original base hipaa implementation nodes
        # This is a one-time operation to load the HIPAA implementation chunks into the graph database
        # Create the vector index for the control and chunk nodes

        # Control node content indexing and embedding
        self.neo4jgraph.query(CONTROL_VECTOR_INDEXING_QUERY)

        # We are running multiple queries for different control sets to avoid large query size and timeout issues
        for query in self.content_embed_queries:
            self.neo4jgraph.query(
                query,
                params={"openAiApiKey": self.OPENAI_API_KEY, "openAiEndpoint": self.OPENAI_ENDPOINT},
            )

        # Process HIPAA implementation chunks
        # This is a one-time operation to load the HIPAA implementation chunks into the graph database
        if init:
            print("Loading HIPAA implementation chunks into the graph database...")
            self.load_hipaa_impl_chunks()
        self.neo4jgraph.query(CHUNK_VECTOR_INDEXING_QUERY)
        self.neo4jgraph.query(
            CHUNK_VECTOR_EMBEDDING_QUERY,
            params={"openAiApiKey": self.OPENAI_API_KEY, "openAiEndpoint": self.OPENAI_ENDPOINT}
        )

        self.neo4jgraph.refresh_schema()
        print(self.neo4jgraph.schema)

    def load_hipaa_impl_chunks(self):
        """Load HIPAA implementation chunks into the graph database"""
        chunks = self.preprocess_chunks()
        # write the chunks to a JSON file
        with open(path.join(inc.SCHEMA_BASE, "hipaa_impl_chunks.json"), "w") as f:
            json.dump(chunks, f, indent=4)

        for chunk_id, chunk_data in chunks.items():
            chunk_label = chunk_data["chunkLabel"]
            chunk_content = chunk_data["chunkContent"]
            chunk_num = chunk_data["chunkNum"]
            impl_nodes = chunk_data["implNodes"]

            if chunk_data["chunkOrig"] == 1:
                # if the chunk is original, update the content
                self.neo4jgraph.query(
                    CHUNK_NODE_UPDATE_QUERY,
                    params={
                        "chunkId": chunk_id,
                        "chunkContent": chunk_content,
                    },
                )
            else:
                # add the chunk to the graph database
                self.neo4jgraph.query(
                    CHUNK_NODE_MERGE_QUERY,
                    params={
                        "chunkLabel": chunk_label,
                        "chunkContent": chunk_content,
                        "chunkNum": chunk_num,
                        "chunkId": chunk_id,
                    },
                )
                # add the relationships to the chunk

                self.neo4jgraph.query(
                    CHUNK_CREATE_ADD_REL_QUERY,
                    params={
                        "chunkId": chunk_id,
                        "ctrlIds": impl_nodes,
                    },
                )
        return

    def preprocess_chunks(self):
        """Preprocess the RAG data"""
        chunks = dict()

        # list all markdown files in the HIPAA implementation directory
        # and process them to create chunks

        implchunks_df = pd.read_csv(path.join(inc.SCHEMA_BASE, "n_hipaa_impl.csv"))
        hippa_rels_df = pd.read_csv(path.join(inc.SCHEMA_BASE, "e_ctrl_hipaa_impl.csv"))

        for index, row in implchunks_df.iterrows():
            chunk_id = row["chunk_id"]
            chunk_label = row["label"]
            chunk_num = row["chunk_n"]
            chunk_orig = 1

            # retrieve distinct 'from_id' from relationships for the mapped chunk_id to_id
            # and add them to the chunk dictionary
            impl_nodes = hippa_rels_df[hippa_rels_df["to_id"] == chunk_id]["from_id"].unique().tolist()
            split_chunks = self.split_content_from_file(path.join(inc.HIPAAIMPL_CORPUS, chunk_label + ".md"))

            # ietrate over the split chunks and create a unique chunk ID with the index
            # and the chunk number

            for i, stext in enumerate(split_chunks):
                n_chunk_id = chunk_id
                # Create a unique chunk ID
                if i > 0:
                    n_chunk_id = chunk_id + (100 * index) + i
                    chunk_orig = 0
                    chunk_num = chunk_num + i

                chunks[n_chunk_id] = {
                    "chunkContent": stext,
                    "chunkLabel": chunk_label,
                    "chunkNum": chunk_num,
                    "chunkId": n_chunk_id,
                    "chunkOrig": chunk_orig,
                    "implNodes": impl_nodes,
                }

        return chunks

    # File/Text processing functions
    def split_content_from_file(self, file):
        """Load a markdown file, remove quotes, escape, and pipe characters."""
        with open(file, "r", encoding="utf-8") as f:
            text = f.read()
        # Remove all quotes, escape, and pipe characters
        utf8text = text.replace('"', "").replace("'", "").replace("\\", "").replace("|", "")
        """Split data from a file into chunks with metadata"""
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=2000,
            chunk_overlap=200,
            length_function=len,
            is_separator_regex=False,
        )
        text_chunks = splitter.split_text(utf8text)
        return text_chunks
