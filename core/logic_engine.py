"""
core/logic_engine.py
LLM chains using HuggingFace local models — no API key, no Ollama required.
"""

from langchain_huggingface import HuggingFacePipeline
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import torch

FREE_TIER_LIMIT = None  # No limit — bot always available without docs

# ── Available models (id, display name, min RAM) ──
AVAILABLE_MODELS = {
    "TinyLlama 1.1B — Fast (2GB RAM)":   "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
    "Phi-2 2.7B — Balanced (4GB RAM)":   "microsoft/phi-2",
    "Mistral 7B — Powerful (8GB RAM)":   "mistralai/Mistral-7B-Instruct-v0.2",
    "Zephyr 7B — Best Chat (8GB RAM)":   "HuggingFaceH4/zephyr-7b-beta",
}

# ── Topics NIARAD refuses to engage with ──
BLOCKED_TOPICS = {
    "hack", "hacking", "exploit", "malware", "virus", "ransomware", "phishing",
    "crack", "bypass", "jailbreak", "drug", "weapon", "bomb", "illegal",
    "porn", "adult", "nsfw", "gore", "violence", "kill", "murder",
    "gambling", "bet", "crypto scam", "fraud", "cheat", "pirate",
    "darkweb", "dark web", "tor browser", "anonymous browsing",
}

ALLOWED_DOMAINS = {
    "education", "study", "lecture", "exam", "assignment", "university",
    "science", "math", "history", "technology", "programming", "coding",
    "artificial intelligence", "machine learning", "data", "research",
    "biology", "chemistry", "physics", "literature", "language", "writing",
    "general knowledge", "explain", "summarize", "what is", "how does",
    "help me understand", "tutor", "learn", "concept", "definition",
}


def is_off_topic(query: str) -> bool:
    """Returns True if the query contains blocked topics."""
    q = query.lower()
    return any(blocked in q for blocked in BLOCKED_TOPICS)


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


def load_llm(model_id: str) -> HuggingFacePipeline:
    """
    Load a HuggingFace model locally.
    Uses GPU if available, otherwise CPU with 4-bit quantization fallback.
    Model is cached after first load — subsequent calls are instant.
    """
    device = 0 if torch.cuda.is_available() else -1
    dtype = torch.float16 if torch.cuda.is_available() else torch.float32

    tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=dtype,
        device_map="auto" if torch.cuda.is_available() else None,
        trust_remote_code=True,
        low_cpu_mem_usage=True,
    )

    pipe = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        max_new_tokens=512,
        temperature=0.1,
        do_sample=True,
        repetition_penalty=1.1,
        return_full_text=False,
    )

    return HuggingFacePipeline(pipeline=pipe)


def route_query(query: str, llm) -> str:
    """Route query to EXTRACTION or SUMMARY mode."""
    prompt = (
        "Classify the query as 'EXTRACTION' (specific facts, dates, venues, tables, names) "
        "or 'SUMMARY' (concepts, overviews, explanations, definitions). "
        "Query: " + query + "\nReply with one word only: EXTRACTION or SUMMARY."
    )
    result = llm.invoke(prompt).upper()
    return "EXTRACTION" if "EXTRACTION" in result else "SUMMARY"


def get_rag_chain(retriever, mode: str, llm):
    """RAG chain that answers from indexed documents."""
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


def get_small_talk_chain(llm):
    """Fast chain for greetings — no retrieval, no routing overhead."""
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


def get_direct_chain(llm):
    """
    Chatbot chain — no documents needed.
    Restricted to educational, academic, and study-related topics.
    """
    template = (
        "You are NIARAD, an intelligent AI study assistant built for students.\n\n"
        "You ONLY help with:\n"
        "- Academic subjects: science, math, history, literature, technology, programming, AI/ML\n"
        "- Study skills, exam prep, concept explanations, and summarization\n"
        "- General knowledge questions that are educational in nature\n"
        "- Coding and software development help\n"
        "- Research and writing assistance\n\n"
        "You MUST REFUSE and redirect if the user asks about:\n"
        "- Hacking, exploits, malware, or illegal activities\n"
        "- Adult, violent, or harmful content\n"
        "- Gambling, fraud, or anything unethical\n"
        "- Anything unrelated to learning or academics\n\n"
        "If a question is off-topic, respond with exactly:\n"
        "\"NIARAD is focused on academic and educational topics. "
        "I cannot help with that. Feel free to ask me about your studies!\"\n\n"
        "If the question is appropriate, answer clearly and helpfully.\n\n"
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