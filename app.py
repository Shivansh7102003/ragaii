import os
from groq import Groq
from dotenv import load_dotenv
from webcrawler import process_website
from langchain_groq import ChatGroq

from langchain_core.messages import HumanMessage, AIMessage
from langchain_community.callbacks.streamlit import StreamlitCallbackHandler
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_classic.chains import create_history_aware_retriever
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain

# Load environment variables
load_dotenv()

# Default settings
DEFAULT_CHUNK_SIZE = 1000
DEFAULT_CHUNK_OVERLAP = 100
DEFAULT_K_VALUE = 5
DEFAULT_TEMPERATURE = 0.5
DEFAULT_MAX_TOKENS = 500


# Initialize LLM
def init_llm(model_name, temperature=DEFAULT_TEMPERATURE, max_tokens=DEFAULT_MAX_TOKENS):
    return ChatGroq(
        api_key=os.environ["API_KEY"],
        model_name=model_name,
        temperature=temperature,
        max_tokens=max_tokens
    )

# Create RAG chain
def create_rag_chain(llm, retriever):
    # Create contextualize question prompt
    contextualize_q_system_prompt = (
        "Given a chat history and the latest user question "
        "which might reference context in the chat history, "
        "formulate a standalone question which can be understood "
        "without the chat history. Do NOT answer the question, just "
        "reformulate it if needed and otherwise return it as is."
    )
    contextualize_q_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
        ]
    )
    
    # Create history aware retriever
    history_aware_retriever = create_history_aware_retriever(
        llm, retriever, contextualize_q_prompt
    )
    
    # Create QA prompt
    qa_system_prompt = (
        "You are an assistant for question-answering tasks about the provided PDF document. "
        "Use the following pieces of retrieved context to answer the question. "
        "If you don't know the answer, just say that you don't know. "
        "Keep your answers conversational and helpful."
    )
    
    qa_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", qa_system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="context"),
        ]
    )
    
    # Create the document chain
    document_chain = create_stuff_documents_chain(llm, qa_prompt)
    
    # Create the history-aware retrieval chain
    retrieval_chain = create_retrieval_chain(
        history_aware_retriever,
        document_chain,
    )
    
    return retrieval_chain, history_aware_retriever

# Function to generate a response to a user query
def generate_response(prompt, llm, retriever, chat_history):
    try:
        # First, try to understand if this is a follow-up question
        contextualized_message = llm.invoke(
            f"Given this chat history: {str(chat_history)}\n\n"
            f"And this follow-up question: {prompt}\n\n"
            f"Rewrite the follow-up question to be a standalone question that captures all context needed. "
            f"If it's already a standalone question, return it unchanged."
        )
        
        # Extract the string content from the AIMessage
        contextualized_query = contextualized_message.content if hasattr(contextualized_message, 'content') else str(contextualized_message)
        
        # Then retrieve relevant documents
        docs = retriever.invoke(contextualized_query)
        
        # Create context from documents
        context = "\n\n".join([doc.page_content for doc in docs])
        
        # Check if context is empty or too short
        if not context or len(context.strip()) < 20:
            return "The answer is not available on the provided website.", context
        
        # First, check if the retrieved context is relevant to the question
        relevance_check = llm.invoke(
            f"Question: {contextualized_query}\n\n"
            f"Retrieved Context:\n{context}\n\n"
            f"Does the above context contain information that can answer the question? "
            f"Respond with ONLY 'YES' or 'NO'. Do not provide any explanation."
        ).content.strip().upper()
        
        # If context is not relevant, return the exact message
        if relevance_check == "NO" or "NO" in relevance_check[:5]:
            return "The answer is not available on the provided website.", context
        
        # Generate response with history and context
        history_str = "\n".join([f"Human: {m.content}" if isinstance(m, HumanMessage) else f"AI: {m.content}" for m in chat_history])
        
        # Enhanced prompt to ensure answer is grounded in context
        response = llm.invoke(
            f"You are a helpful assistant that answers questions STRICTLY based on the provided context. "
            f"If the context does not contain enough information to answer the question, you MUST respond with EXACTLY: "
            f"'The answer is not available on the provided website.'\n\n"
            f"Chat history:\n{history_str}\n\n"
            f"Context from website:\n{context}\n\n"
            f"Human: {prompt}\n"
            f"AI: "
        ).content
        
        # Double-check: if response indicates uncertainty or lack of information
        uncertainty_phrases = [
            "i don't know",
            "i'm not sure",
            "cannot find",
            "not mentioned",
            "doesn't say",
            "no information",
            "not specified",
            "unclear"
        ]
        
        response_lower = response.lower()
        if any(phrase in response_lower for phrase in uncertainty_phrases):
            return "The answer is not available on the provided website.", context
        
        return response, context
        
    except Exception as e:
        return f"An error occurred: {str(e)}", ""
