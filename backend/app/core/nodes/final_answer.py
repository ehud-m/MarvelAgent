from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.prompts import PromptTemplate

from app.core.agents_llms import final_answer_generation_llm
from app.core.prompts import ANSWER_GENERATION_PROMPT, ANSWER_GENERATION_SYSTEM_PROMPT
from app.core.state_models import CypherAgentState


def final_answer_write_node(state: CypherAgentState) -> CypherAgentState:
    """
    Generate a final answer to the user's query based on the query results.
    """
    if not state.result:
        state.messages.append("Final Answer: No results available to generate an answer.")
        return state

    # Format user-facing prompt
    user_prompt = ANSWER_GENERATION_PROMPT.format(
        user_query=state.query,
        cypher_query=state.generated_query,
        query_results=state.result
    )

    # Combine system and user messages
    messages = [
        SystemMessage(content=ANSWER_GENERATION_SYSTEM_PROMPT),
        HumanMessage(content=user_prompt)
    ]

    # Run LLM
    response = final_answer_generation_llm.invoke(messages)
    state.final_answer = response.content.strip()
    state.messages.append("Final Answer: Generated response to user query.")
    return state