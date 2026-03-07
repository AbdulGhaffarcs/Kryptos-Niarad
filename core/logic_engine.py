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
    q = query.strip().lower().rstrip("!?.").strip()
    return q in SMALL_TALK_TRIGGERS or (
        len(q.split()) <= 3 and any(t in q for t in SMALL_TALK_TRIGGERS)
    )


def route_query(query: str) -> str:
    prompt = (
        "Classify the query as 'EXTRACTION' (specific facts, dates, venues, tables, names) "
        "or 'SUMMARY' (concepts, overviews, explanations, definitions). "
        "Query: " + query + "\nReply with one word only: EXTRACTION or SUMMARY."
    )
    result = llm.invoke(prompt).content.upper()
    return "EXTRACTION" if "EXTRACTION" in result else "SUMMARY"


def get_rag_chain(retriever, mode: str):
    if mode == "EXTRACTION":
        instructions = (
            "You are a precise admin assistant. "
            "Extract specific facts, dates, venues, and data. "
            "Use Markdown tables for structured data like schedules. "
            "Be direct and concise."
        )
    else:
        instructions = (
            "You are an expert tutor. "
            "Explain concepts clearly using bullet points and examples. "
            "Be thorough but focused."
        )

    template = (
        instructions + "\n\n"
        "Use ONLY the provided context to answer. "
        "If the answer is not in the context, say so.\n\n"
        "Context:\n{context}\n\n"
        "Question: {question}\n\n"
        "Answer:"
    )

    prompt = ChatPromptTemplate.from_template(template)

    return (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )


def get_small_talk_chain():
    template = (
        "You are NIARAD, a sharp and concise AI assistant.\n"
        "Respond to this greeting or small talk briefly in 1-2 sentences.\n"
        "You may mention you are ready to help analyze documents or answer questions.\n\n"
        "Message: {question}\n"
        "Response:"
    )

    prompt = ChatPromptTemplate.from_template(template)

    return (
        {"question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )


def get_direct_chain():
    template = (
        "You are NIARAD, an intelligent offline AI assistant.\n\n"
        "Rules:\n"
        "- Answer general knowledge questions clearly and concisely (max 3 paragraphs).\n"
        "- If the question requires specific documents or personal study material, "
        "tell the user to upload files via the sidebar for document-aware answers.\n"
        "- Never fabricate specific facts you do not know.\n\n"
        "Question: {question}\n\n"
        "Answer:"
    )

    prompt = ChatPromptTemplate.from_template(template)

    return (
        {"question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )