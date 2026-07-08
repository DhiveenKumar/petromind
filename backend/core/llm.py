# =============================================================================
# llm.py — Pluggable LLM Interface for PetroMind
#
# Design principle: No module imports a specific LLM directly.
# Every module calls get_llm() and gets back a LangChain-compatible
# chat model. Switching providers is one environment variable change.
#
# Supported providers:
#   gemini  → Google Gemini Pro (default, GCP)
#   openai  → OpenAI GPT-4o
#   claude  → Anthropic Claude
#   ollama  → Local Llama (zero cost, offline)
# =============================================================================

from backend.core.config import (
    LLM_PROVIDER,
    GEMINI_API_KEY,
    OPENAI_API_KEY,
    ANTHROPIC_API_KEY
)


def get_llm(temperature: float = 0.0):
    """
    Returns a LangChain-compatible chat model based on LLM_PROVIDER.

    temperature=0.0 default — deterministic outputs for
    safety-critical oil & gas recommendations.
    Callers can override for creative tasks if needed.

    Why LangChain-compatible return type?
    Every module uses the same .invoke() and .stream() interface
    regardless of which provider is active underneath.
    This is the adapter pattern applied to AI model selection.
    """

    if LLM_PROVIDER == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model="gemini-1.5-pro",
            google_api_key=GEMINI_API_KEY,
            temperature=temperature
        )

    elif LLM_PROVIDER == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model="gpt-4o",
            api_key=OPENAI_API_KEY,
            temperature=temperature
        )

    elif LLM_PROVIDER == "claude":
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(
            model="claude-3-5-sonnet-20241022",
            api_key=ANTHROPIC_API_KEY,
            temperature=temperature
        )

    elif LLM_PROVIDER == "ollama":
        from langchain_ollama import ChatOllama
        return ChatOllama(
            model="llama3",
            temperature=temperature
        )

    else:
        raise ValueError(
            f"Unknown LLM_PROVIDER: {LLM_PROVIDER}. "
            f"Choose from: gemini, openai, claude, ollama"
        )


def get_vision_llm():
    """
    Returns vision-capable LLM for the Visual Inspection module.
    Not all providers support vision — this ensures we always
    use a model that can process images.

    Currently Gemini and OpenAI support vision.
    Claude vision support added when stable.
    """

    if LLM_PROVIDER in ["gemini", "ollama", "claude"]:
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model="gemini-1.5-pro-vision",
            google_api_key=GEMINI_API_KEY,
            temperature=0.0
        )

    elif LLM_PROVIDER == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model="gpt-4o",
            api_key=OPENAI_API_KEY,
            temperature=0.0
        )

    else:
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model="gemini-1.5-pro-vision",
            google_api_key=GEMINI_API_KEY,
            temperature=0.0
        )


def get_llm_provider_info() -> dict:
    """
    Returns metadata about the current LLM configuration.
    Used by the /api/health endpoint and admin monitoring page.
    """
    provider_models = {
        "gemini": "gemini-1.5-pro",
        "openai": "gpt-4o",
        "claude": "claude-3-5-sonnet-20241022",
        "ollama": "llama3"
    }

    return {
        "provider": LLM_PROVIDER,
        "model": provider_models.get(LLM_PROVIDER, "unknown"),
        "vision_capable": LLM_PROVIDER in ["gemini", "openai"],
        "temperature": 0.0
    }