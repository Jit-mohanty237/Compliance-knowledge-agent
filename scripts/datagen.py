
import json
import time
import os
from typing import List

from google import genai
from pydantic import BaseModel, Field, ValidationError
from dotenv import load_dotenv

load_dotenv()

# ==========================================================
# GEMINI CLIENT
# ==========================================================


client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

# ==========================================================
# LATAM COUNTRIES
# ==========================================================

LATAM_COUNTRIES = [
    "Argentina",
    "Bolivia",
    "Brazil",
    "Chile",
    "Colombia",
    "Costa Rica",
    "Dominican Republic",
    "Ecuador",
    "El Salvador",
    "Guatemala",
    "Honduras",
    "Mexico",
    "Nicaragua",
    "Panama",
    "Paraguay",
    "Peru",
    "Uruguay",
    "Venezuela"
]


# ==========================================================
# COMPLIANCE CATEGORIES
# ==========================================================

COMPLIANCE_TYPES = [
    "Labor Laws",
    "Employment Contracts",
    "Working Hours & Overtime",
    "Payroll & Social Security",
    "Taxation",
    "Leave & Benefits",
    "Hiring Compliance",
    "Contractor Classification",
    "Termination & Severance",
    "Documentation Required",
    "Compliance Risks",
    "Collective Bargaining",
    "Union Regulations",
    "Remote Work Compliance",
    "Data Privacy Compliance",
    "Health & Safety Compliance",
    "Immigration & Work Permit Compliance",
    "Anti-Discrimination Laws",
    "Mandatory Employee Benefits",
    "Payroll Reporting",
    "Employee Registration Requirements"
]


# ==========================================================
# PYDANTIC SCHEMA
# ==========================================================

class ComplianceLaw(BaseModel):

    law_name: str = Field(
        description="Official law name"
    )

    law_code: str = Field(
        default="",
        description="Labor code or law number"
    )

    article_number: str = Field(
        description="Article number"
    )

    category: str = Field(
        description="Compliance category"
    )

    law_type: str = Field(
        default="",
        description="Labor Code, Tax Law, Social Security Law, Constitutional Law, etc."
    )

    definition: str = Field(
        description="Detailed definition"
    )

    compliance_requirements: List[str] = Field(
        default_factory=list,
        description="Employer obligations and compliance requirements"
    )

    documentation_required: List[str] = Field(
        default_factory=list,
        description="Documents required for compliance"
    )

    compliance_risk: str = Field(
        description="Risk if employer violates law"
    )

    penalty: str = Field(
        description="Penalty for non-compliance"
    )

    keywords: List[str] = Field(
        description="Search keywords"
    )

    source_reference: str = Field(
        description="Official source"
    )

    effective_date: str = Field(
        default="",
        description="Effective date of the law if available"
    )


class ComplianceResponse(BaseModel):

    country: str

    compliance_type: str

    laws: List[ComplianceLaw]


# ==========================================================
# PROMPT BUILDER
# ==========================================================

def build_prompt(
    country: str,
    compliance_type: str
):

    return f"""
You are a LATAM Employment Compliance Expert.

Country:
{country}

Compliance Category:
{compliance_type}

Requirements:

1. Return ALL applicable laws.
2. Include labor code names.
3. Include article numbers.
4. Include legal definitions.
5. Include compliance risks.
6. Include penalties.
7. Include keywords.
8. Include official source references.
9. Include documentation required.
10. Include employer obligations.
11. Include compliance requirements.
12. Include effective date if available.
13. Return ONLY JSON.
14. Do not summarize.
15. Return every applicable law.
16. Include law_code.
17. Include law_type.
18. Include documentation_required.
19. Include compliance_requirements.
20. Include Labor Codes.
21. Include Tax Laws.
22. Include Social Security Laws.
23. Include Constitutional Labor Rights.
24. Include Ministry of Labor Regulations.
25. Include Payroll Regulations.
26. Include Remote Work Regulations.
27. Include Union Rules.
28. Include Collective Bargaining Rules.
29. Include Data Privacy Laws affecting employees.

Examples:

Labor Laws,
Employment Contracts,
Working Hours & Overtime,
Payroll & Social Security,
Taxation,
Leave & Benefits,
Hiring Compliance,
Contractor Classification,
Termination & Severance,
Documentation Required,
Compliance Risks,
Collective Bargaining,
Union Regulations,
Remote Work Compliance,
Data Privacy Compliance,
Health & Safety Compliance,
Immigration & Work Permit Compliance,
Anti-Discrimination Laws,
Mandatory Employee Benefits,
Payroll Reporting,
Employee Registration Requirements

Return every relevant law available for this category.
"""


# ==========================================================
# GEMINI CALL
# ==========================================================
def clean_json(text: str):

    text = text.strip()

    if text.startswith("```json"):
        text = text.replace("```json", "")

    if text.startswith("```"):
        text = text.replace("```", "")

    if text.endswith("```"):
        text = text[:-3]

    return text.strip()


def fetch_compliance(
    country: str,
    compliance_type: str,
    retries: int = 3
):

    prompt = build_prompt(
        country,
        compliance_type
    )

    for attempt in range(retries):

        try:

            response = client.models.generate_content(
                model="gemini-3.1-flash-lite",
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_json_schema":
                        ComplianceResponse.model_json_schema()
                }
            )

            parsed_json = json.loads(
                clean_json(response.text)
            )

            validated = (
                ComplianceResponse.model_validate(
                    parsed_json
                )
            )

            time.sleep(2)
            return validated

        except (
            ValidationError,
            json.JSONDecodeError,
            Exception
        ) as e:

            print(
                f"Retry {attempt+1} failed:"
            )

            print(e)

            time.sleep(2)

    return None


# ==========================================================
# MERGE ALL LAWS
# ==========================================================

def merge_all_laws(
    responses: List[ComplianceResponse]
):

    merged = []

    for response in responses:

        for law in response.laws:

            merged.append(
                {
                    "country":
                        response.country,

                    "compliance_type":
                        response.compliance_type,

                    **law.model_dump()
                }
            )

    return merged


def deduplicate_laws(
    laws
):

    seen = set()

    unique = []

    for law in laws:

        key = (
            law["country"],
            law["law_name"],
            law["article_number"]
        )

        if key not in seen:

            seen.add(key)

            unique.append(law)

    return unique


def merge_string_lists(
    responses
):

    merged = []

    for response in responses:

        for law in response.laws:

            merged.extend(
                law.keywords
            )

            merged.extend(
                law.compliance_requirements
            )

            merged.extend(
                law.documentation_required
            )

    return sorted(
        list(set(merged))
    )


# ==========================================================
# COLLECT ALL DATA
# ==========================================================

def collect_latam_compliance():

    all_results = []

    total_jobs = (
        len(LATAM_COUNTRIES)
        * len(COMPLIANCE_TYPES)
    )

    current_job = 0

    for country in LATAM_COUNTRIES:

        print(
            f"\nProcessing Country: {country}"
        )

        for compliance_type in COMPLIANCE_TYPES:

            current_job += 1

            print(
                f"[{current_job}/{total_jobs}] "
                f"{compliance_type}"
            )

            result = fetch_compliance(
                country,
                compliance_type
            )

            if result and result.laws:

                all_results.append(result)

                with open(
                    "checkpoint.json",
                    "w",
                    encoding="utf-8"
                ) as f:

                    json.dump(
                        [r.model_dump() for r in all_results],
                        f,
                        indent=4,
                        ensure_ascii=False
                    )

                    print(
                        f"✓ Success"
                    )

            else:

                print(
                    f"✗ Failed"
                )

    return all_results


# ==========================================================
# SAVE FILES
# ==========================================================

def save_results(
    responses: List[ComplianceResponse]
):

    nested_output = [
        response.model_dump()
        for response in responses
    ]

    with open(
        "latam_compliance.json",
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            nested_output,
            f,
            indent=4,
            ensure_ascii=False
        )

    merged_laws = deduplicate_laws(
        merge_all_laws(responses)
    )

    with open(
        "latam_laws_flat.json",
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            merged_laws,
            f,
            indent=4,
            ensure_ascii=False
        )

    keywords = merge_string_lists(
        responses
    )

    with open(
        "latam_keywords.json",
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            keywords,
            f,
            indent=4,
            ensure_ascii=False
        )

    print(
        "\nSaved:"
    )

    print(
        "- latam_compliance.json"
    )

    print(
        "- latam_laws_flat.json"
    )

    print(
        "- latam_keywords.json"
    )

    print(
        f"Total Laws: {len(merged_laws)}"
    )


# ==========================================================
# MAIN
# ==========================================================

if __name__ == "__main__":

    responses = (
        collect_latam_compliance()
    )

    save_results(
        responses
    )
