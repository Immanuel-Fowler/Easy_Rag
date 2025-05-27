import streamlit as st
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_ollama import ChatOllama
import os
import chromadb
from streamlit_option_menu import option_menu

st.set_page_config(initial_sidebar_state="collapsed")

PROMPT_TEMPLATE = """
Answer the question based only on the following context:

{context}

---

Answer the question based on the above context: {question}
"""

embedding_function = None

client = None
collections = []
Databases = []
for entry in os.listdir('./'):
    full_path = os.path.join('./', entry)
    if os.path.isdir(full_path) and 'data_' in entry:
        Databases.append(entry)

chosen_database = st.selectbox(
        "Select the database you want to use",
        Databases,
        index=None,
        placeholder="data_xxxx_xxxx...",
    )

if chosen_database is not None:
    client = chromadb.PersistentClient(path=f'./{chosen_database}')
    embedding_function = OllamaEmbeddings(model = chosen_database.split('_')[-1])
    st.success('Database loaded successfully!')

chosen_collection = st.selectbox(
        "Select the collection you want to use",
        [col.name for col in client.list_collections()] if chosen_database is not None else [],
        index=None,
        placeholder="data_xxxx_xxxx...",
    )
mmr_sst_topk =  option_menu("Chose your rag search type", 
                            ["similarity score", "mmr","top k"],
                            icons=["1-square-fill", "2-square-fill", "3-square-fill"], 
                            menu_icon="search", 
                            default_index=1, 
                            orientation="horizontal",)
with st.form("query_form"):
    
    query = st.text_input("Enter your query here", "What is the meaning of life?")

    if mmr_sst_topk == "similarity score":
        search_number_input = st.number_input(
            "Enter the simliarity score threshold",
            min_value=0.00,
            max_value=100.00,
            value=None,
            step=0.25,
            help="Choose the the minimum similarity score of the retrieved results",
            format="%.2f"
        )
    elif mmr_sst_topk == "top k":
        search_number_input = st.number_input(
            "Enter the number of top results to retrieve",
            min_value=1,
            max_value=100,
            value=None,
            step=1,
            help="Choose the number of top results to retrieve",
        )
    

    submitted = st.form_submit_button("Submit")

    if submitted and chosen_database is not None and chosen_collection is not None:
        st.success("Query submitted!")
        vector_store = Chroma(persist_directory=f'./{chosen_database}', 
                    embedding_function=embedding_function,
                    collection_name=f'{chosen_collection}')
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
            st.error("Invalid search type selected.")
            retriever = None

        results = retriever.invoke(query)

        if len(results) == 0:
            st.error(f"Unable to find matching results.")

        context_text = ""

        for result in results:
            context_text += result.page_content + "\n\n---\n\n"

        prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
        prompt = prompt_template.format(context=context_text, question=query)
        print(prompt)
        
        model = ChatOllama(model = "llama3.1")

        response_text = model.invoke(prompt).content
        st.markdown(response_text)

        

