from pydantic import BaseModel, Field
from typing import List

# Structured Output for LLM that generates a python code
class AnalysisResponse(BaseModel):
    reasoning: str = Field(
        description="Reasoning behind the analysis"
    )

    python_code: str = Field(
        description="Python code to execute. Must store final answer in variable 'result'"
    )

# Structured Output for LLM that generates a coding plan (list of instructions)
class PlannerOutput(BaseModel):
    plan: List[str]

# Structured Output for LLM that validates a python code
class ValidationOutput(BaseModel):

    is_valid: bool
    feedback: str

# Structured Output for LLM that acts as a critic, judging the final answer
class CriticOutput(BaseModel):

    is_satisfactory: bool

    feedback: str

# Structured Output for the Plan Generator node's LLM
class PlanStep(BaseModel):
    step_number: int
    description: str