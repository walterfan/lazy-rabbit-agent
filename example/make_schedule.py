#!/usr/bin/env python3
import simple_llm_agent
from pydantic import BaseModel
from typing import Type, List, Optional
from enum import Enum

# Define query types for document-related inquiries
class QueryType(str, Enum):
    DOCUMENT_CONTENT = "document_content"
    LAST_MODIFIED = "last_modified"
    ACCESS_PERMISSIONS = "access_permissions"
    RELATED_DOCUMENTS = "related_documents"

# Define the structure for query responses
class QueryResponse(BaseModel):
    query_type: QueryType
    response: str
    additional_info: Optional[str] = None


class Scheduler:
    def __init__(self):
        self._llm_agent = simple_llm_agent.LlmAgent()
        self._system_prompt = "You are an expert in scheduling and planning."

    def process_confidential_query(self, query: str) -> QueryResponse:
        prompt = f"""Analyze the following confidential document query and provide an appropriate response:
        Query: {query}

        Determine the type of query (document content, last modified, access permissions, or related documents),
        provide a response, and include a confidence score and any additional relevant information.
        Remember, you're handling confidential data, so be cautious about specific details.
        """

        return self._llm_agent.get_object_response(self._system_prompt,  prompt, QueryResponse)


def demo():
    scheduler = Scheduler()

    input = {
        "目标": "提高编程能力",
        "今日任务": ["学习新技术", "练习算法", "阅读技术博客"],
        "优先级": {"学习新技术": "高", "练习算法": "中", "阅读技术博客": "低"},
        "可用时间": ["9:00-11:30", "13:30-18:00"]
     }

    # Sample confidential document queries
    confidential_queries = [
        "What are the key findings in the Q4 financial report?",
        "Who last accessed the merger proposal document?",
        "What are the access permissions for the new product roadmap?",
        "Are there any documents related to Project X's budget forecast?",
        "When was the board meeting minutes document last updated?",
    ]

    # Process each query and print the results
    for i, query in enumerate(confidential_queries, 1):
        response:QueryResponse = scheduler.process_confidential_query(query)
        print(f"{query} : {response.query_type}")
        """
        #> What are the key findings in the Q4 financial report? : document_content
        #> Who last accessed the merger proposal document? : access_permissions
        #> What are the access permissions for the new product roadmap? : access_permissions
        #> Are there any documents related to Project X's budget forecast? : document_content
        #> When was the board meeting minutes document last updated? : last_modified
        """

if __name__ == "__main__":
    demo()