from langchain_core.messages import SystemMessage, HumanMessage

from app.core.agents_llms import answer_judgment_llm
from app.core.prompts import ANSWER_JUDGMENT_PROMPT, ANSWER_JUDGMENT_SYSTEM_PROMPT
from app.core.state_models import CypherAgentState
from langchain.prompts import PromptTemplate


def answer_judge_node(state: CypherAgentState) -> CypherAgentState:
    """
    Judge the quality of the final answer and determine if refinement is needed.
    """
    if not state.final_answer:
        state.messages.append("Judge: No final answer to evaluate.")
        state.needs_refinement = True
        state.refinement_feedback = "No answer was generated. Please ensure the query execution was successful."
        return state

    # Format user message with evaluation context
    prompt_text = ANSWER_JUDGMENT_PROMPT.format(
        user_query=state.query,
        cypher_query=state.generated_query,
        query_results=state.result,
        generated_answer=state.final_answer
    )

    # Build message sequence
    messages = [
        SystemMessage(content=ANSWER_JUDGMENT_SYSTEM_PROMPT),
        HumanMessage(content=prompt_text)
    ]

    # Invoke the LLM
    judgment = answer_judgment_llm.invoke(messages).content.strip()

    # Parse the LLM's judgment
    if "EXCELLENT" in judgment or "GOOD" in judgment:
        state.answer_quality = judgment.split("\n")[0] if "\n" in judgment else judgment
        state.needs_refinement = False
        state.messages.append(f"Judge: Answer quality is {state.answer_quality}.")
    else:
        state.answer_quality = "NEEDS_REFINEMENT"
        state.needs_refinement = True
        state.refinement_feedback = judgment
        state.messages.append("Judge: Answer needs refinement.")

    return state