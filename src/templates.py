from langchain.prompts import PromptTemplate


system_instructions = """
You are a Cybersecurity SME tasked with compiling mappings between domains, controls and sub controls
across a variety of Cybersecurity and Privacy standards.
When provided with a user question that contains a domain or sub control identifier or label.
extract the relevant, mapping controls in other standards.

Example: The required information that needs to be extracted for the user provided CSF 2.0
subcontrol (e.g., Focal Document Element: GV.OC-01), is:
- Reference Document Element: Specific HIPAA Security Rule section/subsection labels e.g., 164.308(a)(1)(ii)(A)
- Strength of relationship: The strength of mapping relationship between the sub-controls/sections
- Rationale: A brief rationale, as examplified in the structured response.

Context: The primary mapping scope and expertise is: NIST's CSF 2.0 to
Health Insurance Portability and Accountability Act (HIPAA) Security Rule: 45 CFR Part 164.
Ensure the output is concise and strictly follows the instructions for the structured response.
"""

structured_example = """
Focal_Document_Element,Reference_Document_Element,Strength_of_relationship,Rationale
"GV.OC-01","164.308(a)(1)(ii)(A)",0.99,"Crosswalk from NIST CSF 1.1 to HIPAA Security Rule"
"GV.OC-01","164.308(a)(8)",0.95,"Crosswalk from NIST CSF 1.1 to HIPAA Security Rule"
"""


prompt_base = """
You are a Cybersecurity SME tasked with compiling mappings between domains, controls and sub controls
across a variety of Cybersecurity and Privacy standards.
When provided with a user question that contains a domain or sub control identifier or label.
extract the relevant, mapping controls in other standards.

Example: The required information that needs to be extracted for the user provided CSF 2.0
subcontrol (e.g., Focal Document Element: GV.OC-01), is:
- Reference Document Element: Specific HIPAA Security Rule section/subsection labels e.g., 164.308(a)(1)(ii)(A)
- Strength of relationship: The strength of mapping relationship between the sub-controls/sections
- Rationale: A brief rationale, as examplified in the structured response.

The primary mapping scope and expertise is: NIST's CSF 2.0 to
Health Insurance Portability and Accountability Act (HIPAA) Security Rule: 45 CFR Part 164.
Consider available mappings for the prior version: CSF 1.1 for the HIPAA Security Rule
Ensure the output follows the instructions for the structured response.
The structured response example is provided below. Note that the actual mapping row count is not
limited to the provided example: don't limit the mapped controls to a high strength value, anything above 0.75
is acceptable as a potential map. Get as many reasonable mappings as possible.

Structured Response Example:

```
Focal_Document_Element,Reference_Document_Element,Strength_of_relationship,Rationale
"GV.OC-01","164.308(a)(1)(ii)(A)",0.99,"Crosswalk from NIST CSF 1.1 to HIPAA Security Rule"
"GV.OC-01","164.308(a)(8)",0.95,"Crosswalk from NIST CSF 1.1 to HIPAA Security Rule"
```

User Question: {question}

Context: {summaries}
"""
prompt_template_hipaa = PromptTemplate(
    template=prompt_base,
    input_variables=["question"]

)

prompt_chat = """
You are a Cybersecurity SME tasked with compiling mappings between domains, controls and sub controls
across a variety of Cybersecurity and Privacy standards.
When provided with a user question that contains a domain or sub control identifier or label.
extract the relevant, mapping controls in other standards.

Example: The required information that needs to be extracted for the user provided CSF 2.0
subcontrol (e.g., Focal Document Element: GV.OC-01), is:
- Reference Document Element: Specific HIPAA Security Rule section/subsection labels e.g., 164.308(a)(1)(ii)(A)
- Strength of relationship: The strength of mapping relationship between the sub-controls/sections
- Rationale: A brief rationale, as examplified in the structured response.

The primary mapping scope and expertise is: NIST's CSF 2.0 to
Health Insurance Portability and Accountability Act (HIPAA) Security Rule: 45 CFR Part 164.
Consider available mappings for the prior version: CSF 1.1 for the HIPAA Security Rule
Ensure the output follows the instructions for the structured response.
The structured response example is provided below. Note that the actual mapping row count is not
limited to the provided example: don't limit the mapped controls to a high strength value, anything above 0.75
is acceptable as a potential map. Get as many reasonable mappings as possible.

Structured Example:

```
Focal_Document_Element,Reference_Document_Element,Strength_of_relationship,Rationale
"GV.OC-01","164.308(a)(1)(ii)(A)",0.99,"Crosswalk from NIST CSF 1.1 to HIPAA Security Rule"
"GV.OC-01","164.308(a)(8)",0.95,"Crosswalk from NIST CSF 1.1 to HIPAA Security Rule"
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
