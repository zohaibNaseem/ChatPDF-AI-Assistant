import streamlit as st
import tempfile
import os
import datetime
from pdf_chat import process_pdf, get_qa_chain

# Page config with clean design
st.set_page_config(
    page_title="AI Assistant", 
    page_icon="🤖",
    layout="wide"
)

# Custom CSS for GPT-like appearance
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
    }
    
    .greeting {
        font-size: 2.5rem;
        font-weight: 300;
        margin-bottom: 0.5rem;
    }
    
    .subheading {
        font-size: 1.2rem;
        opacity: 0.9;
        font-weight: 300;
    }
    
    .upload-section {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        border: 2px dashed #dee2e6;
    }
    
    .stChatMessage {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .chat-container {
        max-width: 800px;
        margin: 0 auto;
    }
</style>
""", unsafe_allow_html=True)

# Get current time for greeting
current_hour = datetime.datetime.now().hour
if 5 <= current_hour < 12:
    greeting = "Good Morning"
elif 12 <= current_hour < 17:
    greeting = "Good Afternoon"
else:
    greeting = "Good Evening"

# Main header
st.markdown(f"""
<div class="main-header">
    <div class="greeting">{greeting} 👋</div>
    <div class="subheading">How can I help you today?</div>
</div>
""", unsafe_allow_html=True)

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
    st.session_state.qa_chain = None
    st.session_state.pdf_processed = False
    st.session_state.pdf_name = None

# Check for API key
if not os.getenv("GROQ_API_KEY"):
    st.error("⚠️ API key not configured. Please contact administrator.")
    st.stop()

# File upload section
with st.container():
    st.markdown('<div class="upload-section">', unsafe_allow_html=True)
    
    if not st.session_state.pdf_processed:
        st.markdown("### 📄 Upload a document to get started")
        pdf = st.file_uploader("", type="pdf", label_visibility="collapsed")
        
        if pdf:
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    tmp.write(pdf.read())
                    tmp_path = tmp.name
                
                with st.spinner("Reading your document..."):
                    vectordb = process_pdf(tmp_path)
                    qa_chain = get_qa_chain(vectordb)
                    st.session_state.qa_chain = qa_chain
                    st.session_state.pdf_processed = True
                    st.session_state.pdf_name = pdf.name
                
                # Clean up temp file
                os.unlink(tmp_path)
                st.rerun()
                
            except Exception as e:
                st.error(f"Error processing document: {str(e)}")
    else:
        st.success(f"✅ Document '{st.session_state.pdf_name}' is ready!")
        if st.button("Upload New Document", type="secondary"):
            st.session_state.pdf_processed = False
            st.session_state.qa_chain = None
            st.session_state.chat_history = []
            st.session_state.pdf_name = None
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# Chat interface
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

# Display chat history
for i, (role, msg) in enumerate(st.session_state.chat_history):
    if role == "You":
        with st.chat_message("user"):
            st.markdown(msg)
    else:
        with st.chat_message("assistant"):
            st.markdown(msg)

# Chat input
if st.session_state.pdf_processed:
    prompt = st.chat_input("Ask me anything about your document...")
    
    if prompt:
        try:
            # Add user message
            st.session_state.chat_history.append(("You", prompt))
            
            # Display user message
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Get AI response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    result = st.session_state.qa_chain({"question": prompt})
                    response = result["answer"]
                
                st.markdown(response)
            
            # Add bot response to history
            st.session_state.chat_history.append(("AI Assistant", response))
            
        except Exception as e:
            st.error(f"Something went wrong: {str(e)}")
else:
    st.chat_input("Upload a document first to start chatting...", disabled=True)

st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666; font-size: 0.9rem;'>"
    "💡 Upload a PDF document and ask questions about its content"
    "</div>", 
    unsafe_allow_html=True
)