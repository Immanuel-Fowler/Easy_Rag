import streamlit as st

feature_explanations = {
    "Overview": """
**Easy_Rag** is a system for document-based question answering using retrieval-augmented generation. 
""",
    "Document Upload & Ingestion": """
**Purpose:** Upload and process documents (PDF, DOCX, TXT, etc.).

**How it works:**
- Upload files via the web interface.
- The system extracts text from each document.
- Text is prepared for chunking and further processing.
""",
    "Text Chunking": """
**Purpose:** Split documents into smaller, overlapping text chunks.

**How it works:**
- Text is divided into segments of a set size.
- Overlap preserves context between chunks.
- Chunks are sent to the embedding system.
""",
    "Embedding Generation": """
**Purpose:** Convert text chunks into numerical vectors (embeddings).

**How it works:**
- Each chunk is processed by a language model.
- The model outputs a vector for each chunk.
- Embeddings are stored for retrieval.
""",
    "Vector Database": """
**Purpose:** Store and search embeddings efficiently.

**How it works:**
- Embeddings are indexed in a vector database (e.g., FAISS, ChromaDB).
- User queries are embedded and compared to stored vectors.
- Most similar chunks are retrieved for answering.
""",
    "Question Answering": """
**Purpose:** Answer user questions using relevant document chunks.

**How it works:**
- User submits a question.
- Relevant chunks are retrieved from the database.
- Chunks and question are sent to a language model.
- The model generates an answer using the context.
""",
    "Settings & Configuration": """
**Purpose:** Customize system parameters.

**How it works:**
- Adjust chunk size, overlap, model, and database options.
- Settings affect how documents are processed and retrieved.
""",
    "Security & Privacy": """
**Purpose:** Protect user data.

**How it works:**
- Documents processed locally or securely.
- Data retention and access controls can be configured.
"""
}

st.title("Easy_Rag Feature Explanations")

for feature, explanation in feature_explanations.items():
    st.header(feature)
    st.markdown(explanation)