import os
import json
from azure.core.credentials import AzureKeyCredential
from azure.ai.openai import OpenAIClient
from azure.identity import DefaultAzureCredential
import requests
from requests.exceptions import RequestException
import time


# Configuração das variáveis de ambiente para a API
AZURE_OPENAI_ENDPOINT = os.getenv('AZURE_OPENAI_ENDPOINT')
AZURE_OPENAI_DEPLOYMENT = os.getenv('AZURE_OPENAI_DEPLOYMENT')
AZURE_OPENAI_API_KEY = os.getenv('AZURE_OPENAI_API_KEY')


if not all([AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_DEPLOYMENT, AZURE_OPENAI_API_KEY]):
    raise EnvironmentError('Defina as variáveis de ambiente AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_DEPLOYMENT e AZURE_OPENAI_API_KEY.')


# A função call_azure_openai foi modificada para usar a API de forma direta com requests
# Isso permite um controle mais granular para requisições multimodais, que ainda estão
# em desenvolvimento na biblioteca azure-ai-openai e podem ter formatos específicos.
def call_azure_openai(prompt: str, base64_image: str, max_retries: int = 5) -> dict:
    """
    Chama a API do Azure OpenAI para uma análise multimodal.

    Args:
        prompt (str): O prompt de texto com as instruções.
        base64_image (str): A imagem codificada em Base64.
        max_retries (int): O número máximo de tentativas em caso de falha.

    Returns:
        dict: O resultado da análise da IA em formato JSON.
    """
    
    # Formato da URL para a API de chat completions com o modelo de visão
    # O modelo GPT-4o, por exemplo, é ideal para este tipo de tarefa
    api_version = "2024-02-15-preview"
    full_url = f"{AZURE_OPENAI_ENDPOINT}/openai/deployments/{AZURE_OPENAI_DEPLOYMENT}/chat/completions?api-version={api_version}"

    headers = {
        "Content-Type": "application/json",
        "api-key": AZURE_OPENAI_API_KEY
    }

    # Estrutura da requisição multimodal para a API de chat completions
    payload = {
        "messages": [
            {
                "role": "system",
                "content": "You are a senior security engineer specialized in threat modeling and STRIDE."
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        "temperature": 0.0,
        "max_tokens": 1500,
        "response_format": { "type": "json_object" }
    }

    retries = 0
    while retries < max_retries:
        try:
            # Envia a requisição para a API
            response = requests.post(full_url, headers=headers, json=payload)
            response.raise_for_status() # Lança um erro para códigos de status HTTP ruins (4xx ou 5xx)

            content = response.json()['choices'][0]['message']['content']
            return json.loads(content)

        except (RequestException, KeyError, json.JSONDecodeError) as e:
            retries += 1
            if retries == max_retries:
                raise RuntimeError(f"Falha ao chamar a API do Azure OpenAI após {max_retries} tentativas: {e}")
            time.sleep(2 ** retries) # Espera com backoff exponencial

    return {}
# Exemplo de uso:
# result = call_azure_openai("Analise o diagrama e identifique ameaças STRIDE.", base64_image)
# print(json.dumps(result, indent=2))