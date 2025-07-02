class Block:
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.inputs = []
        self.outputs = []
    
    def add_input(self, input_name, input_type):
        self.inputs.append({'name': input_name, 'type': input_type})

block_array = [
    Block("Input", "Input block for user data")]

# Example block definitions in Python
blocks = [
    {"type": "TextInput", "label": "Text Input", "color": "#2de0fc"},
    {"type": "Retriever", "label": "Retriever", "color": "#ffb347"},
    {"type": "LLM", "label": "LLM", "color": "#a259ff"},
    # Add more as needed
]