from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
import os
import json
from .prompt_builder import prepare_prompt_payload
from .azure_client import call_azure_openai

# Certifique-se de que o caminho para o arquivo é relativo ao diretório raiz do projeto
# Isso evita problemas com caminhos absolutos.
# Exemplo de estrutura:
# /seu_projeto
# ├── app/
# │   ├── __init__.py
# │   ├── main.py
# │   ├── prompt_builder.py
# │   └── azure_client.py
# └── requirements.txt

app = FastAPI(
    title="Analisador de Ameaças STRIDE",
    description="Uma API que utiliza Azure OpenAI para analisar diagramas de arquitetura e identificar ameaças STRIDE."
)

@app.post("/analyze")
async def analyze_architecture(image: UploadFile = File(...), metadata: str | None = None):
    """
    Analisa um diagrama de arquitetura de aplicação para identificar ameaças STRIDE.

    A imagem deve ser enviada como um arquivo binário. O modelo de IA interpretará
    o diagrama e gerará uma análise detalhada.
    """
    
    # Verifica se o arquivo é uma imagem
    if image.content_type.split('/')[0] != 'image':
        raise HTTPException(status_code=400, detail='O arquivo enviado não é uma imagem.')

    image_bytes = await image.read()

    # Prepara o prompt de texto e a imagem para a requisição multimodal
    try:
        prompt_payload, base64_image = prepare_prompt_payload(image_bytes, metadata)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao preparar a requisição: {e}")

    # Chama o modelo Azure OpenAI e recebe a resposta
    try:
        analysis_result = call_azure_openai(prompt_payload, base64_image)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao chamar a API do Azure OpenAI: {e}")
    
    # Retorna o resultado da análise
    return JSONResponse(content={
        "status": "sucesso",
        "analysis": analysis_result
    })

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
# Para rodar localmente, use:
# uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload