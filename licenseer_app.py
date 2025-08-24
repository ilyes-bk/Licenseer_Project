import streamlit as st
import os
import time
from license_compatibility_llm import LicenseCompatibilityLLM
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="LICENSEER - Open Source License Compatibility Checker",
    page_icon="🔍",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Custom CSS for prettier UI
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #4CAF50;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #555;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: row;
        align-items: flex-start;
        gap: 0.5rem;
    }
    .chat-message-content {
        flex-grow: 1;
        color: #000;
    }
    .user-message {
        background-color: #E8F5E9;
        border-left: 5px solid #4CAF50;
    }
    .bot-message {
        background-color: #F5F5F5;
        border-left: 5px solid #2196F3;
    }
    .user-avatar {
        font-size: 1.5rem;
    }
    .bot-avatar {
        font-size: 1.5rem;
        color: #2196F3;
    }
    .input-area {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f9f9f9;
        margin-top: 2rem;
    }
    .stTextInput>div>div>input {
        border-radius: 0.5rem;
    }
    .disclaimer {
        font-size: 0.8rem;
        color: #777;
        margin-top: 2rem;
        padding: 0.5rem;
        background-color: #f5f5f5;
        border-radius: 0.3rem;
    }
    .stButton button {
        background-color: #4CAF50;
        color: white;
        border-radius: 0.5rem;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    .license-info {
        border: 1px solid #ddd;
        border-radius: 0.5rem;
        padding: 1rem;
        margin-top: 1rem;
        background-color: #f9f9f9;
    }
    .blinking-cursor {
        display: inline-block;
        width: 10px;
        height: 20px;
        margin-left: 5px;
        background: #2196F3;
        animation: blink 1s infinite;
    }
    @keyframes blink {
        0% { opacity: 1; }
        50% { opacity: 0; }
        100% { opacity: 1; }
    }
</style>
""", unsafe_allow_html=True)

# Initialize LicenseCompatibilityLLM
@st.cache_resource
def load_license_compatibility_llm():
    try:
        return LicenseCompatibilityLLM()
    except Exception as e:
        st.error(f"Error initializing license compatibility checker: {e}")
        st.info("If this is a first run, the vector database will be built from src/data/licenses. Ensure those JSON files exist.")
        return None

llm = load_license_compatibility_llm()

# Header
st.markdown('<div class="main-header">🔍 LICENSEER</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Open Source License Compatibility Checker with RAG</div>', unsafe_allow_html=True)

# Initialize chat history if it doesn't exist
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages
for message in st.session_state.messages:
    avatar = "👤" if message["role"] == "user" else "🤖"
    avatar_class = "user-avatar" if message["role"] == "user" else "bot-avatar"
    message_class = "user-message" if message["role"] == "user" else "bot-message"
    
    st.markdown(f"""
    <div class="chat-message {message_class}">
        <div class="{avatar_class}">{avatar}</div>
        <div class="chat-message-content">{message["content"]}</div>
    </div>
    """, unsafe_allow_html=True)

# Input area
st.markdown('<div class="input-area">', unsafe_allow_html=True)

# Description
st.markdown("""
Ask me about the compatibility between two open source packages:
- "Are requests and urllib3 compatible?"
- "Can I use django with celery?"
- "Check compatibility between pandas and numpy"
""")

# User input
user_input = st.text_input("Your question:", key="user_input", placeholder="Type your question here...")

# Submit button
submit_button = st.button("Check Compatibility")

# Process input
if submit_button and user_input:
    if llm is None:
        st.error("License compatibility checker is not initialized. Please check your configuration.")
    else:
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Display user message
        st.markdown(f"""
        <div class="chat-message user-message">
            <div class="user-avatar">👤</div>
            <div class="chat-message-content">{user_input}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Display "thinking" message
        thinking_placeholder = st.empty()
        thinking_placeholder.markdown(f"""
        <div class="chat-message bot-message">
            <div class="bot-avatar">🤖</div>
            <div class="chat-message-content">Analyzing licenses and compatibility... <span class="blinking-cursor"></span></div>
        </div>
        """, unsafe_allow_html=True)
        
        try:
            # Process query
            response = llm.process_query(user_input)
            
            # Remove thinking message
            thinking_placeholder.empty()
            
            # Add bot message to chat
            st.session_state.messages.append({"role": "assistant", "content": response})
            
            # Display bot response
            st.markdown(f"""
            <div class="chat-message bot-message">
                <div class="bot-avatar">🤖</div>
                <div class="chat-message-content">{response}</div>
            </div>
            """, unsafe_allow_html=True)
            
        except Exception as e:
            # Remove thinking message
            thinking_placeholder.empty()
            
            # Display error message
            error_message = f"Sorry, I encountered an error: {str(e)}"
            st.session_state.messages.append({"role": "assistant", "content": error_message})
            
            st.markdown(f"""
            <div class="chat-message bot-message">
                <div class="bot-avatar">🤖</div>
                <div class="chat-message-content">{error_message}</div>
            </div>
            """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title("About LICENSEER")
    st.markdown("""
    **LICENSEER** is an AI-powered tool that helps developers understand license compatibility between open-source packages.
    
    ### Features:
    - 📋 License identification for packages
    - 🔄 Compatibility checking
    - 🧠 RAG-enhanced explanations
    - 💼 Detailed license information
    
    ### How it works:
    1. We extract package names from your query
    2. We identify licenses for each package
    3. We check compatibility between licenses
    4. RAG system provides context from license texts
    5. LLM generates a comprehensive response
    """)
    
    st.markdown("---")
    
    # Clear chat button
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.experimental_rerun()

    # Credits
    st.markdown("---")
    st.markdown("### Credits")
    st.markdown("Powered by:")
    st.markdown("- OpenAI GPT-4")
    st.markdown("- LangChain RAG")
    st.markdown("- Neo4j Graph Database")
    st.markdown("- SPDX License Data")
    
# Footer disclaimer
st.markdown("""
<div class="disclaimer">
    <strong>Disclaimer:</strong> This tool provides general guidance on license compatibility based on available data and AI analysis. 
    It does not constitute legal advice. Always consult with a legal professional for specific licensing questions.
</div>
""", unsafe_allow_html=True) 