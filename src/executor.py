import pandas as pd

def execute_python(code: str, df: pd.DataFrame):
    """
    Execute LLM-generated Python code.

    The generated code MUST store the final answer
    in a variable named 'result'.
    """

    local_vars = {
        "df": df,
        "pd": pd
    }

    try:
        exec(code, {}, local_vars)

        if "result" not in local_vars:
            raise ValueError(
                "Generated code did not create a variable named 'result'"
            )

        return local_vars["result"]

    except Exception as e:
        return f"Execution Error: {str(e)}"