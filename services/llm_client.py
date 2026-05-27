import os
from typing import List, Dict, Optional

import requests

# Charge .env (développement) si python-dotenv est installé
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    # Si python-dotenv n'est pas disponible, on continue avec os.environ
    pass



def _get_env(name: str, default: Optional[str] = None) -> Optional[str]:
    val = os.getenv(name)
    # Ne considère pas une valeur “placeholder” comme une clé valide.
    if val in (None, "", "YOUR_DEEPSEEK_API_KEY"):
        return default
    if name == "DEEPSEEK_API_KEY" and val is not None and not val.strip():
        return default
    return val




class LLMClientError(RuntimeError):
    pass


def get_llm_provider() -> str:
    provider = (_get_env("LLM_PROVIDER", "openai") or "openai").lower()
    if provider not in {"openai", "deepseek"}:
        provider = "openai"
    return provider


def build_system_prompt() -> str:
    # Prompt “sécurité” + contexte pharmacie.
    return (
        "Tu es un assistant médical pour une pharmacie. "
        "Tu dois répondre en français, avec prudence et clarté. "
        "Tu ne remplaces jamais un médecin. "
        "Si les symptômes semblent graves (difficulté à respirer, douleur thoracique, confusion, etc.), "
        "ou si la personne est un enfant, une femme enceinte/allaitante, ou si les symptômes persistent, "
        "tu dois recommander de consulter rapidement un professionnel de santé. "
        "Tu peux proposer des conseils généraux et recommander de lire la notice. "
        "Tu peux aussi proposer des vérifications (prix/stock) mais seulement si l'utilisateur demande explicitement."
    )


def _call_openai_chat(messages: List[Dict[str, str]]) -> str:
    api_key = _get_env("OPENAI_API_KEY")
    if not api_key:
        raise LLMClientError("OPENAI_API_KEY manquante dans les variables d'environnement")

    model = _get_env("OPENAI_MODEL", "gpt-3.5-turbo")

    url = _get_env("OPENAI_BASE_URL", "https://api.openai.com/v1") + "/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": messages,
        "temperature": float(_get_env("LLM_TEMPERATURE", "0.4") or 0.4),
    }

    r = requests.post(url, headers=headers, json=payload, timeout=60)
    if r.status_code >= 400:
        raise LLMClientError(f"OpenAI erreur {r.status_code}: {r.text}")

    data = r.json()
    # Format: { choices: [ { message: { content } } ] }
    try:
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        raise LLMClientError(f"Réponse OpenAI inattendue: {e} / {data}")


def _call_deepseek_chat(messages: List[Dict[str, str]]) -> str:
    api_key = _get_env("DEEPSEEK_API_KEY")
    if not api_key:
        raise LLMClientError("DEEPSEEK_API_KEY manquante dans les variables d'environnement")

    model = _get_env("DEEPSEEK_MODEL", "deepseek-chat")
    base_url = _get_env("DEEPSEEK_BASE_URL", "https://api.deepseek.com")

    url = base_url.rstrip("/") + "/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": messages,
        "temperature": float(_get_env("LLM_TEMPERATURE", "0.4") or 0.4),
    }

    r = requests.post(url, headers=headers, json=payload, timeout=60)
    if r.status_code >= 400:
        raise LLMClientError(f"DeepSeek erreur {r.status_code}: {r.text}")

    data = r.json()
    try:
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        raise LLMClientError(f"Réponse DeepSeek inattendue: {e} / {data}")


def chat_completion(user_message: str, history: Optional[List[Dict[str, str]]] = None) -> str:
    provider = get_llm_provider()

    messages: List[Dict[str, str]] = []
    messages.append({"role": "system", "content": build_system_prompt()})

    if history:
        # history doit être de la forme [{role, content}, ...] (user/assistant)
        messages.extend(history)

    messages.append({"role": "user", "content": user_message})

    if provider == "deepseek":
        return _call_deepseek_chat(messages)
    return _call_openai_chat(messages)

