import subprocess

def get_local_ollama_models():
    result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
    models = []
    for line in result.stdout.splitlines()[1:]:  # Skip header line
        if line.strip():
            model_name = line.split()[0]
            models.append(model_name)
    return models

# Example usage:
local_models = get_local_ollama_models()
print(local_models)