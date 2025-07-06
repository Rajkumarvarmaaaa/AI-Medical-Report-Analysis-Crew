import os
from dotenv import load_dotenv
from crewai import LLM

load_dotenv()

# --- NEW: Add Database and Broker URLs ---
# Using SQLite for simplicity. For production, use 'postgresql://user:password@host/dbname'
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///analysis_results.db")
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

### Loading LLM
shared_llm = LLM(
    model="gemini/gemini-2.0-flash",
    temperature=0.7,
)