# =============================================================================
# config.py — Central configuration for PetroMind
# Loads all settings from .env file (development)
# In production: GCP Secret Manager via service account
# =============================================================================

import os
from dotenv import load_dotenv

load_dotenv()

# =============================================================================
# LLM PROVIDER — pluggable interface
# =============================================================================
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini")

# =============================================================================
# GEMINI (GCP)
# =============================================================================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")

# =============================================================================
# OPENAI (alternative)
# =============================================================================
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# =============================================================================
# ANTHROPIC CLAUDE (alternative)
# =============================================================================
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# =============================================================================
# QDRANT — vector database
# =============================================================================
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "petromind")

# =============================================================================
# APPLICATION
# =============================================================================
APP_ENV = os.getenv("APP_ENV", "development")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# =============================================================================
# CHUNKING SETTINGS
# =============================================================================
CHUNK_SIZE = 512
CHUNK_OVERLAP = 50
TOP_K_RESULTS = 5

# =============================================================================
# VALIDATION
# =============================================================================
def validate_config():
    """
    Pre-flight checklist — runs at startup.
    Checks that the active LLM provider has its key configured.
    Fails fast rather than failing mid-request.
    """
    errors = []

    if LLM_PROVIDER == "gemini" and not GEMINI_API_KEY:
        errors.append("GEMINI_API_KEY missing")
    elif LLM_PROVIDER == "openai" and not OPENAI_API_KEY:
        errors.append("OPENAI_API_KEY missing")
    elif LLM_PROVIDER == "claude" and not ANTHROPIC_API_KEY:
        errors.append("ANTHROPIC_API_KEY missing")

    if not QDRANT_HOST:
        errors.append("QDRANT_HOST missing")

    if errors:
        raise ValueError(
            f"Configuration errors: {', '.join(errors)}\n"
            f"Check your .env file."
        )

    print(f"✅ Configuration validated")
    print(f"   LLM Provider: {LLM_PROVIDER}")
    print(f"   Qdrant:       {QDRANT_HOST}:{QDRANT_PORT}")
    print(f"   Collection:   {QDRANT_COLLECTION}")
    print(f"   Environment:  {APP_ENV}")


# =============================================================================
# RBAC SETTINGS
# =============================================================================
SECRET_KEY = os.getenv("SECRET_KEY", "petromind-dev-secret-change-in-production")
ACCESS_TOKEN_EXPIRE_MINUTES = 60