from langchain_groq import ChatGroq
from app.configuration import settings

llm = ChatGroq(
    api_key=settings.groq_api_key,
    model=settings.model_name,
    temperature=0
)