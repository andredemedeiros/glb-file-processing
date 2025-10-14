import os
from dotenv import load_dotenv

# Carrega o arquivo .env (a partir da raiz)
load_dotenv()

# Lê a variável do ambiente
path_to_glb = os.getenv("PATH_TO_GLB")

if not path_to_glb:
    raise ValueError("Variável PATH_TO_GLB não encontrada no arquivo .env")

print(f"Caminho do arquivo GLB: {path_to_glb}")