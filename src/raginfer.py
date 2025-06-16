"""This module contains a demo class for graph inference & RAG functionalities leveraging LanguageChain"""

import os
from src.gdbi import NEO4JConnector
import src.templates as templates

from langchain_neo4j import Neo4jGraph
from langchain_community.vectorstores import Neo4jVector
from langchain_openai import OpenAIEmbeddings
from langchain.chains import RetrievalQAWithSourcesChain
from langchain_openai import ChatOpenAI


# from langchain import hub
# from langchain.prompts.prompt import PromptTemplate
# from langchain.chains.combine_documents import create_stuff_documents_chain
# from langchain.chains.retrieval import create_retrieval_chain
# import textwrap


class GraphInference:
    """Graph Inference class"""

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

    def debug(self):
        """Debug method to print connection details"""
        self.neo4jconnector.verify_connectivity()
        print(f"Graph schema: {self.neo4jgraph.schema}")

    def infer_chat(self, question=None):
        """Generate mapping with LLM without retrieval augmentation"""
        if question is None or len(question) == 0 or question == "":
            """Default question for plain inference"""
            question = templates.demo_question_hipaa
        print(question)

        # Create a chatbot Question & Answer chain from the retriever
        llm = ChatOpenAI(
            model="gpt-4o", temperature=0, max_tokens=None, timeout=None, api_key=self.OPENAI_API_KEY, max_retries=2
        )

        # Alternatively we can use a vanilla prompt template with the LLM directly
        messages = [
            ("system", templates.prompt_chat),
            ("human", templates.demo_question_hipaa),
        ]

        results = llm.invoke(messages)
        return results.content

    def infer_plain(self, question=None):
        """Generate LLM mappings leveraging GraphRAG vectors and embeddings (semantic search)"""
        if question is None or len(question) == 0 or question == "":
            """Default question for plain inference"""
            question = templates.demo_question_hipaa
        print(question)

        """Infer with question no augmentation for LLM"""
        vector_store = Neo4jVector.from_existing_graph(
            embedding=OpenAIEmbeddings(api_key=self.OPENAI_API_KEY),
            url=self.neo4jconnector.getUri(),
            username=self.neo4jconnector.getAuthUser(),
            password=self.neo4jconnector.getAuthPassword(),
            index_name="chunkContent",
            node_label="hipaaimpl",
            text_node_properties=["chunk", "label"],
            embedding_node_property="contentEmbeddingOpenAI",
            # search_type="hybrid",  # Use hybrid search for better results
        )

        # print(vector_store.node_label)
        # print(vector_store.embedding_node_property)

        # Create a retriever from the store
        # Using a k of default for the retriever
        # retriever = vector_store.as_retriever(search_kwargs={"k": 200})
        retriever = vector_store.as_retriever(search_type="mmr")

        # retriever = vector_store.as_retriever(search_type="similarity_score_threshold",
        #                                       search_kwargs={"score_threshold": 0.5})

        # Create a chatbot Question & Answer chain from the retriever
        llm = ChatOpenAI(
            model="gpt-4o", temperature=0, max_tokens=None, timeout=None, api_key=self.OPENAI_API_KEY, max_retries=2
        )

        plain_chain = RetrievalQAWithSourcesChain.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever,
            chain_type_kwargs={"prompt": templates.prompt_template_hipaa},
        )

        results = plain_chain.invoke({"question": question})
        return results["answer"]

    def infer_rag(self, question, only_outputs=False):
        """Generate LLM mappings leveraging GraphRAG vectors and context from existing mappings
           for augmented retrieval (semantic + episodic search)"""
        if question is None or len(question) == 0 or question == "":
            """Default question for plain inference"""
            question = templates.demo_question_hipaa
        print(question)

        retrieval_query = """
        MATCH (node)<-[:controlimpl]-(c1:control)<-[:controlmap]-(c2:control)<-[:stdcontrol]-(s:standard)
        WITH node, c1, c2, s
        WITH collect (
            'HIPAA implementation for Security Rule: ' + c1.label +
            ' is referenced by security standard ' + s.label + ' control: ' + c2.label +
            ' capturing: ' +  c2.content + ' in the context of ' + c1.content 
        ) AS hipaa_mapping_context, c1, node
        WHERE hipaa_mapping_context IS NOT NULL AND hipaa_mapping_context <> []
        RETURN apoc.text.join(hipaa_mapping_context, "\n") AS text, 0.9 as score,
            node {.*, vector: Null, info: Null, source: c1.label} AS metadata
        """

        vector_store = Neo4jVector.from_existing_index(
            embedding=OpenAIEmbeddings(api_key=self.OPENAI_API_KEY),
            url=self.neo4jconnector.getUri(),
            username=self.neo4jconnector.getAuthUser(),
            password=self.neo4jconnector.getAuthPassword(),
            database="neo4j",
            index_name="chunkContent",
            node_label="hipaaimpl",
            retrieval_query=retrieval_query,
        )

        # Create a retriever from the vector store
        # retriever = vector_store_with_question_rationale.as_retriever(search_kwargs={'k': 9})
        retriever = vector_store.as_retriever(search_type="mmr")

        # retriever = vector_store.as_retriever(search_type="similarity_score_threshold",
        #                                       search_kwargs={"score_threshold": 0.5})

        # Create a chatbot Question & Answer chain from the retriever
        llm = ChatOpenAI(
            model="gpt-4o", temperature=0, max_tokens=None, timeout=None, api_key=self.OPENAI_API_KEY, max_retries=2
        )

        plain_chain = RetrievalQAWithSourcesChain.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever,
            chain_type_kwargs={"prompt": templates.prompt_template_hipaa},
        )

        results = None
        if only_outputs:
            results = plain_chain.invoke({"question": question}, return_only_outputs=True)
        else:
            results = plain_chain.invoke({"question": question})

        return results["answer"]
