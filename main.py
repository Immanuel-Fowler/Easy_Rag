import streamlit as st
import os
import chromadb
import json
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from streamlit_option_menu import option_menu
from langchain_community.document_loaders import WebBaseLoader, SitemapLoader
import time

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
if st.button("❓ Help", help="Go to help page"):
    st.switch_page("pages/Help.py")

current_dir = os.path.dirname(os.path.abspath(__file__))
Databases = [name for name in os.listdir(current_dir) if os.path.isdir(os.path.join(current_dir, name)) and 'data_' in name]


with st.container():
    with st.form("make_database_form"):
        st.write("Type in the name of the database you want to create")
        database_name = st.text_input("Database name")
        # Embedding model selection removed from database creation
        submitted = st.form_submit_button("Create database")
        if submitted:
            st.write("Creating database...")
            client = chromadb.Client()
            # Use a default embedding model for path, but this is not used for collection anymore
            client =  chromadb.PersistentClient(path=f'./data_{database_name}_default')
            st.success('Database created successfully!')
            st.rerun()

    
    
with st.container(border = True):
    database_option = st.selectbox(
        "Select the database you want to use",
        Databases,
        index=None,
        placeholder="data_xxxx_xxxx...",
    )

# Helper functions for collection-embedding mapping

def get_collection_embedding_map(db_path):
    mapping_path = os.path.join(db_path, 'collection_embedding_map.json')
    if os.path.exists(mapping_path):
        with open(mapping_path, 'r') as f:
            return json.load(f)
    return {}

def save_collection_embedding_map(db_path, mapping):
    mapping_path = os.path.join(db_path, 'collection_embedding_map.json')
    with open(mapping_path, 'w') as f:
        json.dump(mapping, f)

if database_option is not None:
    client = chromadb.PersistentClient(path=f'{database_option}')
    db_path = os.path.abspath(database_option)
    collection_embedding_map = get_collection_embedding_map(db_path)
    invoke_or_update =  option_menu("Choose to invoke or update your database", ["Invoke Database", 'Update Database'], 
    icons=['robot', 'database-add'], menu_icon="clipboard2-check", default_index=1, orientation="horizontal",)

    if invoke_or_update == 'Invoke Database':
        results = []
        # Show embedding model next to collection name
        collection_names = [col.name for col in client.list_collections()]
        collection_labels = [
            f"{name} ({collection_embedding_map.get(name, 'No embedding')})" for name in collection_names
        ]
        collection_option = st.selectbox(
            "Select the collection you want to use",
            options=collection_names,
            format_func=lambda name: f"{name} ({collection_embedding_map.get(name, 'No embedding')})",
            index=None,
            placeholder="xxxx...",
        )

        if collection_option is not None:
            # Get embedding model for this collection
            embedding_model = collection_embedding_map.get(collection_option)
            if not embedding_model:
                st.error("No embedding model found for this collection. Please update the collection to set an embedding model.")
            else:
                with st.form("invoke_database_form"):
                    col1,col2 = st.columns([3,1])

                    with col1:
                        st.write("Type in your query")
                        query = st.text_input("Query")

                    with col2:
                        st.write("Number of results")
                        number_of_results = st.number_input("Number of results or Similarity Score", min_value=0, max_value=100, value=None)
                        search_type = st.selectbox(
                            "Select search type",
                            options=["similarity_score_threshold", "mmr", "top_k"],
                            index=0,
                            help="Choose the search type for your query.",
                        )
                        submitted = st.form_submit_button("Invoke")

                    if submitted:
                        if query:
                            print(f'collection_name = {collection_option}\nembedding_function = {embedding_model}\npersist_directory = {database_option}')
                            vector_store = Chroma(
                                collection_name=collection_option,
                                embedding_function=OllamaEmbeddings(model=embedding_model),
                                persist_directory=f'./{database_option}'
                            )
                            if search_type == "similarity_score_threshold":
                                retriever = vector_store.as_retriever(
                                    search_type="similarity_score_threshold",
                                    search_kwargs={"score_threshold": float(number_of_results)}
                                )
                            elif search_type == "mmr":
                                retriever = vector_store.as_retriever(search_type="mmr")
                            elif search_type == "top_k":
                                retriever = vector_store.as_retriever(search_kwargs={"k": number_of_results})
                            else:
                                st.error("Invalid search type selected.")
                                retriever = None
                            if retriever:
                                results = retriever.invoke(query)
                                st.success('query succesful!')
                        else:
                            st.error('Collection not found')
            for result in results:
                with st.container(border = True):
                    st.header("Metadata")
                    for key in result.metadata:
                        st.write(f"{key}: {result.metadata[key]}")
                    st.divider()
                    st.write(result.page_content)

    elif invoke_or_update == 'Update Database':
        existing_collections = client.list_collections()
        if existing_collections == []:
            st.write("Lets make your first collection for this database")
            new_collection_name = st.text_input("Collection name")
            new_collection_embedding = st.selectbox(
                "Select embedding model for this collection",
                ["mxbai-embed-large", "all-minilm", "nomic-embed-text", "granite-embedding", "paraphrase-multilingual"],
                index=0,
                placeholder="xxxx...",
            )
            if new_collection_name and new_collection_embedding:
                client.create_collection(name=new_collection_name)
                collection_embedding_map = get_collection_embedding_map(db_path)
                collection_embedding_map[new_collection_name] = new_collection_embedding
                save_collection_embedding_map(db_path, collection_embedding_map)
                st.rerun()
        else:
            col1, col2 = st.columns([2,1])
            existing_collections = [col.name for col in client.list_collections()]
            # Show embedding model next to collection name in multiselect
            collection_labels = [
                f"{name} ({collection_embedding_map.get(name, 'No embedding')})" for name in existing_collections
            ]
            with col1:
                selected_collections = st.multiselect(
                    "Select existing collections:",
                    options=existing_collections,
                    format_func=lambda name: f"{name} ({collection_embedding_map.get(name, 'No embedding')})",
                    default=[],
                    help="Choose one or more collections from the list."
                )
            with col2:
                with st.form("add_new_collection_form"):
                    st.write("Or create a new collection")
                    new_collection = st.text_input("New collection name")
                    new_collection_embedding = st.selectbox(
                        "Select embedding model for this collection",
                        ["mxbai-embed-large", "all-minilm", "nomic-embed-text", "granite-embedding", "paraphrase-multilingual"],
                        index=0,
                        placeholder="xxxx...",
                    )
                    submitted = st.form_submit_button("Create collection")
                    if submitted:
                        if new_collection and new_collection_embedding and new_collection not in existing_collections:
                            client.create_collection(name=new_collection)
                            collection_embedding_map = get_collection_embedding_map(db_path)
                            collection_embedding_map[new_collection] = new_collection_embedding
                            save_collection_embedding_map(db_path, collection_embedding_map)
                            st.success('Collection created successfully!')
                            st.rerun()
                        else:
                            st.error("Collection already exists or invalid name.")
            if len(selected_collections) > 0:
                with st.container(border = True):
                    upload_option = st.radio("Data Loading Options",['Sitemap','Page','PDF'], horizontal=True)
                    if upload_option == 'Sitemap':
                        with st.form("database_sitemap_form"):
                            sitemap_url = st.text_input("Sitemap URL")
                            submitted = st.form_submit_button("Submit")
                            if submitted:
                                if sitemap_url:
                                    sitemap_loader = SitemapLoader(web_path=sitemap_url)
                                    docs = sitemap_loader.load_and_split()
                                    if not docs:
                                        st.error("No documents found in the sitemap.")
                                    else:
                                        for selected_collection in selected_collections:
                                            collection_embedding_map = get_collection_embedding_map(db_path)
                                            embedding_model = collection_embedding_map.get(selected_collection)
                                            if not embedding_model:
                                                st.error(f"No embedding model found for collection {selected_collection}.")
                                                continue
                                            vectore_store = Chroma.from_documents(
                                                documents=docs, 
                                                embedding=OllamaEmbeddings(model=embedding_model), 
                                                persist_directory=f'./{database_option}', 
                                                collection_name=selected_collection
                                            )
                                else:
                                    st.error("Please enter a valid Page URL.")
                    elif upload_option == 'Page':
                        with st.form("database_page_form"):
                            page_url = st.text_input("Page URL")
                            submitted = st.form_submit_button("Submit")
                            if submitted:
                                if page_url:
                                    page_loader = WebBaseLoader(web_path=page_url)
                                    docs = page_loader.load_and_split()
                                    if not docs:
                                        st.error("Error with page loader.")
                                    else:
                                        for selected_collection in selected_collections:
                                            collection_embedding_map = get_collection_embedding_map(db_path)
                                            embedding_model = collection_embedding_map.get(selected_collection)
                                            if not embedding_model:
                                                st.error(f"No embedding model found for collection {selected_collection}.")
                                                continue
                                            vectore_store = Chroma.from_documents(
                                                documents=docs, 
                                                embedding=OllamaEmbeddings(model=embedding_model), 
                                                persist_directory=f'./{database_option}', 
                                                collection_name=selected_collection
                                            )
                                else:
                                    st.error("Please enter a valid Page URL.")
                    elif upload_option == 'PDF':
                        st.write("coming soon")
                    else:
                        st.write("coming soon")