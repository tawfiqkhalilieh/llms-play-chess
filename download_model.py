from huggingface_hub import hf_hub_download
import os

model_id = "Qwen/Qwen2.5-0.5B-Instruct-GGUF"
filename = "qwen2.5-0.5b-instruct-q8_0.gguf"
local_dir = "models"

print(f"Downloading {filename} from {model_id} to {local_dir}...")
try:
    path = hf_hub_download(repo_id=model_id, filename=filename, local_dir=local_dir, local_dir_use_symlinks=False)
    print(f"Download complete: {path}")
except Exception as e:
    print(f"Error downloading model: {e}")
