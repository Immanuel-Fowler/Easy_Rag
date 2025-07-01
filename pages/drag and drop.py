# 01: These would be the basic imports to get started
import streamlit as st
from barfi.flow import Block, SchemaManager, ComputeEngine
from barfi.flow.streamlit import st_flow
import os



st.set_page_config(page_title="Chatbot", layout="wide", initial_sidebar_state="collapsed")

if st.button("❓ Help", help="Go to help page"):
    st.switch_page("pages/Help.py")

st.header("Feature Still Being Developed")
st.write("***Not Yet Ready For Use***")
#Local Data Source Block
data_block_local = Block(name="Local Data Source Block")
data_block_local.add_output(name="Output")
data_block_local.add_option(
    name="Local Source Path", type="input", value = ""
)

#Remote Data Source Block
data_block_remote = Block(name="Remote Data Source Block")
data_block_remote.add_output(name="Output")
data_block_remote.add_option(
    name="Source Path", type="input", value="Enter Path to Data Source"
)
data_block_remote.add_option(
    name="Source Type", type="select", items=["sitemap","url", "file(Only PDF's)"]
)

# RAG Block
rag_block = Block(name="RAG Block")
rag_block.add_option(
    name="Score Threshold",
    value = None, 
    type = "number",
    min = 0.00,
    max = 1.00
)
rag_block.add_option(
    name="Top K Results",
    value = None, 
    type = "integer",
    min = 0,
    max = 100
)
rag_block.add_option(
    name="Large Language Model",
    value = "",
    type = "input",
)
rag_block.add_input(
    name="Input"
)
rag_block.add_output(
    name="Similarity Score Output",
)
rag_block.add_output(
    name="Top K Output",
)
rag_block.add_output(
    name="MMR Output",
)
rag_block.add_option(
    name="Embedding Model",
    value = "",
    type = "input",
)

#log Output Block 
log_output_block = Block(name="Log Output")
log_output_block.add_input(
    name="Input"
)
base_blocks=[log_output_block,data_block_local,data_block_remote,rag_block]

barfi_result = st_flow(base_blocks)

schema_manager = SchemaManager()

with st.expander("Schema Management"):
    load_or_save = st.radio(
        "Load or Save Schema",
        ["Save Schema", "Load Schema", "Delete Schema"],
        horizontal=True,
    )

    if load_or_save == "Save Schema":
        schema_name = st.text_input("Schema Name",help="Enter a name for the schema to save it.",)
        if st.button("Save Schema"):
            if schema_name not in schema_manager.schema_names:  
                schema_manager.save_schema(
                    schema_name=schema_name,
                    flow_schema = barfi_result.editor_schema
                )
            else:
                st.warning(f"Schema '{schema_name}' already exists. Please choose a different name.")

    elif load_or_save == "Load Schema":
        schema_names = schema_manager.schema_names
        if schema_names:
            schema_name = st.selectbox("Select Schema to Load", schema_names)
            if st.button("Load Schema"):
                barfi_result = schema_manager.load_schema(schema_name)
                st.success(f"Schema '{schema_name}' loaded successfully.")
        else:
            st.warning("No schemas available to load.")

    elif load_or_save == "Delete Schema":
        schema_names = schema_manager.schema_names
        if schema_names:
            schema_name = st.selectbox("Select Schema to Delete", schema_names)
            if st.button("Delete Schema"):
                schema_manager.delete_schema(schema_name)
                st.success(f"Schema '{schema_name}' deleted successfully.")
        else:
            st.warning("No schemas available to delete.")



# View the schema/result
#st.write(barfi_result)
#st.write(schema_manager.schema_names)