from typing import TypedDict, Optional

# State of our LangGraph Graph
# shared memory of the graph
class AnalystState(TypedDict):

    question: str

    metadata: dict

    plan: list[str]

    generated_code: Optional[str]

    reasoning: Optional[str]

    validation_passed: Optional[bool]
    validation_feedback: Optional[str]
    attempts: int

    execution_result: Optional[str]

    final_answer: Optional[str]