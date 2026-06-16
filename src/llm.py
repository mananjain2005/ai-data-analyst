from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()


def get_llm():
    """
    Returns configured Groq LLM.
    """

    llm = ChatGroq(
        # model="llama-3.3-70b-versatile",
        model="llama-3.1-8b-instant"
        temperature=0
    )

    return llm