from typing import TypedDict, Optional
from pandas import DataFrame

# State of our LangGraph Graph
# shared memory of the graph
class AnalystState(TypedDict):

    df: DataFrame

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

    chart_requested: Optional[bool]

    # critic_passed: Optional[bool]
    # critic_feedback: Optional[str]
    # critic_attempts: int