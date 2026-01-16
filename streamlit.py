import streamlit as st
from app import init_llm, create_rag_chain, generate_response
from webcrawler import process_website
from langchain_core.messages import HumanMessage, AIMessage

# Set page config
st.set_page_config(
    page_title="Website Q&A System",
    page_icon="🌐",
    layout="wide"
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "db" not in st.session_state:
    st.session_state.db = None

if "retriever" not in st.session_state:
    st.session_state.retriever = None

if "llm" not in st.session_state:
    st.session_state.llm = None

if "website_metadata" not in st.session_state:
    st.session_state.website_metadata = None

# Create a sidebar for configuration and URL input
with st.sidebar:
    st.title("🌐 Website Q&A System")
    
    # URL input
    website_url = st.text_input(
        "Enter Website URL",
        placeholder="https://example.com",
        help="Enter a valid website URL to index and ask questions about"
    )
    
    # Force re-index option
    force_reindex = st.checkbox(
        "Force re-index",
        value=False,
        help="Re-crawl the website even if it's already indexed"
    )
    
    # Model selection
    model_name = st.selectbox(
        "Select a model",
        options=[
            "llama-3.1-8b-instant",
            "llama-3.3-70b-versatile",
            "meta-llama/llama-4-maverick-17b-128e-instruct",
            "openai/gpt-oss-safeguard-20b"
        ],
        index=0
    )
    
    # Process button
    process_button = st.button("🔍 Index Website")
    
    # Restart button
    restart_button = st.button("🔄 Restart Chat")
    
    # Display indexed website info
    if st.session_state.website_metadata:
        st.divider()
        st.subheader("Indexed Website")
        st.write(f"**Title:** {st.session_state.website_metadata.get('title', 'N/A')}")
        st.write(f"**URL:** {st.session_state.website_metadata.get('url', 'N/A')}")

# Handle restart
if restart_button:
    st.session_state.messages = []
    st.session_state.chat_history = []
    st.rerun()

# Process website if requested
if website_url and process_button:
    with st.spinner("🌐 Crawling and indexing website..."):
        # Process the website
        result = process_website(
            url=website_url,
            force_reindex=force_reindex
        )
        
        if result['success']:
            st.session_state.db = result['db']
            st.session_state.retriever = result['retriever']
            st.session_state.website_metadata = result['metadata']
            
            # Initialize LLM
            st.session_state.llm = init_llm(model_name)
            
            if result['was_cached']:
                st.success(f"✅ Loaded cached index for: {result['metadata'].get('title', website_url)}")
            else:
                st.success(f"✅ Website indexed successfully! You can now ask questions about: {result['metadata'].get('title', website_url)}")
        else:
            st.error(f"❌ Failed to process website: {result['error']}")

# Display chat interface in the main area
st.title("🌐 Website Chat Assistant")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Create a chat input
if prompt := st.chat_input("Ask a question about your document"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.write(prompt)
    
    # Check if website has been indexed
    if st.session_state.db is None:
        with st.chat_message("assistant"):
            st.write("Please enter a website URL and click 'Index Website' first.")
        st.session_state.messages.append({"role": "assistant", "content": "Please enter a website URL and click 'Index Website' first."})
    else:
        # Display assistant response
        with st.chat_message("assistant"):
            # Create a placeholder for streaming output
            message_placeholder = st.empty()
            
            # Generate response
            response, context = generate_response(
                prompt, 
                st.session_state.llm, 
                st.session_state.retriever, 
                st.session_state.chat_history
            )
            
            # Show context if available
            if context:
                with st.expander("View retrieved context"):
                    st.write(context)
            
            # Display response
            message_placeholder.markdown(response)
            
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": response})
            
            # Update chat history for context
            st.session_state.chat_history.append(HumanMessage(content=prompt))
            st.session_state.chat_history.append(AIMessage(content=response))

# Add a footer
st.markdown("---")
st.markdown("Website Q&A Application | Built with Streamlit, LangChain, and Groq")
