"""Amazon Bedrock (ap-southeast-1): explicação da escolha e respostas do assistente.
Sem chave, devolve texto de fallback para a demo não travar.
"""
from __future__ import annotations
import json, os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).with_name(".env"))

REGION = "ap-southeast-1"
SONNET = "anthropic.claude-3-5-sonnet-20240620-v1:0"
HAIKU = "anthropic.claude-3-haiku-20240307-v1:0"
EMBED = "cohere.embed-multilingual-v3"

_client = None


def client():
    """Chave do time (par ACCESS_KEY/SECRET emitido para ap-southeast-1) ou bearer token.
    As chaves ficam em BEDROCK_* para não sequestrar a role da EC2 usada pelo S3."""
    global _client
    if _client is None:
        import boto3
        if not os.environ.get("AWS_BEARER_TOKEN_BEDROCK"):   # variável vazia faz o boto3 tentar bearer e falhar
            os.environ.pop("AWS_BEARER_TOKEN_BEDROCK", None)
        kw = {"region_name": REGION}
        if os.environ.get("BEDROCK_ACCESS_KEY_ID"):
            kw.update(aws_access_key_id=os.environ["BEDROCK_ACCESS_KEY_ID"],
                      aws_secret_access_key=os.environ["BEDROCK_SECRET_ACCESS_KEY"])
        _client = boto3.client("bedrock-runtime", **kw)
    return _client


def available() -> bool:
    return bool(os.environ.get("AWS_BEARER_TOKEN_BEDROCK") or os.environ.get("BEDROCK_ACCESS_KEY_ID") or os.environ.get("AWS_ACCESS_KEY_ID"))


def credential_mode() -> str:
    if os.environ.get("BEDROCK_ACCESS_KEY_ID"):
        return "par de chaves do time (BEDROCK_ACCESS_KEY_ID)"
    if os.environ.get("AWS_BEARER_TOKEN_BEDROCK"):
        return "bearer token (AWS_BEARER_TOKEN_BEDROCK)"
    if os.environ.get("AWS_ACCESS_KEY_ID"):
        return "AWS_ACCESS_KEY_ID genérico (cuidado: sequestra a role da EC2 para o S3)"
    return "nenhuma"


def selftest() -> str:
    """python -c 'import bedrock; print(bedrock.selftest())'  → confirma região e chave antes da demo.
    Regra do briefing: a chave só vale em ap-southeast-1; em qualquer outra região o erro é de
    credencial/acesso negado, nunca "região errada". Por isso a região é fixa no código, não no .env."""
    if not available():
        return "sem credenciais Bedrock no .env"
    region = client().meta.region_name
    if region != REGION:
        return f"FALHOU antes de chamar: cliente apontado para {region}; a chave só autentica em {REGION}"
    try:
        reply = converse("Responda só: pronto para decolar.", "Responda em português, uma frase.", max_tokens=30)
        return f"OK Bedrock {region} · credencial: {credential_mode()} · AWS_REGION no ambiente: {os.environ.get('AWS_REGION', '(não definido)')} · resposta: {reply}"
    except Exception as e:
        msg = str(e)
        if "IncompleteSignature" in msg or "Credential' parameter" in msg:
            hint = " → linha AWS_BEARER_TOKEN_BEDROCK= vazia no .env faz o boto3 tentar bearer; apague a linha ou preencha"
        elif any(k in msg for k in ("AccessDenied", "UnrecognizedClient", "InvalidSignature", "security token", "ExpiredToken")):
            hint = " → erro de credencial no Bedrock quase sempre é região errada (a chave só vale em ap-southeast-1); se a região está certa, falta o formulário de primeiro uso dos modelos Anthropic no console, ou a chave é de outro time"
        elif "ValidationException" in msg:
            hint = " → modelo não existe em ap-southeast-1 (Titan e Mistral não estão lá); use os IDs de bedrock.py"
        else:
            hint = ""
        return "FALHOU: " + msg[:160] + hint


def converse(prompt: str, system: str, model: str = HAIKU, max_tokens: int = 500) -> str:
    r = client().converse(
        modelId=model, system=[{"text": system}],
        messages=[{"role": "user", "content": [{"text": prompt}]}],
        inferenceConfig={"maxTokens": max_tokens, "temperature": 0.3},
    )
    return "".join(c.get("text", "") for c in r["output"]["message"]["content"])


def embed(texts: list[str], kind: str = "search_document") -> list[list[float]]:
    r = client().invoke_model(modelId=EMBED, body=json.dumps({"texts": texts, "input_type": kind}))
    return json.loads(r["body"].read())["embeddings"]


SYSTEM_EXPLAIN = (
    "Você é o GreenFlight, assistente de compra de passagens que explica a pegada de carbono. "
    "Responda em português do Brasil, em até 4 frases, sem markdown, citando números do contexto. "
    "Seja honesto: a emissão por passageiro depende da ocupação do voo e do tipo de aeronave."
)


def explain_choice(chosen: dict, alternatives: list[dict]) -> str:
    ctx = {"escolhido": chosen, "alternativas": alternatives[:4]}
    prompt = ("Explique para o comprador por que o voo escolhido é (ou não é) a melhor opção de carbono "
              "entre as alternativas, e o que mais pesou: aeronave, ocupação ou distância. Contexto JSON: "
              + json.dumps(ctx, ensure_ascii=False))
    if not available():
        return _fallback_explain(chosen, alternatives)
    try:
        return converse(prompt, SYSTEM_EXPLAIN, model=HAIKU)
    except Exception as e:  # região errada, chave inválida, etc.
        return _fallback_explain(chosen, alternatives) + f" (Bedrock indisponível: {str(e)[:60]})"


def _fallback_explain(chosen: dict, alternatives: list[dict]) -> str:
    worst = max([a.get("per_pax_kg", 0) for a in alternatives] + [chosen.get("per_pax_kg", 0)])
    saved = round(worst - chosen.get("per_pax_kg", 0), 1)
    return (f"O voo {chosen.get('flightno')} em {chosen.get('aircraft')} emite {chosen.get('per_pax_kg')} kg de CO2 por passageiro "
            f"com ocupação de {round(chosen.get('occupancy', 0) * 100)}%. Em relação à pior alternativa listada, "
            f"você evita {saved} kg de CO2, o equivalente a {round(saved / 22, 1)} árvores por um ano.")


def recommend_project(preference: str, projects: list[dict]) -> dict:
    """Bedrock escolhe entre os top-k da busca vetorial e explica. Fallback: primeiro da lista."""
    if not projects:
        return {"recommended_project": None, "short_reason": "Nenhum projeto disponível."}
    fallback = {"recommended_project": projects[0]["name"], "project_id": projects[0]["id"],
                "short_reason": f"Projeto mais próximo da sua preferência \"{preference}\" pela busca semântica ({projects[0]['country']}, {projects[0]['project_type'].replace('_', ' ').lower()})."}
    if not available():
        return fallback
    try:
        import greenflight
        txt = converse(greenflight.recommend_prompt(preference, projects),
                       "Você recomenda projetos ambientais para um programa de compensação de carbono de companhia aérea. Responda só JSON.", model=HAIKU, max_tokens=300)
        data = json.loads(txt[txt.find("{"): txt.rfind("}") + 1])
        name = data.get("recommended_project") or projects[0]["name"]
        match = next((p for p in projects if p["name"].lower() == str(name).lower()), projects[0])
        return {"recommended_project": match["name"], "project_id": match["id"], "short_reason": data.get("short_reason") or fallback["short_reason"]}
    except Exception as e:
        fallback["short_reason"] += f" (Bedrock indisponível: {str(e)[:50]})"
        return fallback


def answer(question: str, knowledge: list[dict]) -> str:
    ctx = "\n".join(f"- ({k['topic']}) {k['content']}" for k in knowledge)
    prompt = f"Pergunta: {question}\n\nBase de conhecimento do GreenFlight (use só isto):\n{ctx}"
    if not available():
        return "Com base no que sei: " + (knowledge[0]["content"] if knowledge else "não encontrei nada na base.")
    try:
        return converse(prompt, SYSTEM_EXPLAIN, model=HAIKU)
    except Exception as e:
        return (knowledge[0]["content"] if knowledge else "Sem resposta.") + f" (Bedrock indisponível: {str(e)[:60]})"
