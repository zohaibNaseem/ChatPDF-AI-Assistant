import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq  # Updated import
from langchain.chains import ConversationalRetrievalChain
from langchain_community.vectorstores import FAISS  # Updated import
from langchain_huggingface import HuggingFaceEmbeddings  # Updated import
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyMuPDFLoader  # Updated import
from langchain.memory import ConversationBufferMemory

# Load environment variables
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

def process_pdf(pdf_path):
    """Process PDF and create vector database"""
    try:
        # Load PDF
        loader = PyMuPDFLoader(pdf_path)
        docs = loader.load()
        
        if not docs:
            raise ValueError("No content found in PDF")
        
        # Split documents
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100
        )
        chunks = splitter.split_documents(docs)
        
        # Create embeddings
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        
        # Create vector database
        vectordb = FAISS.from_documents(chunks, embedding=embeddings)
        
        return vectordb
        
    except Exception as e:
        raise Exception(f"Error processing PDF: {str(e)}")

def get_qa_chain(vectordb):
    """Create QA chain with conversation memory"""
    try:
        if not groq_api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        
        # Initialize LLM
        llm = ChatGroq(
            model="llama3-70b-8192",
            groq_api_key=groq_api_key,
            temperature=0.1
        )
        
        # Create memory
        memory = ConversationBufferMemory(
            memory_key="chat_history", 
            return_messages=True,
            output_key="answer"
        )
        
        # Create QA chain
        qa_chain = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=vectordb.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 3}
            ),
            memory=memory,
            verbose=True,
            return_source_documents=True
        )
        
        return qa_chain
        
    except Exception as e:
        raise Exception(f"Error creating QA chain: {str(e)}")