"""Configuration for the LLM Council."""

import os
from dotenv import load_dotenv

# .env dosyasındaki anahtarları yükle
load_dotenv()

# API Anahtarları
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Ollama Yerel Ayarları
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")

# Konsey Üyeleri (Hibrit Yapı)

COUNCIL_MODELS = [
    "ollama/deepseek-r1:8b",                   # Yerel (Çalışıyor)
    "groq/llama-3.3-70b-versatile",            # Groq (Çalışıyor)
    "groq/llama-3.1-8b-instant",
    "google/gemini-2.5-flash" #openrouter/mistralai/mistral-7b-instruct:free
    # qwen/qwen3-32b
]

# Başkan Modeli (Hata almamak için Groq üzerinden en güçlü modeli seçelim)
CHAIRMAN_MODEL = "google/gemini-2.5-flash"

# OpenRouter API (Eğer OpenRouter modelleri de eklenecekse kullanılır)
#OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Veri depolama dizini
DATA_DIR = "data/conversations"