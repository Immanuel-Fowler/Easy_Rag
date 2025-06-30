import streamlit as st
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_ollama import ChatOllama
import os
import chromadb
from streamlit_option_menu import option_menu
import json

def get_collection_embedding_map(db_path):
    mapping_path = os.path.join(db_path, 'collection_embedding_map.json')
    if os.path.exists(mapping_path):
        with open(mapping_path, 'r') as f:
            return json.load(f)
    return {}

st.set_page_config(page_title="Chatbot", layout="wide", initial_sidebar_state="collapsed")

if st.button("❓ Help", help="Go to help page"):
    st.switch_page("pages/Help.py")
    
# Sidebar for database/collection selection
with st.expander("**Chatbot Parameters**"):
    #st.title("🔎 RAG Chatbot")
    Databases = []
    for entry in os.listdir('./'):
        full_path = os.path.join('./', entry)
        if os.path.isdir(full_path) and 'data_' in entry:
            Databases.append(entry)

    chosen_database = st.selectbox(
        "Select database",
        Databases,
        index=None,
        placeholder="data_xxxx_xxxx...",
    )

    if chosen_database is not None:
        client = chromadb.PersistentClient(path=f'./{chosen_database}')
        collection_embedding_map = get_collection_embedding_map(f'./{chosen_database}')
        collections = [col.name for col in client.list_collections()]
    else:
        client = None
        embedding_function = None
        collections = []

    chosen_collection = st.selectbox(
        "Select collection",
        collections,
        index=None,
        placeholder="xxxx...",
    )

    if chosen_collection is not None:
        embedding_function = OllamaEmbeddings(model=collection_embedding_map.get(chosen_collection))

    mmr_sst_topk = option_menu(
        "RAG search type",
        ["similarity score", "mmr", "top k"],
        icons=["1-square-fill", "2-square-fill", "3-square-fill"],
        menu_icon="search",
        default_index=1,
        orientation="horizontal",
    )

    if mmr_sst_topk == "similarity score":
        search_number_input = st.number_input(
            "Similarity score threshold",
            min_value=0.00,
            max_value=100.00,
            value=0.0,
            step=0.25,
            help="Minimum similarity score of the retrieved results",
            format="%.2f"
        )
    elif mmr_sst_topk == "top k":
        search_number_input = st.number_input(
            "Number of top results",
            min_value=1,
            max_value=100,
            value=3,
            step=1,
            help="Number of top results to retrieve",
        )
    else:
        search_number_input = None

st.title("💬 Chatbot")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history using st.chat_message
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input at the bottom
if prompt := st.chat_input("Ask me anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Only respond if database and collection are selected
    if chosen_database and chosen_collection:
        with st.chat_message("assistant"):
            with st.spinner("Bot is typing..."):
                # RAG retrieval
                vector_store = Chroma(
                    persist_directory=f'./{chosen_database}',
                    embedding_function=embedding_function,
                    collection_name=f'{chosen_collection}'
                )
                if mmr_sst_topk == "similarity score":
                    retriever = vector_store.as_retriever(
                        search_type="similarity_score_threshold",
                        search_kwargs={"score_threshold": float(search_number_input)}
                    )
                elif mmr_sst_topk == "mmr":
                    retriever = vector_store.as_retriever(search_type="mmr")
                elif mmr_sst_topk == "top k":
                    retriever = vector_store.as_retriever(search_kwargs={"k": search_number_input})
                else:
                    retriever = None

                PROMPT_TEMPLATE = """
                Answer the question based only on the following context:

                {context}

                ---

                Answer the question based on the above context: {question}
                """

                if retriever:
                    results = retriever.invoke(prompt)
                    if not results:
                        bot_response = "Sorry, I couldn't find any relevant information."
                    else:
                        context_text = "\n\n---\n\n".join([r.page_content for r in results])
                        prompt_text = PROMPT_TEMPLATE.format(context=context_text, question=prompt)
                        model = ChatOllama(model="llama3.1")
                        # Streaming not supported, so just show the response
                        bot_response = model.invoke(prompt_text).content
                else:
                    bot_response = "Sorry, something went wrong with the retrieval."
                st.markdown(bot_response)
        st.session_state.messages.append({"role": "assistant", "content": bot_response})
    else:
        with st.chat_message("assistant"):
            st.markdown("Please select a database and collection to start chatting.")
        st.session_state.messages.append({"role": "assistant", "content": "Please select a database and collection to start chatting."})

if prompt is not None:
    with st.expander("View Full Prompt"):
        st.write(prompt_text)