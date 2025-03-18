import json

from langchain_core.messages import SystemMessage, HumanMessage

from app.core.agents_llms import character_summary_llm
from app.core.prompts import CHARACTER_SUMMARY_PROMPT_TEMPLATE, CHARACTER_SUMMARY_SYSTEM_PROMPT
from app.core.state_models import CypherAgentState


def summarize_character_descriptions(state: CypherAgentState) -> CypherAgentState:
    """
    Summarizes character descriptions in the query results.
    If too many characters are returned, only list their names and ask the user to narrow down the query.
    """
    if not state.result:
        state.messages.append("Summarization: No results to summarize.")
        return state

    try:
        result_data = json.loads(state.result)
    except json.JSONDecodeError:
        state.messages.append("Summarization: Failed to parse result JSON.")
        return state

    characters = []
    for item in result_data:
        char = item.get("c") or item.get("character")
        if char and isinstance(char, dict):
            characters.append(char)

    if not characters:
        state.messages.append("Summarization: No characters found.")
        return state

    # Threshold to avoid summarizing too many characters
    MAX_CHARACTERS = 7
    if len(characters) > MAX_CHARACTERS:
        names = [char.get("name", "Unknown") for char in characters]
        limited_names = ", ".join(names)
        state.final_answer = (
            f"I found {len(characters)} characters, which is quite a lot to summarize in detail.\n\n"
            f"Here are their names: {limited_names}.\n\n"
            "Would you like to focus on one or more specific characters?"
        )
        state.messages.append("Summarization: Too many characters, prompt user to refine selection.")
        return state

    # Otherwise, summarize their descriptions
    descriptions = [char["description"] for char in characters if "description" in char]
    joined_text = "\n".join(descriptions)

    user_prompt = CHARACTER_SUMMARY_PROMPT_TEMPLATE.format(descriptions=joined_text)

    messages = [
        SystemMessage(content=CHARACTER_SUMMARY_SYSTEM_PROMPT),
        HumanMessage(content=user_prompt)
    ]

    summary = character_summary_llm.invoke(messages).content.strip()
    state.result += f'\n\n"summary": "{summary}"'
    state.messages.append("Summarization: Character descriptions summarized.")

    return state
