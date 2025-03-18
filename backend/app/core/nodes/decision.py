from app.core.state_models import CypherAgentState


def decision_node(state: CypherAgentState) -> dict:
    """
    Single decision node that determines the next step in the workflow.
    Returns a dict with the next step key.
    """
    if not state.query:
        return {"next": "end"}
    if not state.generated_query:
        return {"next": "generate"}
    if not state.is_query_valid:
        # Clear invalid query and regenerate
        state.generated_query = None
        return {"next": "generate"}
    if not state.result:
        return {"next": "execution"}
    if not state.final_answer:
        return {"next": "answer_generation"}
    if not state.answer_quality:
        return {"next": "answer_judgment"}
    if state.needs_refinement:
        # Reset for refinement based on feedback
        state.generated_query = None
        state.result = None
        state.final_answer = None
        state.answer_quality = None
        state.needs_refinement = False
        state.messages.append(f"Decision: Refining based on feedback: {state.refinement_feedback}")
        return {"next": "generate"}
    # If we have a good answer, we're done
    return {"next": "end"}
