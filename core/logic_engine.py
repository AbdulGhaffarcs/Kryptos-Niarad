from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

llm = ChatOllama(model="llama3.2", temperature=0)

def route_query(query):
    """Determines if the user wants data extraction or a concept summary."""
    router_prompt = (
        "Classify the query into 'EXTRACTION' (dates, venues, tables, specific facts) "
        "or 'SUMMARY' (concepts, overviews, lecture explanations). "
        f"Query: {query}\nReply with one word only."
    )
    response = llm.invoke(router_prompt).content.upper()
    return "EXTRACTION" if "EXTRACTION" in response else "SUMMARY"

def get_rag_chain(retriever, mode):
    """Builds the final chain with mode-specific instructions."""
    
    if mode == "EXTRACTION":
        instructions = "You are an admin assistant. Extract specific data points. Use a Markdown table for schedules."
    else:
        instructions = "You are a tutor. Summarize the content using clear bullet points and educational tone."

    template = f"""
    {instructions}
    
    Context: {{context}}
    Question: {{question}}
    
    Answer:
    """
    
    prompt = ChatPromptTemplate.from_template(template)
    
    return (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )