from app.core.nodes.decision import decision_node
from app.core.nodes.execute_query import execute_query_neo4j
from app.core.nodes.final_answer import final_answer_write_node
from app.core.nodes.generate_query import generate_cypher_query
from app.core.nodes.judge_answer import answer_judge_node
from app.core.nodes.summarize import summarize_character_descriptions
from app.core.nodes.validate_query import validate_query
from app.core.state_models import CypherAgentState
from langgraph.graph import StateGraph, START, END

from app.db.redis_client import RedisClient




def build_cypher_agent():
    """Create and return the compiled Cypher agent graph."""
    cypher_graph = StateGraph(CypherAgentState)

    # Add individual nodes
    cypher_graph.add_node("decision", decision_node)
    cypher_graph.add_node("generate", generate_cypher_query)
    cypher_graph.add_node("validate", validate_query)
    cypher_graph.add_node("execution", execute_query_neo4j)
    cypher_graph.add_node("answer_generation", final_answer_write_node)
    cypher_graph.add_node("answer_judgment", answer_judge_node)
    cypher_graph.add_node("summarize_characters", summarize_character_descriptions)


    # Set entry point
    cypher_graph.set_entry_point("decision")

    # Add conditional edges
    cypher_graph.add_conditional_edges(
        "decision",
        lambda state: decision_node(state)["next"],
        {
            "generate": "generate",
            "execution": "execution",
            "answer_generation": "answer_generation",
            "answer_judgment": "answer_judgment",
            "end": END
        }
    )

    # Direct edges between nodes
    cypher_graph.add_edge("generate", "validate")
    cypher_graph.add_edge("validate", "decision")
    # cypher_graph.add_edge("execution", "decision")
    cypher_graph.add_edge("execution", "summarize_characters")
    cypher_graph.add_edge("summarize_characters", "decision")
    cypher_graph.add_edge("answer_generation", "decision")
    cypher_graph.add_edge("answer_judgment", "decision")

    # Compile the graph
    return cypher_graph.compile()

def run_cypher_agent(query: str, debug: bool = False):
    """
    Run the Cypher agent with a given natural language query.

    Args:
        query (str): Natural language query to process
        debug (bool): Whether to print debug information

    Returns:
        CypherAgentState: The final state after processing
    """
    # Create an initial state with the query
    key = query.strip().lower()
    redis_client = RedisClient.get_instance()

    # Check Redis cache
    cached_answer = redis_client.get(key)
    if cached_answer:
        if debug:
            print("\n[Cache Hit] Returning cached answer.\n")
        # Return minimal fake state with the cached result
        return CypherAgentState(
            query=query,
            final_answer=cached_answer,
            messages=["Cache hit: returning previously computed answer."]
        )

    initial_state = CypherAgentState(query=query)

    # Build and run the agent
    app = build_cypher_agent()
    final_state = app.invoke(initial_state, {'recursion_limit': 30}, debug=debug)

    if final_state['final_answer']:
        redis_client.set(key, final_state['final_answer'])

    # # Print the final answer if available
    # if final_state.final_answer and not debug:
    #     print(f"\nAnswer: {final_state.final_answer}")

    return final_state