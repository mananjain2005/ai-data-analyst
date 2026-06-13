from llm import get_llm
from schemas import AnalysisResponse
from dataframe_utils import summarize_dataframe
from executor import execute_python


def ask_analyst(question, df):

    metadata = summarize_dataframe(df)

    llm = get_llm()

    structured_llm = llm.with_structured_output(
        AnalysisResponse
    )

    prompt = f"""
You are a senior data analyst.

Dataset Metadata:

{metadata}

The dataframe is available as variable df.

User Question:
{question}

Generate Python code.

Rules:
1. Use pandas.
2. Store final answer in variable result.
3. Return only valid structured output.
"""

    response = structured_llm.invoke(prompt)

    result = execute_python(
        response.python_code,
        df
    )

    return {
        "reasoning": response.reasoning,
        "generated_code": response.python_code,
        "result": result
    }