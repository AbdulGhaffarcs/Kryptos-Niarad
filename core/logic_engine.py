"""
core/logic_engine.py
LLM chains for RAG and direct conversation modes.
"""

from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

llm = ChatOllama(model="llama3.2", temperature=0)

FREE_TIER_LIMIT = 10

SMALL_TALK_TRIGGERS = {
    "hi", "hello", "hey", "sup", "yo", "greetings", "howdy",
    "good morning", "good evening", "good afternoon", "good night",
    "how are you", "what's up", "whats up", "who are you",
    "what can you do", "help", "thanks", "thank you", "bye", "goodbye"
}


def is_small_talk(query: str) -> bool:
    """Detect greetings and small talk to skip the routing LLM call."""
    q = query.strip().lower().rstrip("!?.").strip()
    return q in SMALL_TALK_TRIGGERS or (len(q.split()) <= 3 and any(t in q for t in SMALL_TALK_TRIGGERS))


def route_query(query: str) -> str:
    """Route query to EXTRACTION or SUMMARY mode using LLM."""
    prompt = (
        "Classify the query as 'EXTRACTION' (specific facts, dates, venues, tables, names) "
        "or 'SUMMARY' (concepts, overviews, explanations, definitions). "
        f"Query: {query}\nReply with one word only: EXTRACTION or SUMMARY."
    )
    result = llm.invoke(prompt).content.upper()
    return "EXTRACTION" if "EXTRACTION" in result else "SUMMARY"


def get_rag_chain(retriever, mode: str):
    """RAG chain that answers from indexed documents."""
    if mode == "EXTRACTION":
        instructions = (
            "You are a precise admin assistant. Extract specific facts, dates, venues, and data. "
            "Use Markdown tables for structured data like schedules or timetables. "
            "Be direct and concise."
        )
    else:
        instructions = (
            "You are an expert tutor. Explain concepts clearly using bullet points, "
            "examples, and a clear educational tone. Be thorough but focused."
        )

    prompt = ChatPromptTemplate.from_template(f"""
{instructions}

Use ONLY the provided context to answer. If the answer is not clearly in the context, say so.

Context:
{{context}}

Question: {{question}}

Answer:""")

    return (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )


def get_small_talk_chain():
    """Fast chain for greetings — no retrieval, no routing overhead."""
    prompt = ChatPromptTemplate.from_template("""You are NIARAD, a sharp and concise AI assistant.
Respond to this greeting or small talk briefly in 1-2 sentences.
You may mention you're ready to help analyze documents or answer questions.

Message: {question}
Response:""")

    return (
        {"question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )


def get_direct_chain():
    """Free-tier chain: general conversation without document context."""
    prompt = ChatPromptTemplate.from_template("""You are NIARAD, an intelligent offline AI assistant.

Rules:
- Answer general knowledge questions clearly and concisely (max 3 paragraphs).
- If the question requires specific documents or personal study material,
  tell the user to upload files via the sidebar for document-aware answers.
- Never fabricate specific facts you don't know.

Question: {question}

Answer:""")

    return (
        {"question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )