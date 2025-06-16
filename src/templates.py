from langchain.prompts import PromptTemplate


system_instructions = """
You are a Cybersecurity SME tasked with compiling mappings between domains, controls and sub controls
across a variety of Cybersecurity and Privacy standards.
Your core expertise centers around the mapping of NIST's CSF 2.0 controls to
Health Insurance Portability and Accountability Act (HIPAA) Security Rule: 45 CFR Part 164.

When provided with a user question that contains a domain or sub control identifier or label.
extract the relevant, mapping provisions. 
For instance, the required information that needs to be extracted for the user provided 
CSF 2.0 subcontrol (e.g., Focal Document Element: GV.OC-01), is:
- Reference Document Element: Specific HIPAA Security Rule section/subsection labels e.g., 164.308(a)(1)(ii)(A)
- Strength of relationship: Estimated strength or confidence in the mapping relationship between the sub-controls and sections
- Rationale: A brief rationale behind the mapping, such as conceptual relevance, reference to prior mappings.

In providing your response,

1 - First and foremost, note that the 'Structured Response Example' below is provided ONLY to
demonstrate the expected format. Do not limit your response to this example, and 
find AS MANY realistic mappings as possible.
2 - In the process, consider material published by NIST/OLIR, or any other security standards capturing:
- Available mappings for NIST CSF 1.1 to the HIPAA Security Rule provisions.
- Available mappings from the prior version: NIST CSF 1.1 to CSF 2.0 controls and subcontrols.
3 - Ensure the output follows the instructions for the structured response.
4 - Do not include any additional explanation or context outside of the response.

"""

structured_example = """
Focal_Document_Element,Reference_Document_Element,Strength_of_relationship,Rationale
"GV.OC-01","164.308(a)(1)(ii)(A)",0.85,"Crosswalk-CSF 1.1 to HIPAA Security Rule"
"""


prompt_base = system_instructions + """
Structured Response Example:

```""" + structured_example + """
```

User Question: {question}

Context: {summaries}
"""

prompt_template_hipaa = PromptTemplate(
    template=prompt_base,
    input_variables=["question"]

)

prompt_chat = system_instructions + """
Structured Response Example:

```""" + structured_example + """
```

"""

prompt_template_hipaa_complex = PromptTemplate(
    input_variables=["summaries", "question"],
    template=(
        "System Instructions:\n"
        "{system_instructions}\n\n"
        "Structured Response Example:\n"
        "{structured_example}\n\n"
        "User question: {question}"
    ),
    partial_variables={
        "system_instructions": system_instructions,
        "structured_example": structured_example
    }
)


demo_question_hipaa = "What are the HIPAA Security Rule sections that map to CSF 2.0's GV.OC-01?"
demo_control_hipaa = "GV.OC-01"
rag_query_hipaa = """
MATCH (c2:control {label: $csf2ctrl})<-[r1:controlmap]->(ci:control)-[r2:controlmap]->(ch:control)
WHERE c2.ctrlid > 3000 and c2.ctrlid < 4000 AND ch.ctrlid > 4000 and ch.ctrlid < 5000
Return c2.label as csf2, ch.label as hipaa,
0.7 + (count(distinct ci.ctrlid)*0.05) + ((size(split(ch.label, "("))-1)*0.025) as strength
order by c2.label, ch.label
"""
ground_rag_colmap = {
                "csf2": "Focal_Document_Element",
                "hipaa": "Reference_Document_Element",
                "strength": "Strength_of_relationship"}


plain_example = '''{
    "Focal DocumentElement": "GV.OC-01",
    "Reference Document Element": [
        {
            "164.308(a)(1)(ii)(A)": {
                "Strength of relationship": 0.99,
                "Rationale": "Crosswalk from NIST CSF 1.1 to HIPAA Security Rule",
            }
        },
        {
            "164.308(a)(4)(ii)(B)": {
                "Strength of relationship": 0.99,
                "Rationale": "Crosswalk from NIST CSF 1.1 to HIPAA Security Rule",
            }
        },
        {
            "164.308(a)(4)(ii)(C)": {
                "Strength of relationship": 0.99,
                "Rationale": "Crosswalk from NIST CSF 1.1 to HIPAA Security Rule",
            }
        },
        {
            "164.308(a)(7)(ii)(B)": {
                "Strength of relationship": 0.99,
                "Rationale": "Crosswalk from NIST CSF 1.1 to HIPAA Security Rule",
            }
        },
        {
            "164.308(a)(7)(ii)(C)": {
                "Strength of relationship": 0.99,
                "Rationale": "Crosswalk from NIST CSF 1.1 to HIPAA Security Rule",
            }
        },
        {
            "164.308(a)(7)(ii)(D)": {
                "Strength of relationship": 0.99,
                "Rationale": "Crosswalk from NIST CSF 1.1 to HIPAA Security Rule",
            }
        },
        {
            "164.308(a)(7)(ii)(E)": {
                "Strength of relationship": 0.99,
                "Rationale": "Crosswalk from NIST CSF 1.1 to HIPAA Security Rule",
            }
        },
        {
            "164.308(a)(8)": {
                "Strength of relationship": 0.99,
                "Rationale": "Crosswalk from NIST CSF 1.1 to HIPAA Security Rule",
            }
        },
        {
            "164.310(a)(2)(i)": {
                "Strength of relationship": 0.99,
                "Rationale": "Crosswalk from NIST CSF 1.1 to HIPAA Security Rule",
            }
        },
        {
            "164.314(a)": {
                "Strength of relationship": 0.99,
                "Rationale": "Crosswalk from NIST CSF 1.1 to HIPAA Security Rule",
            }
        },
        {
            "164.314(a)(2)(i)": {
                "Strength of relationship": 0.99,
                "Rationale": "Crosswalk from NIST CSF 1.1 to HIPAA Security Rule",
            }
        },
        {
            "164.314(a)(2)(ii)": {
                "Strength of relationship": 0.99,
                "Rationale": "Crosswalk from NIST CSF 1.1 to HIPAA Security Rule",
            }
        },
        {
            "164.314(a)(2)(iii)": {
                "Strength of relationship": 0.99,
                "Rationale": "Crosswalk from NIST CSF 1.1 to HIPAA Security Rule",
            }
        },
        {
            "164.314(b)(2)(i)": {
                "Strength of relationship": 0.99,
                "Rationale": "Crosswalk from NIST CSF 1.1 to HIPAA Security Rule",
            }
        },
        {
            "164.314(b)(2)(ii)": {
                "Strength of relationship": 0.99,
                "Rationale": "Crosswalk from NIST CSF 1.1 to HIPAA Security Rule",
            }
        },
        {
            "164.314(b)(2)(iii)": {
                "Strength of relationship": 0.99,
                "Rationale": "Crosswalk from NIST CSF 1.1 to HIPAA Security Rule",
            }
        },
        {
            "164.314(b)(2)(iv)": {
                "Strength of relationship": 0.99,
                "Rationale": "Crosswalk from NIST CSF 1.1 to HIPAA Security Rule",
            }
        },
        {
            "164.316(a)": {
                "Strength of relationship": 0.99,
                "Rationale": "Crosswalk from NIST CSF 1.1 to HIPAA Security Rule",
            }
        },
        {
            "164.316(b)(2)(i)": {
                "Strength of relationship": 0.99,
                "Rationale": "Crosswalk from NIST CSF 1.1 to HIPAA Security Rule",
            }
        },
        {
            "164.316(b)(2)(ii)": {
                "Strength of relationship": 0.99,
                "Rationale": "Crosswalk from NIST CSF 1.1 to HIPAA Security Rule",
            }
        },
        {
            "164.316(b)(2)(iii)": {
                "Strength of relationship": 0.99,
                "Rationale": "Crosswalk from NIST CSF 1.1 to HIPAA Security Rule",
            }
        },
    ],
    "References": []
}'''
