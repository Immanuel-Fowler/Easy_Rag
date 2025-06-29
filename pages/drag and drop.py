# 01: These would be the basic imports to get started
import streamlit as st
from barfi.flow import Block, SchemaManager, ComputeEngine
from barfi.flow.streamlit import st_flow

#Local Data Source Block
data_block_local = Block(name="Local Data Source")
data_block_local.add_output(name="Output")
data_block_local.add_option(
    name="Local Source Path", type="input", value = ""
)

#Remote Data Source Block
data_block_remote = Block(name="Remote Data Source")
data_block_remote.add_output(name="Output")
data_block_remote.add_option(
    name="Source Path", type="input", value="Enter Path to Data Source"
)
data_block_remote.add_option(
    name="Source Type", type="select", items=["sitemap","url", "file(Only PDF's)"]
)

# RAG Block
rag_block = Block(name="RAG")
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

#LLM With Prompt Block
llm_w_prompt_block = Block(name="LLM With Prompt")
llm_w_prompt_block.add_option(
    name="Large Language Model",
    value = "",
    type = "input",
)
llm_w_prompt_block.add_input(
    name="Input"
)
base_blocks=[llm_w_prompt_block,data_block_local,data_block_remote,rag_block]
barfi_result = st_flow(base_blocks)
 
# 05: You can view the schema here
st.write(barfi_result)