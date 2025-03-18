from langchain_core.messages import SystemMessage, HumanMessage

from app.core.agents_llms import schema_validation_llm
from app.core.prompts import SCHEMA_VALIDATION_PROMPT, SCHEMA_VALIDATION_SYSTEM_PROMPT
from langchain_neo4j import Neo4jGraph

from app.core.state_models import CypherAgentState
from app.db.neo4j_client import Neo4jClient


def validate_query(state: CypherAgentState) -> CypherAgentState:
    """
    Combined validation using both LLM and Neo4j.
    """
    if not state.generated_query:
        state.messages.append("Validation: No generated query available.")
        state.is_query_valid = False
        return state

    user_prompt = SCHEMA_VALIDATION_PROMPT.format(
        question=state.query,
        cypher_query=state.generated_query
    )

    messages = [
        SystemMessage(content=SCHEMA_VALIDATION_SYSTEM_PROMPT),
        HumanMessage(content=user_prompt)
    ]

    response = schema_validation_llm.invoke(messages).content.strip().lower()

    if response != "valid":
        state.is_query_valid = False
        state.messages.append("Validation: Query invalid according to LLM.")
        return state

    # Then validate with Neo4j
    kg = Neo4jClient.get_instance()

    try:
        validation_query = "EXPLAIN " + state.generated_query
        kg.query_knowledge_graph(validation_query)
        state.is_query_valid = True
        state.messages.append("Validation: Query is valid.")
    except Exception as e:
        state.is_query_valid = False
        state.messages.append(f"Validation error: {str(e)}")

    return state
