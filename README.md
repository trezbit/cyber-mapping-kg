# CYBER-MAPPING-KG
Knowledge Graph POC implementation to illustrate SME Agentic workflow with RAG support.

## Demo Schema
> [!NOTE]
>
> **Node properties**:
> 
> standard {std_id: INTEGER, label: STRING, title: STRING, type: STRING}
>
> control {label: STRING, ctrlid: INTEGER, content: STRING, contentEmbeddingOpenAI: LIST}
>
> hipaaimpl {label: STRING, chunk_id: INTEGER, chunk: STRING, chunk_n: INTEGER, contentEmbeddingOpenAI: LIST}
>
> **Relationship properties**:
>
> stdcontrol {from_id: INTEGER, to_id: INTEGER}
>
> controlmap {from_id: INTEGER, to_id: INTEGER, concept_type: INTEGER, ref: STRING, hipaa: BOOLEAN, set_type: STRING}
>
> controlimpl {from_id: INTEGER, to_id: INTEGER}
>
> **The relationships**:
>
> (:standard)-[:stdcontrol]->(:control)
>
> (:control)-[:controlmap]->(:control)
>
> (:control)-[:controlimpl]->(:hipaaimpl)
> 
