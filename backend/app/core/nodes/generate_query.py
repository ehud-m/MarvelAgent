from langchain_core.messages import SystemMessage, HumanMessage

from app.core.agents_llms import cypher_generation_llm
from app.core.prompts import CYHPER_GENERATION_PROMPT, MARVEL_CYPHER_SYSTEM_PROMPT
from app.core.state_models import CypherAgentState
from langchain.prompts import PromptTemplate


def clean_cypher_query(query: str) -> str:
    """
    Removes markdown formatting (triple backticks and language identifiers)
    from the generated Cypher query.
    """
    query = query.strip()
    if query.startswith("```"):
        lines = query.splitlines()
        # Remove the first line if it's a markdown code block start (e.g., "```cypher")
        if lines[0].strip().startswith("```"):
            lines = lines[1:]
        # Remove the last line if it is the closing triple backticks
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        return "\n".join(lines).strip()
    return query




def generate_cypher_query(state: CypherAgentState) -> CypherAgentState:
    """
    Generates a Cypher query from the natural language query stored in state.query.
    """
    if not state.query:
        state.messages.append("No natural language query provided.")
        return state

    # Format user message prompt
    user_prompt = CYHPER_GENERATION_PROMPT.format(question=state.query)

    # Construct chat message sequence
    messages = [
        SystemMessage(content=MARVEL_CYPHER_SYSTEM_PROMPT),
        HumanMessage(content=user_prompt)
    ]

    # Generate and clean query
    raw_query = cypher_generation_llm.invoke(messages).content.strip()
    state.generated_query = clean_cypher_query(raw_query)
    state.messages.append("Generated and cleaned Cypher query.")
    return state