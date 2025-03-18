import os

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

if os.getenv("OPENAI_API_KEY"):
    model = "gpt-4o-2024-08-06"
    cypher_generation_llm = ChatOpenAI(
        model=model,
        temperature=0.0
    )
    schema_validation_llm = ChatOpenAI(
        model=model,
        temperature=0.0
    )
    final_answer_generation_llm = ChatOpenAI(
        model=model,
        temperature=0.0
    )
    answer_judgment_llm = ChatOpenAI(
        model=model,
        temperature=0.0
    )
    character_summary_llm = ChatOpenAI(
        model=model,
        temperature=0.0
    )


else:
    model = "gemini-2.0-flash-lite"
    cypher_generation_llm = ChatGoogleGenerativeAI(
        model=model,
        temperature=0.0,
    )

    schema_validation_llm = ChatGoogleGenerativeAI(
        model=model,
        temperature=0.0
    )

    final_answer_generation_llm = ChatGoogleGenerativeAI(
        model=model,
        temperature=0.0
    )

    answer_judgment_llm = ChatGoogleGenerativeAI(
        model=model,
        temperature=0.0
    )

    character_summary_llm = ChatGoogleGenerativeAI(
        model=model,
        temperature=0.0
    )
