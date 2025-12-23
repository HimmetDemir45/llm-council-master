import httpx
import asyncio
from typing import List, Dict, Any, Optional
from .config import GROQ_API_KEY, GOOGLE_API_KEY, OLLAMA_BASE_URL,OPENROUTER_API_KEY

async def query_model(model: str, messages: List[Dict[str, str]], timeout: float = 120.0):
    if model.startswith("ollama/"):
        target_model = model.replace("ollama/", "")
        url = f"{OLLAMA_BASE_URL}/chat/completions"
        payload = {"model": target_model, "messages": messages, "stream": False}
        async with httpx.AsyncClient(timeout=timeout) as client:
            try:
                response = await client.post(url, json=payload)
                if response.status_code != 200:
                    print(f"!!! OLLAMA HATASI ({target_model}): {response.text}")
                    return None
                return {'content': response.json()['choices'][0]['message']['content']}
            except Exception as e:
                print(f"!!! OLLAMA BAGLANTI HATASI: {e}")
                return None

    # 2. GROQ API
    elif model.startswith("groq/"):
        target_model = model.replace("groq/", "")
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
        payload = {"model": target_model, "messages": messages}
        return await _make_openai_call(url, headers, payload, timeout, model)

    # 3. GOOGLE API (Daha sağlam yapı)
    elif model.startswith("google/"):
        target_model = model.replace("google/", "")
        # Model isminin başına 'models/' eklenmesi gerekebilir
        # URL yapısını v1beta1 olarak değiştirmek en geniş uyumluluğu sağlar
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{target_model}:generateContent?key={GOOGLE_API_KEY}"

        prompt = messages[-1]["content"] if messages else ""
        gemini_payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(url, json=gemini_payload)
                data = response.json()
                # Hata ayıklama için terminale yazdır
                if response.status_code != 200:
                    print(f"!!! GOOGLE API HATASI: {data}")
                    return None

                if "candidates" in data:
                    return {'content': data['candidates'][0]['content']['parts'][0]['text']}
                return None
        except Exception as e:
            print(f"!!! GOOGLE BAGLANTI HATASI: {e}")
            return None
    # ... diğer if/elif bloklarının altına ekle
    elif model.startswith("openrouter/"):
        target_model = model.replace("openrouter/", "")
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "HTTP-Referer": "http://localhost:3000", # OpenRouter için gereklidir
            "X-Title": "LLM Council",
            "Content-Type": "application/json"
        }
        payload = {
            "model": target_model,
            "messages": messages
        }
        return await _make_openai_call(url, headers, payload, timeout, model)

async def _make_openai_call(url, headers, payload, timeout, model_name):
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(url, headers=headers, json=payload)
            if response.status_code != 200:
                print(f"!!! HATA {model_name}: Kod {response.status_code} - {response.text}")
                return None
            data = response.json()
            return {'content': data['choices'][0]['message']['content']}
    except Exception as e:
        print(f"!!! BAGLANTI HATASI {model_name}: {e}")
        return None

async def query_models_parallel(models, messages):
    tasks = [query_model(model, messages) for model in models]
    responses = await asyncio.gather(*tasks)
    return {model: response for model, response in zip(models, responses)}