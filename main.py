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

current_dir = os.path.dirname(os.path.abspath(__file__))
Databases = [name for name in os.listdir(current_dir) if os.path.isdir(os.path.join(current_dir, name)) and 'data_' in name]


with st.container():
    with st.form("make_database_form"):
        st.write("Type in the name of the database you want to create")
        database_name = st.text_input("Database name")
        st.write("Choose the embedding model for the database")
        embedding_model = st.selectbox(
            "Select the embedding model",
            ["mxbai-embed-large", 
             "all-minilm", 
             "nomic-embed-text",
             "granite-embedding",
             "paraphrase-multilingual"],
            index=0,
            placeholder="xxxx...",
        )

        submitted = st.form_submit_button("Create database")
        if submitted:
            st.write("Creating database...")
            
            client = chromadb.Client()
            client =  chromadb.PersistentClient(path=f'./data_{database_name}_{embedding_model}')
            #collection = client.create_collection(name=collection_name)

            st.success('Database created successfully!')
            st.rerun()

    
    
with st.container(border = True):
    database_option = st.selectbox(
        "Select the database you want to use",
        Databases,
        index=None,
        placeholder="data_xxxx_xxxx...",
    )

if database_option is not None:
    client = chromadb.PersistentClient(path=f'{database_option}')
    invoke_or_update =  option_menu("Choose to invoke or update your database", ["Invoke Database", 'Update Database'], 
    icons=['robot', 'database-add'], menu_icon="clipboard2-check", default_index=1, orientation="horizontal",)

    if invoke_or_update == 'Invoke Database':
        results = []
        collection_option = st.selectbox(
            "Select the collection you want to use",
            client.list_collections(),
            index=None,
            placeholder="xxxx...",
        )

        if collection_option is not None:
                
            with st.form("invoke_database_form"):
                col1,col2 = st.columns([3,1])

                with col1:
                    st.write("Type in your query")
                    query = st.text_input("Query")

                with col2:
                    st.write("Number of results")
                    kwargs = st.number_input("Number of results", min_value=1, max_value=10, value=3)
                submitted = st.form_submit_button("Invoke")

                if submitted:
                    if query:
                        print(f'collection_name = {collection_option}\nembedding_function = {database_option.split("_")[-1]}\npersist_directory = {database_option}')
                        vector_store = Chroma(
                            collection_name=collection_option,
                            embedding_function=OllamaEmbeddings(model = database_option.split('_')[-1]),
                            persist_directory=f'./{database_option}'
                        )

                        retriever = vector_store.as_retriever(search_kwargs={"k": kwargs})
                        results = retriever.invoke(query)              

                        st.success('query succesful!')
                                #st.rerun()
                    else:
                        st.error('Collection not found')
            for result in results:
                with st.container(border = True):
                    st.header("Metadata")
                    for key in result.metadata:
                        st.write(f"{key}: {result.metadata[key]}")
                    st.divider()
                    st.write(result.page_content)
                
                #st.write(results)

    elif invoke_or_update == 'Update Database':
        existing_collections = client.list_collections()
        if existing_collections == []:
            st.write("Lets make your first collection for this database")
            new_collection_name = st.text_input("Collection name")

            if new_collection_name:
                client.create_collection(name=new_collection_name)
                st.rerun()

        else:
            col1, col2 = st.columns([2,1])
            selected_collections = []

            with col1: 
                selected_collections = st.multiselect(
                    "Select existing collections:",
                    options=existing_collections,
                    default=[],
                    help="Choose one or more collections from the list."
                )

            with col2:
                with st.form("add_new_collection_form"):
                    st.write("Or create a new collection")
                    new_collection = st.text_input("New collection name")
                    submitted = st.form_submit_button("Create collection")

                    if submitted:
                        if new_collection and new_collection not in existing_collections:
                            client.create_collection(name=new_collection)
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
                                    print("Page loader Initialized\n\n")
                                    
                                    # Load and split the documents
                                    docs = sitemap_loader.load_and_split()
                                    print("Page loader loaded and split\n\n")

                                    for selected_collection in selected_collections:

                                        # Initialize the vector store
                                        vectore_store = Chroma.from_documents(
                                            documents=docs, 
                                            embedding=OllamaEmbeddings(model = database_option.split('_')[-1]), 
                                            persist_directory=f'./{database_option}', 
                                            collection_name=selected_collection
                                        )

                                        print(f'Data Uploaded to Collection: \033[92m{selected_collection}\033[0m\n\n')

                                else:
                                    st.error("Please enter a valid Page URL.")
                                

                    elif upload_option == 'Page':
                        with st.form("database_page_form"):
                            page_url = st.text_input("Page URL")
                            submitted = st.form_submit_button("Submit")
                            if submitted:
                                if page_url:

                                    page_loader = WebBaseLoader(web_path=page_url)
                                    print("Page loader Initialized\n\n")
                                    
                                    # Load and split the documents
                                    docs = page_loader.load_and_split()
                                    print("Page loader loaded and split\n\n")

                                    for selected_collection in selected_collections:

                                        # Initialize the vector store
                                        vectore_store = Chroma.from_documents(
                                            documents=docs, 
                                            embedding=OllamaEmbeddings(model = database_option.split('_')[-1]), 
                                            persist_directory=f'./{database_option}', 
                                            collection_name=selected_collection
                                        )

                                        print(f'Data Uploaded to Collection: \033[92m{selected_collection}\033[0m\n\n')

                                else:
                                    st.error("Please enter a valid Page URL.")

                    elif upload_option == 'PDF':
                        st.write("coming soon")

                    else:
                        st.write("coming soon")