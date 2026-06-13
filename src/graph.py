from langgraph.graph import StateGraph, START, END

from state import AnalystState
from llm import get_llm
from schemas import AnalysisResponse, PlannerOutput, ValidationOutput, CriticOutput
from executor import execute_python
from dataframe_utils import load_dataframe

# NODE 1: PLANNING NODE
def planner_node(state):

    llm = get_llm()

    structured_llm = llm.with_structured_output(
        PlannerOutput
    )

#     prompt = f"""
# You are a senior business analyst.

# Question:
# {state['question']}

# Create a short analysis plan.

# Return 3-5 steps.
# """

    prompt = f"""
You are a senior data analyst.

Your job is NOT to answer the question.

Your job is to create a step-by-step analytical plan that another agent will use to analyze a pandas DataFrame.

Dataset Metadata:
{state['metadata']}

User Question:
{state['question']}

Guidelines:

1. Create 3-5 concrete analysis steps.
2. Focus on calculations that can be performed using a pandas DataFrame.
3. Be specific.
4. Do not write Python code.
5. Do not answer the question.
6. Each step should represent a distinct analytical task.
7. Prefer data-driven investigation over assumptions.
8. If the question cannot be answered from the available dataset metadata, create a plan that first investigates what relevant columns are available.

Examples:

Question:
"Which region generated the highest revenue?"

Plan:
[
    "Calculate total revenue by region",
    "Rank regions by revenue",
    "Identify the region with the highest revenue"
]

Question:
"Why did revenue decline in March?"

Plan:
[
    "Calculate monthly revenue trend",
    "Compare March revenue with February",
    "Compare March revenue with April",
    "Analyze revenue by product category in March",
    "Analyze revenue by region in March"
]

Return only the analysis plan.
"""
    
    response = structured_llm.invoke(prompt)

    return {
        "plan": response.plan
    }

# NODE 2: GENERATE CODE
def generate_code(state):

    llm = get_llm()

    structured_llm = llm.with_structured_output(
        AnalysisResponse
    )
    # AnalysisResponse: Reasoning and Python_Code

    prompt = f"""
You are a senior data analyst.

A pandas DataFrame named df already exists.

Dataset metadata:

{state['metadata']}

Analysis Plan:

{state['plan']}

User Question:

{state['question']}

Previous Validation Feedback:
{state.get("validation_feedback", "None")}

Critic Feedback:
{state.get("critic_feedback", "None")}

You must fix all issues mentioned in both validation feedback and critic feedback.

The plan contains required analysis steps.
Your generated code must implement every step in the plan.
If a step is ignored, the analysis will be considered incomplete.

Generate pandas code.

Rules:

1. Use dataframe df for all calculations
2. NEVER overwrite df.
3. Never create unnecessary columns
4. Prefer pandas aggregation operations.
5. The variable 'result' should contain the final answer directly.
6. Do not store intermediate calculations inside df.
7. NEVER use metadata to answer analytical questions.
8. Use temporary variables when needed.
9. Stick to the instructions given as 'Analysis Plan'
10. Use the sample values provided in metadata to understand column formats.
11. Before performing any date, time, month, quarter, year, weekday, season, trend, or time-series analysis, convert the relevant column(s) to datetime format.


Example1:

Question:
Which region generated highest revenue?

Good Code:

region_revenue = df.groupby("region")["revenue"].sum()
result = region_revenue.idxmax()

Bad Code:

df["revenue_by_region"] = ...

Example2:

Question:
What was the total revenue in March?

Good Code:

df["date"] = pd.to_datetime(df["date"])

march_revenue = (
    df[df["date"].dt.month == 3]
    ["revenue"]
    .sum()
)

result = march_revenue

If the user explicitly requests a chart, generate Python code that:

1. Creates the required visualization using matplotlib.
2. Saves the chart to the ../outputs/ folder.
3. Stores the image path in variable 'result'.
4. Do not call plt.show()
5. Use informative titles
6. Label axes clearly

Example:

plt.savefig("../outputs/chart.png")
result = "../outputs/chart.png"

"""

    response = structured_llm.invoke(prompt)

    return {
        "generated_code": response.python_code,
        "reasoning": response.reasoning,
        "attempts": state.get("attempts", 0) + 1
    }

df = load_dataframe("../data/sample.csv")

# NODE 3: VALIDATE CODE
def validate_code(state):

    llm = get_llm()

    structured_llm = llm.with_structured_output(
        ValidationOutput
    )

    feedback = state.get(
    "validation_feedback",
    "No validation feedback available."
)

    prompt = f"""
You are a senior Python reviewer.

Review this generated pandas code.

Question:
{state['question']}

Code:
{state['generated_code']}

Dataset Metadata:
{state['metadata']}

Check for:

1. Incorrect date handling.
2. String matching on dates.
3. Overwriting dataframe df.
4. Creating unnecessary dataframe columns.
5. Operations that may fail on empty data.
6. Obviously incorrect logic.
7. Dangerous operations.

If the code is acceptable:

- Set is_valid = True
- Give a short feedback message

If the code has problems:

- Set is_valid = False
- Explain the most important issue
- Suggest how to fix it

Be concise. Only flag issues that are likely to occur given the provided metadata. Do not flag hypothetical issues such as missing columns that are known to exist.

If chart generation is requested:

Check that:

1. matplotlib is imported.
2. plt.savefig(...) is used.
3. plt.show() is NOT used.
4. result contains the saved image path.
5. The chart has a title.
6. Axes are labeled when appropriate.
"""

    response = structured_llm.invoke(prompt)

    return {
        "validation_passed": response.is_valid,
        "validation_feedback": response.feedback
    }

MAX_ATTEMPTS = 2

# Conditional Router
def validation_router(state):

    if state["validation_passed"]:
        return "execute_code"
    
    if state["attempts"] >= MAX_ATTEMPTS:
        print(f"Max attempts reached ({MAX_ATTEMPTS}). Executing anyway...")
        return "execute_code"

    return "generate_code"

# NODE 4: EXECUTE CODE
def execute_code(state):

    result = execute_python(
        state["generated_code"],
        df
    )

    return {
        "execution_result": str(result)
    }

# NODE 5: CRITIC NODE
def critic_node(state):

    llm = get_llm()

    structured_llm = llm.with_structured_output(
        CriticOutput
    )

    prompt = f"""
You are a senior data analytics reviewer.

Question:
{state['question']}

Analysis Plan:
{state['plan']}

Generated Code:
{state['generated_code']}

Execution Result:
{state['execution_result']}

Determine whether the execution result sufficiently answers the user's question.

For each plan step:

1. Mark COMPLETED or NOT COMPLETED.
2. Explain why.
3. List all missing steps.
4. Set is_satisfactory=False if any important step is missing.

Rules:

1. Focus on whether the question was answered.
2. Do not review code quality.
3. Do not suggest alternative implementations.
4. Check whether the analysis plan was completed.
5. If critical information is missing, reject.

Return concise feedback.
"""

    response = structured_llm.invoke(prompt)

    return {
        "critic_passed": response.is_satisfactory,
        "critic_feedback": response.feedback,
        "critic_attempts": state.get("critic_attempts", 0) + 1
    }


# CRITIC ROUTER
MAX_CRITIC_ATTEMPTS = 2

def critic_router(state):

    if state["critic_passed"]:
        return "generate_answer"

    if state["critic_attempts"] >= MAX_CRITIC_ATTEMPTS:
        print(
            f"Critic max attempts reached "
            f"({MAX_CRITIC_ATTEMPTS})."
        )
        return "generate_answer"

    return "generate_code"

# NODE 6: ANSWER NODE
def generate_answer(state):

    llm = get_llm()

    prompt = f"""
You are a data analyst assistant.

User's Question:
{state['question']}

Computed Analysis Result:
{state['execution_result']}

Rules:

1. The computed analysis result is the source of truth.
2. Do NOT perform any additional calculations.
3. Do NOT make assumptions.
4. Do NOT say information is missing if a computed result exists.
5. Base your answer entirely on the computed analysis result.
6. If the result contains an execution error, explain the error instead of answering the question.

Provide a concise answer that responds to the user's question.
"""
    
    execution_result = state["execution_result"]

    if isinstance(execution_result, str) and execution_result.endswith(".png"):
        return {
            "final_answer": f"Chart generated successfully: {execution_result}"
        }

    response = llm.invoke(prompt)

    return {
        "final_answer": response.content
    }

# Build graph
builder = StateGraph(AnalystState)

builder.add_node("planner", planner_node)
builder.add_node("generate_code", generate_code)
builder.add_node("validate_code", validate_code)
builder.add_node("execute_code", execute_code)
# builder.add_node("critic", critic_node)
builder.add_node("generate_answer", generate_answer)

builder.add_edge(START, "planner")
builder.add_edge("planner", "generate_code")
builder.add_edge("generate_code", "validate_code")
builder.add_conditional_edges(
    "validate_code",
    validation_router,
    {
        "execute_code": "execute_code",
        "generate_code": "generate_code"
    }
)
builder.add_edge("execute_code", "generate_answer")
# builder.add_conditional_edges(
#     "critic",
#     critic_router,
#     {
#         "generate_answer": "generate_answer",
#         "generate_code": "generate_code"
#     }
# )
builder.add_edge("generate_answer", END)

graph = builder.compile()