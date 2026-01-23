import json
import os
from dataclasses import dataclass
from typing import Any, Dict, Optional

from boto3.session import Session
from langchain_openai import ChatOpenAI
from langchain_aws import ChatBedrock

from get_secret import GetSecret


# ------------------------------------------------------------
# Utility: Load JSON
# ------------------------------------------------------------
def _load_json(path: str) -> Dict[str, Any]:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Model selector file not found: {path}")
    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)


# ------------------------------------------------------------
# Utility: Build Bedrock client
# ------------------------------------------------------------
def _build_bedrock_client(region: str, secret_name: str):
    secret_loader = GetSecret(region_name=region)
    creds = secret_loader.get_secret(secret_name) or {}

    access_key = (
        creds.get("ACCESS_KEY")
        or creds.get("AWS_ACCESS_KEY_ID")
        or os.getenv("AWS_ACCESS_KEY_ID")
    )
    secret_key = (
        creds.get("SECRET_KEY")
        or creds.get("AWS_SECRET_ACCESS_KEY")
        or os.getenv("AWS_SECRET_ACCESS_KEY")
    )
    session_token = (
        creds.get("SESSION_TOKEN")
        or creds.get("AWS_SESSION_TOKEN")
        or os.getenv("AWS_SESSION_TOKEN")
    )

    if not access_key or not secret_key:
        raise RuntimeError("Missing AWS credentials for Bedrock client.")

    session = Session()
    return session.client(
        service_name="bedrock-runtime",
        region_name=region,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        aws_session_token=session_token,
    )


# ------------------------------------------------------------
# Utility: Resolve OpenAI Key
# ------------------------------------------------------------
def _resolve_openai_api_key(
    *, region: str, secret_name: Optional[str], explicit_api_key: Optional[str]
) -> str:
    if explicit_api_key:
        return explicit_api_key

    if secret_name:
        secrets = GetSecret(region_name=region).get_secret(secret_name) or {}
        api_key = secrets.get("OPENAI_API_KEY") or secrets.get("openai_api_key")
        if api_key:
            return api_key

    env_api = os.getenv("OPENAI_API_KEY") or os.getenv("openai_api_key")
    if env_api:
        return env_api

    raise ValueError(
        "Missing OpenAI API key. Provide via Secrets Manager, "
        "model_selector.json api_key, or OPENAI_API_KEY env var."
    )


# ------------------------------------------------------------
# Dataclass: Configuration
# ------------------------------------------------------------
@dataclass
class LLMConfig:
    provider: str
    family: str
    model_id: str
    region: str
    secret_name: Optional[str]
    temperature: float
    max_tokens: int
    anthropic_version: Optional[str] = None
    api_key: Optional[str] = None


# ------------------------------------------------------------
# Provider Mapping Fix (for Bedrock)
# ------------------------------------------------------------
def _map_family_to_provider(family: str) -> Optional[str]:
    """
    Map family → Bedrock provider.
    Needed because global/us/eu model IDs break LangChain's autodection.
    """
    family = (family or "").lower()

    if family in ("claude", "anthropic"):
        return "anthropic"

    if family in ("llama", "meta", "llama3"):
        return "meta"

    if family in ("mistral", "mixtral"):
        return "mistral"

    # add more families here
    return None  # default → let LangChain try (safe fallback)


# ------------------------------------------------------------
# Main Factory
# ------------------------------------------------------------
class LLM:
    def __init__(self, selector_path: str = "model_selector.json"):
        self.selector_path = selector_path
        self._config = _load_json(selector_path)

    # --------------------------------------------------------
    # Build actual LLM model instance
    # --------------------------------------------------------
    def create_llm(self, model_key: str = "current"):
        models = self._config.get("models") or {}
        if model_key not in models:
            raise KeyError(f"Model key '{model_key}' not found in selector.")

        raw_cfg = models[model_key]
        cfg = LLMConfig(
            provider=(raw_cfg.get("provider") or "").lower(),
            family=(raw_cfg.get("family") or "").lower(),
            model_id=raw_cfg.get("model_id"),
            region=raw_cfg.get("region") or "us-east-1",
            secret_name=raw_cfg.get("secret_name"),
            temperature=float(raw_cfg.get("temperature", 0.2)),
            max_tokens=int(raw_cfg.get("max_tokens", 4000)),
            anthropic_version=raw_cfg.get("anthropic_version"),
            api_key=raw_cfg.get("api_key"),
        )

        # ----------------------------------------------------
        # OPENAI MODELS
        # ----------------------------------------------------
        if cfg.provider == "openai":
            api_key = _resolve_openai_api_key(
                region=cfg.region,
                secret_name=cfg.secret_name,
                explicit_api_key=cfg.api_key,
            )

            return ChatOpenAI(
                model=cfg.model_id,
                temperature=cfg.temperature,
                max_tokens=cfg.max_tokens,
                api_key=api_key,
            )

        # ----------------------------------------------------
        # BEDROCK MODELS (Claude, Llama, etc.)
        # ----------------------------------------------------
        if cfg.provider == "bedrock":
            client = _build_bedrock_client(cfg.region, cfg.secret_name or "")

            model_kwargs: Dict[str, Any] = {
                "temperature": cfg.temperature,
                "max_tokens": cfg.max_tokens,
            }

            # Claude models require anthropic_version
            if cfg.family == "claude" and cfg.anthropic_version:
                model_kwargs["anthropic_version"] = cfg.anthropic_version

            # 🔥 FIX: Explicitly map provider for Bedrock
            explicit_provider = _map_family_to_provider(cfg.family)

            chat_args = {
                "client": client,
                "model_id": cfg.model_id,
                "model_kwargs": model_kwargs,
            }

            # Only override provider if mapping is known
            if explicit_provider:
                chat_args["provider"] = explicit_provider

            return ChatBedrock(**chat_args)

        # ----------------------------------------------------
        # Unsupported Provider
        # ----------------------------------------------------
        raise NotImplementedError(f"Provider '{cfg.provider}' not supported.")
