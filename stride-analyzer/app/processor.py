import base64
import json
import io
from PIL import Image

def prepare_prompt_payload(image_bytes: bytes, metadata: str | None = None) -> tuple[str, str]:
    """
    Prepara o payload da requisição multimodal para o modelo de IA.
    
    Recebe os bytes da imagem e metadados, codifica a imagem em Base64 e constrói
    o prompt de texto que guiará a análise.
    
    Retorna uma tupla contendo o prompt de texto e a imagem em Base64.
    """
    
    # Valida e processa a imagem para garantir que seja um formato aceitável
    try:
        img = Image.open(io.BytesIO(image_bytes))
        # Converte para um formato compatível para codificação (e.g., JPEG)
        buffered = io.BytesIO()
        img.save(buffered, format="JPEG")
        base64_image = base64.b64encode(buffered.getvalue()).decode('utf-8')
    except Exception as e:
        raise ValueError(f"Não foi possível processar a imagem: {e}")

    # Tenta carregar os metadados do JSON se eles existirem
    try:
        parsed_metadata = json.loads(metadata) if metadata else {}
    except json.JSONDecodeError:
        parsed_metadata = {"raw_metadata": metadata}

    # Define a estrutura de saída JSON esperada do modelo
    json_schema = {
        "title": "Análise de Ameaças STRIDE",
        "description": "Análise detalhada de ameaças para um diagrama de arquitetura, baseada na metodologia STRIDE.",
        "type": "object",
        "properties": {
            "threats": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "category": {"type": "string", "enum": ["Spoofing", "Tampering", "Repudiation", "Information Disclosure", "Denial of Service", "Elevation of Privilege"]},
                        "threat_description": {"type": "string"},
                        "cause": {"type": "string"},
                        "mitigation": {"type": "string"}
                    },
                    "required": ["category", "threat_description", "cause", "mitigation"]
                }
            },
            "summary": {"type": "string"}
        },
        "required": ["threats", "summary"]
    }
    
    # Constrói o prompt que será enviado ao modelo.
    # Ele deve ser claro e conciso para obter a melhor resposta.
    prompt_template = f"""
    Você é um analista de segurança especializado em modelagem de ameaças e na metodologia STRIDE.
    Analise o diagrama de arquitetura de aplicação fornecido na imagem.

    Com base no diagrama e nos metadados fornecidos (se existirem): {json.dumps(parsed_metadata)},
    identifique as ameaças potenciais de segurança utilizando a metodologia STRIDE.

    Para cada ameaça identificada, forneça:
    - **category**: Uma das categorias STRIDE (Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege).
    - **threat_description**: Uma descrição clara da ameaça.
    - **cause**: O componente ou o ponto de falha na arquitetura que causa a ameaça.
    - **mitigation**: Uma recomendação concisa de como mitigar a ameaça.

    Estruture sua resposta estritamente como um objeto JSON. Siga o seguinte schema:
    {json.dumps(json_schema, indent=2)}

    """
    
    return prompt_template, base64_image
