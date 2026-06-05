import re

class IntentClassifier:
    """
    Service to classify user queries into intents: COMPLIANCE, HR, or GENERAL.
    
    Why this exists:
        In a multi-knowledge-base RAG system, routing queries to the correct vector 
        collection improves search relevance and speed, and prevents mixing contexts 
        from different domains (e.g., mixing HR internal policies with regulatory laws).

    How it works:
        It uses case-insensitive keyword and phrase matching. It normalizes the user 
        query and checks for the presence of specific regulatory or human resource terms.
        If any matching keyword is found, the respective intent is returned.
        Otherwise, it falls back to GENERAL.

    How it connects:
        This class is imported by `compliance_agent.py` to classify incoming queries
        before selecting the vector database collection to search.

    Common mistakes:
        - Exact string matching instead of substring or token boundary matching.
        - Not handling case sensitivity.
        - Hardcoding collection routing directly inside the classifier (violating separation of concerns).
    """

    @staticmethod
    def classify(query: str) -> str:
        if not query:
            return "GENERAL"
            
        # Normalize: convert to lowercase and strip whitespace
        normalized_query = query.lower().strip()
        
        # Word list for HR queries
        hr_keywords = [
            "leave", "vacation", "employee", "employee lifecycle", "onboarding", 
            "offboarding", "recruitment", "hiring", "termination", "resignation", 
            "probation", "performance review", "promotion", "manager", "hr policy"
        ]
        
        # Word list for COMPLIANCE queries
        compliance_keywords = [
            "brazil", "argentina", "chile", "mexico", "peru", "colombia", "latam", 
            "employment law", "compliance", "regulation", "legal requirement", "eor", 
            "payroll compliance"
        ]
        
        # Check for HR matches
        for keyword in hr_keywords:
            if keyword in normalized_query:
                return "HR"
                
        # Check for COMPLIANCE matches
        for keyword in compliance_keywords:
            if keyword in normalized_query:
                return "COMPLIANCE"
                
        # Fallback to GENERAL
        return "GENERAL"
