import json
import chromadb
from chromadb.utils import embedding_functions
from pathlib import Path
import pandas as pd

CHROMA_PATH = Path(__file__).resolve().parent / "chroma_db"

client = chromadb.PersistentClient(
    path=str(CHROMA_PATH)
)
COLLECTION_NAME = "latam_compliance"

embedding_fn = (
    embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )
)

collection = client.get_or_create_collection(
    name=COLLECTION_NAME,
    embedding_function=embedding_fn
)

print("\n=== CHROMA DEBUG ===")
print("Compliance Collection Name:", COLLECTION_NAME)
print("Collections Available:")
print(client.list_collections())
print("====================\n")


def build_document(record):
    """
    Format raw JSON compliance records into clean text layout.
    """
    return f"""
Country: {record.get('country', '')}

Compliance Type:
{record.get('compliance_type', '')}

Law Name:
{record.get('law_name', '')}

Article Number:
{record.get('article_number', '')}

Category:
{record.get('category', '')}

Definition:
{record.get('definition', '')}

Compliance Risk:
{record.get('compliance_risk', '')}

Penalty:
{record.get('penalty', '')}

Keywords:
{' '.join(record.get('keywords', []))}
"""


def ingest_json(json_file):
    """
    Ingest compliance JSON dataset into the latam_compliance collection.
    
    Why this exists:
        Maintains the original compliance ingestion pipeline, preserving existing 
        schemas, vector indexes, and matching behavior.
    """
    print(f"Reading JSON records from {json_file}...")
    with open(
        json_file,
        "r",
        encoding="utf-8"
    ) as f:
        records = json.load(f)

    ids = []
    documents = []
    metadatas = []

    for idx, record in enumerate(records):
        doc = build_document(record)
        ids.append(
            f"{record['country']}_{idx}"
        )
        documents.append(doc)
        metadatas.append({
            "country":
                record.get("country", ""),

            "compliance_type":
                record.get(
                    "compliance_type",
                    ""
                ),

            "law_name":
                record.get(
                    "law_name",
                    ""
                ),

            "article_number":
                str(
                    record.get(
                        "article_number",
                        ""
                    )
                )
        })

    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas
    )

    print(
        f"Inserted {len(ids)} records into {COLLECTION_NAME} collection."
    )


def ingest(json_file):
    """
    Wrapper around ingest_json for backward compatibility.
    """
    ingest_json(json_file)


def get_val(df, r, c):
    """
    Helper to retrieve value from a pandas DataFrame safely, converting NaN/NaT to None.
    """
    if r >= df.shape[0] or c >= df.shape[1]:
        return None
    val = df.iloc[r, c]
    if pd.isna(val):
        return None
    return val


def ingest_excel(eor_file, hr_file):
    """
    Ingest KOMP_EOR and HR Lifecycle spreadsheets into the new hr_playbook collection.
    
    Why this exists:
        Converts unstructured rows and grids of HR & EOR playbooks into clean, 
        searchable text documents stored in a separate database collection.
        
    How it works:
        Uses pandas to load workbooks. 
        - EOR Playbook: Iterates through country column pairs, mapping topic ranges.
        - HR Playbook: Tracks category sections and row items inside priority sheets.
    """
    hr_collection = client.get_or_create_collection(
        name="hr_playbook",
        embedding_function=embedding_fn
    )

    # Clear previous documents for fresh reload
    try:
        client.delete_collection("hr_playbook")
        hr_collection = client.get_or_create_collection(
            name="hr_playbook",
            embedding_function=embedding_fn
        )
        print("Cleared existing hr_playbook collection for fresh import.")
    except Exception as e:
        print(f"Error resetting collection: {e}")

    all_docs = []
    all_ids = []
    all_metas = []

    # 1. Parse KOMP_EOR_Playbook_Ver1.0.xlsx
    eor_path = Path(eor_file)
    if eor_path.exists():
        print(f"Parsing EOR Playbook: {eor_path.name}...")
        eor_xls = pd.ExcelFile(eor_path)
        for sheet_name in eor_xls.sheet_names:
            df = pd.read_excel(eor_path, sheet_name=sheet_name, header=None)
            
            # Identify topic groups
            topics = []
            current_topic = None
            for r in range(2, df.shape[0]):
                sno = get_val(df, r, 0)
                title = get_val(df, r, 1)
                if sno is not None or title is not None:
                    if current_topic:
                        topics.append(current_topic)
                    current_topic = {
                        "sno": sno,
                        "title": title,
                        "start_row": r,
                        "end_row": r
                    }
                else:
                    if current_topic:
                        current_topic["end_row"] = r
            if current_topic:
                topics.append(current_topic)
                
            # Parse country columns
            for c in range(2, df.shape[1], 2):
                country_name = get_val(df, 1, c)
                if not country_name or str(country_name).strip() in ['', '-', 'No.', '% /days']:
                    continue
                country_name = str(country_name).strip()
                
                for idx, topic in enumerate(topics):
                    details = []
                    for r in range(topic["start_row"], topic["end_row"] + 1):
                        val1 = get_val(df, r, c)
                        val2 = get_val(df, r, c + 1)
                        
                        if val1 is not None:
                            val1 = str(val1).strip()
                        if val2 is not None:
                            val2 = str(val2).strip()
                            
                        if val1 in ['-', '']:
                            val1 = None
                        if val2 in ['-', '']:
                            val2 = None
                            
                        if val1 and val2:
                            details.append(f"{val1}: {val2}")
                        elif val1:
                            details.append(val1)
                        elif val2:
                            details.append(val2)
                    
                    if details:
                        details_str = "\n".join(f"  {d}" for d in details)
                        doc_content = f"Country: {country_name}\nCategory: EOR Compliance\nTopic: {topic['title']}\n\nDetails:\n{details_str}"
                        
                        doc_id = f"eor_{sheet_name}_{country_name}_{idx}".lower().replace(" ", "_")
                        all_docs.append(doc_content)
                        all_ids.append(doc_id)
                        all_metas.append({
                            "source_file": eor_path.name,
                            "knowledge_base": "hr_playbook"
                        })
    else:
        print(f"Warning: EOR file not found at {eor_file}")

    # 2. Parse HR Playbook_Employee Lifecycle_Ver1.0.xlsx
    hr_path = Path(hr_file)
    if hr_path.exists():
        print(f"Parsing HR Playbook: {hr_path.name}...")
        hr_xls = pd.ExcelFile(hr_path)
        for sheet_name in hr_xls.sheet_names:
            df = pd.read_excel(hr_path, sheet_name=sheet_name, header=None)
            priority = sheet_name.strip()
            
            current_category = None
            current_sub_category = None
            project_idx = 0
            
            for r in range(df.shape[0]):
                sno = get_val(df, r, 1)
                hr_project = get_val(df, r, 2)
                sno_str = str(sno).strip() if sno is not None else ""
                
                if sno_str.upper() == 'SNO':
                    current_category = str(hr_project).strip() if hr_project else None
                    current_sub_category = None
                    continue
                    
                if sno is None and hr_project is not None:
                    val = str(hr_project).strip()
                    if val and val != '-':
                        current_sub_category = val
                    continue
                    
                is_numeric = False
                try:
                    float(sno_str)
                    is_numeric = True
                except ValueError:
                    pass
                    
                if is_numeric:
                    project_name = str(hr_project).strip() if hr_project else ""
                    frequency = get_val(df, r, 3)
                    timelines = get_val(df, r, 4)
                    action_plan = get_val(df, r, 5)
                    business_impact = get_val(df, r, 6)
                    success_measures = get_val(df, r, 7)
                    status_update = get_val(df, r, 8)
                    timelines_met = get_val(df, r, 9)
                    revised_timeline = get_val(df, r, 10)
                    support_required = get_val(df, r, 11)
                    
                    doc_parts = []
                    doc_parts.append(f"Priority: {priority}")
                    if current_category:
                        doc_parts.append(f"Category: {current_category}")
                    if current_sub_category:
                        doc_parts.append(f"Sub-Category: {current_sub_category}")
                    doc_parts.append(f"HR Project: {project_name}")
                    
                    if frequency:
                        doc_parts.append(f"Frequency: {str(frequency).strip()}")
                    if timelines:
                        doc_parts.append(f"Timeline: {str(timelines).strip()}")
                    if action_plan:
                        doc_parts.append(f"Action Plan:\n{str(action_plan).strip()}")
                    if business_impact:
                        doc_parts.append(f"Business Impact:\n{str(business_impact).strip()}")
                    if success_measures:
                        doc_parts.append(f"Success Measures:\n{str(success_measures).strip()}")
                    if status_update:
                        doc_parts.append(f"Status Update: {str(status_update).strip()}")
                    if timelines_met:
                        doc_parts.append(f"Timelines Met/Deferred: {str(timelines_met).strip()}")
                    if revised_timeline:
                        doc_parts.append(f"Revised Timeline: {str(revised_timeline).strip()}")
                    if support_required:
                        doc_parts.append(f"Support Required: {str(support_required).strip()}")
                        
                    doc_content = "\n\n".join(doc_parts)
                    doc_id = f"hr_{priority.lower().replace(' ', '_')}_{project_idx}"
                    project_idx += 1
                    
                    all_docs.append(doc_content)
                    all_ids.append(doc_id)
                    all_metas.append({
                        "source_file": hr_path.name,
                        "knowledge_base": "hr_playbook"
                    })
    else:
        print(f"Warning: HR Playbook file not found at {hr_file}")

    if all_docs:
        print(f"Adding {len(all_docs)} documents to the hr_playbook collection...")
        hr_collection.add(
            ids=all_ids,
            documents=all_docs,
            metadatas=all_metas
        )
        print("Chroma ingestion for hr_playbook completed.")
    else:
        print("No documents were processed for hr_playbook.")


if __name__ == "__main__":
    # Base workspace data folder path
    data_dir = Path(__file__).resolve().parents[2] / "data"
    
    # 1. Ingest original compliance records
    ingest_json(str(data_dir / "latam_laws_flat.json"))
    
    # 2. Ingest playbooks
    ingest_excel(
        str(data_dir / "KOMP_EOR_Playbook_Ver1.0.xlsx"),
        str(data_dir / "HR Playbook_Employee Lifecycle_Ver1.0.xlsx")
    )
