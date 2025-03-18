import json

from app.core.state_models import CypherAgentState
from app.db.neo4j_client import Neo4jClient



def execute_query_neo4j(state: CypherAgentState) -> CypherAgentState:
    """
    Execute the generated Cypher query against Neo4j.
    """
    if not state.is_query_valid or not state.generated_query:
        state.messages.append("Execution: Query not valid or not generated; aborting execution.")
        return state

    kg = Neo4jClient.get_instance()
    try:
        result = kg.query_knowledge_graph(state.generated_query)
        state.result = json.dumps(result)
        state.messages.append("Execution: Query executed successfully.")
    except Exception as e:
        state.messages.append(f"Execution error: {str(e)}")
    return state