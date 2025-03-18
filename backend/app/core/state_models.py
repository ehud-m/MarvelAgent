from pydantic import BaseModel
from typing import Optional, List


class CypherAgentState(BaseModel):
    """
    Represents the state of a Cypher query agent.

    Attributes:
        query (Optional[str]): The natural language query provided by the user.
        generated_query (Optional[str]): The Cypher query generated from the natural language query.
        result (Optional[str]): The result of executing the generated query.
        messages (List[str]): Log or status messages.
        is_query_valid (bool): Flag indicating if the generated query passed validation.
        final_answer (Optional[str]): The final answer to the user's query.
        answer_quality (Optional[str]): Assessment of the answer quality.
        needs_refinement (bool): Flag indicating if the answer needs refinement.
        refinement_feedback (Optional[str]): Feedback for refining the query or answer.
    """
    query: Optional[str] = None
    generated_query: Optional[str] = None
    result: Optional[str] = None
    messages: List[str] = []
    is_query_valid: bool = False
    final_answer: Optional[str] = None
    answer_quality: Optional[str] = None
    needs_refinement: bool = False
    refinement_feedback: Optional[str] = None
