# streamlit run ..\app.py

import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Allow imports from src/
sys.path.append(str(Path(__file__).parent / "src"))

from graph import graph
from dataframe_utils import summarize_dataframe

st.set_page_config(
    page_title="AI Data Analysis Agent",
    page_icon="📊",
    layout="wide"
)

st.title("📊 AI Data Analysis Agent")

st.markdown(
    "Upload a CSV file and ask questions in natural language."
)

# -------------------------
# Upload CSV
# -------------------------

uploaded_file = st.file_uploader(
    "Upload CSV",
    type=["csv"]
)

if uploaded_file is not None:

    df = pd.read_csv(uploaded_file)

    metadata = summarize_dataframe(df)

    st.success(
        f"Dataset loaded successfully ({len(df)} rows)"
    )

    with st.expander("Dataset Preview"):

        st.dataframe(df.head())

    question = st.text_input(
        "Ask a question about your data"
    )

    if st.button("Analyze"):

        with st.spinner("Running analysis..."):

            result = graph.invoke(
                {
                    "df": df,
                    "question": question,
                    "metadata": metadata,
                    "attempts": 0,
                    # "validation_feedback": "",
                    # "critic_feedback": ""
                }
            )

        # -------------------------
        # Tabs
        # -------------------------

        tab1, tab2, tab3 = st.tabs(
            [
                "Answer",
                "Plan",
                "Generated Code",
                # "Validation"
            ]
        )

        # -------------------------
        # Answer
        # -------------------------

        with tab1:

            st.subheader("Final Answer")

            st.write(
                result["final_answer"]
            )

            execution_result = result[
                "execution_result"
            ]

            if (
                isinstance(execution_result, str)
                and execution_result.endswith(".png")
            ):

                st.image(
                    execution_result,
                    caption="Generated Chart"
                )

        # -------------------------
        # Plan
        # -------------------------

        with tab2:

            with st.expander(
                "Analysis Plan",
                expanded=True
            ):

                for step in result["plan"]:
                    st.markdown(f"- {step}")

        # -------------------------
        # Generated Code
        # -------------------------

        with tab3:

            st.subheader("Generated Python Code")

            st.code(
                result["generated_code"],
                language="python"
            )

        # -------------------------
        # Validation
        # -------------------------

        # with tab4:

        #     st.subheader("Validation Status")

        #     st.write(
        #         f"Passed: {result['validation_passed']}"
        #     )

        #     st.write(
        #         result["validation_feedback"]
        #     )