import pandas as pd
from langchain_neo4j import Neo4jGraph
from src.gdbi import NEO4JConnector
from src.raginfer import GraphInference
import src.templates as templates
from io import StringIO
# Baseline custom agent for RAG workflow
# Can be implemented via LangGraph Tasks/Tools/EntryPoint or Google ADK

# from langgraph.func import entrypoint, task
# from langchain.agents import initialize_agent
# from langchain.agents import Tool
# from langchain.memory import ConversationBufferMemory
# from langchain_core.messages import ToolMessage
# from langgraph.prebuilt import create_react_agent


class GraphRAGAgent:
    """Graph RAG agent manager  class"""

    def __init__(self):
        """Initialize RAG inference class"""
        self.neo4jconnector = NEO4JConnector()
        """Initialize the Neo4j graph via LangChain"""
        self.neo4jgraph = Neo4jGraph(
            url=self.neo4jconnector.getUri(),
            username=self.neo4jconnector.getAuthUser(),
            password=self.neo4jconnector.getAuthPassword(),
        )
        self.inferer = GraphInference()

    def generate_map(self, query: str):
        """Use the Neo4j Graph to run a RAG Query."""
        self.ctrlquery = query
        result = self.inferer.infer_rag(query, only_outputs=True)
        return result

    def finetune_df(self, dfopen, dfrag) -> pd.DataFrame:
        """Finetune the DataFrame by merging two DataFrames."""
        # add new columns to the DataFrame
        # dfrag["strength"] = 0.7 + dfrag["strength"]*0.05 + dfrag["specific"]*0.025

        # Focal_Document_Element,Reference_Document_Element,Strength_of_relationship,Rationale
        dfrag = dfrag.rename(
            columns=templates.ground_rag_colmap
        )
        dfrag["Rationale"] = "Grounded from KB inference"

        # Merge the generated DataFrame with the grounded DataFrame by appending the generated DataFrame
        dfmerged = dfopen._append(dfrag)

        # Aggregate the DataFrame by Focal_Document_Element and Reference_Document_Element
        dfmerged = dfmerged.groupby(
            ['Focal_Document_Element', 'Reference_Document_Element'],
            as_index=False
        ).agg(
            Strength_of_relationship=('Strength_of_relationship', 'mean'),
            Rationale=('Rationale', lambda x: '; '.join(x))
        )

        # Add a new column indicating if both methods agree on the relationship
        dfmerged['Agreement'] = dfmerged.apply(
            lambda row: 'Yes' if len(row['Rationale'].split(";")) > 1 else 'No', axis=1
        )
        return dfmerged

    def ground_map(self, strout: str, msg=None) -> pd.DataFrame:
        """Ground genai query results to the Neo4j Graph."""

        if msg is None or len(msg) == 0 or msg == "":
            """Default question for grounding"""
            msg = templates.demo_control_hipaa
        # Read the strout csv string output into a DataFrame
        strout = strout.strip("```\n")

        dfgen = pd.read_csv(StringIO(strout))
        if dfgen.empty:
            raise ValueError("The DataFrame is empty. No data to ground.")

        resdf = self.neo4jconnector.run_df_query(
            templates.rag_query_hipaa,
            params={"csf2ctrl": msg},
        )

        if type(resdf) is not pd.DataFrame:
            raise ValueError("Expected a DataFrame from the Neo4j query.")
        dfmerged = self.finetune_df(dfgen, resdf)
        return dfmerged

    def invoke(self, msg=None):
        """Run the RAG agent with a query."""
        # Demo reasoning chain
        # 1 - Generate the mapping using RAG augmented LLM session
        genmap = self.generate_map(msg)
        # 2 - Ground the generated mapping to the Neo4j Graph
        groundmap = self.ground_map(genmap, msg)
        # 3 - Combine the results
        response = {
            "generated_map": genmap,
            "grounded_map": groundmap
        }
        # Return the response
        return response
