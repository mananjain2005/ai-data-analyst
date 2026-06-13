# from llm import get_llm

# llm = get_llm()

# response = llm.invoke(
#     "What is a dataframe in one sentence?"
# )

# print(response.content)

# from dataframe_utils import (
#     load_dataframe,
#     summarize_dataframe
# )

# df = load_dataframe("../data/sample.csv")

# summary = summarize_dataframe(df)

# print(summary)

# from dataframe_utils import load_dataframe
# from executor import execute_python

# df = load_dataframe("../data/sample.csv")

# code = """
# result = df.groupby("region")["revenue"].sum()
# """

# answer = execute_python(code, df)

# print(answer)

# from dataframe_utils import load_dataframe
# from analyst import ask_analyst

# df = load_dataframe("../data/sample.csv")

# while True:

#     question = input("\nQuestion (type 'exit' to quit): ")

#     if question.lower() == "exit":
#         break

#     answer = ask_analyst(
#         question,
#         df
#     )

#     print("\nReasoning:")
#     print(answer["reasoning"])

#     print("\nGenerated Code:")
#     print(answer["generated_code"])

#     print("\nResult:")
#     print(answer["result"])

from dataframe_utils import (
    load_dataframe,
    summarize_dataframe
)

from graph import graph

df = load_dataframe("../data/sample.csv")

metadata = summarize_dataframe(df)

while True:

    question = input("\nQuestion (type 'exit' to quit): ")

    if question.lower() == "exit":
        break

    result = graph.invoke(
        {
            "question": question,
            "metadata": metadata,
            "attempts": 0
        }
    )

    # print("\nAnswer:")
    # print(result["final_answer"])

    print("\nGenerated Plan:")
    for i, step in enumerate(result["plan"], start=1):
        print(f"{i}. {step}")

    print("\nGenerated Code:")
    print(result["generated_code"])

    print(f"\nValidation Attempt: {result['attempts']}")

    print("\nReturned State Keys:")
    print(result.keys())

    print(f"\nValidation Passed: {result['validation_passed']}")

    print(f"\nValidation Feedback:")
    print(result["validation_feedback"])

    print("\nExecution Result:")
    print(result["execution_result"])

    print("\nFinal Answer:")
    print(result["final_answer"])

# Which region generated highest revenue?
# 
#     "Calculate total revenue by region",
#     "Rank regions by total revenue",
#     "Identify the top-performing region"
# 
# Why did revenue decline in March?
# 
#     "Calculate monthly revenue trend",
#     "Quantify March revenue decline",
#     "Analyze category-level contribution to the decline",
#     "Analyze regional contribution to the decline",
#     "Identify the primary drivers"
# 
