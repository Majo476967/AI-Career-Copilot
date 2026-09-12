"""Central Doubao configuration. Import is offline; clients are created on demand."""
import math
import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

DEFAULT_MODEL = "doubao-1-5-lite-32k-250115"
DEFAULT_BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"


class LLMConfigurationError(ValueError):
    pass


class LLMRequestError(RuntimeError):
    pass


@dataclass(frozen=True)
class LLMConfig:
    api_key: str = field(repr=False)
    model: str = DEFAULT_MODEL
    base_url: str = DEFAULT_BASE_URL
    timeout: float = 60.0
    max_retries: int = 2


def load_llm_config():
    # Explicit project path; never print env values or secrets.
    load_dotenv(Path(__file__).resolve().with_name(".env"), override=False)
    key = os.getenv("ARK_API_KEY", "").strip()
    if not key or key == "your_ark_api_key_here":
        raise LLMConfigurationError("请配置 ARK_API_KEY；不要将真实密钥提交到仓库。")
    try:
        timeout = float(os.getenv("ARK_TIMEOUT_SECONDS", "60"))
        retries = int(os.getenv("ARK_MAX_RETRIES", "2"))
        if not math.isfinite(timeout) or timeout <= 0 or retries < 0:
            raise ValueError
    except ValueError:
        raise LLMConfigurationError("ARK_TIMEOUT_SECONDS 必须为正数，ARK_MAX_RETRIES 必须为非负整数。") from None
    model = os.getenv("ARK_MODEL", DEFAULT_MODEL).strip()
    base_url = os.getenv("ARK_BASE_URL", DEFAULT_BASE_URL).strip()
    if not model or not base_url.startswith("https://"):
        raise LLMConfigurationError("ARK_MODEL 不能为空，ARK_BASE_URL 必须使用 HTTPS。")
    return LLMConfig(key, model, base_url, timeout, retries)


def get_llm_client(config=None):
    from openai import OpenAI
    config = config or load_llm_config()
    return OpenAI(api_key=config.api_key, base_url=config.base_url,
                  timeout=config.timeout, max_retries=config.max_retries)


def get_chat_model(*, temperature=0, config=None):
    """Shared initialization for the existing LangChain Agent and analyzers."""
    from langchain_openai import ChatOpenAI
    config = config or load_llm_config()
    return ChatOpenAI(model=config.model, api_key=config.api_key, base_url=config.base_url,
                      temperature=temperature, timeout=config.timeout, max_retries=config.max_retries)


def generate_answer(prompt):
    """Retain the V0 helper and prompt behavior, with a safe basic API error boundary."""
    from openai import APIError
    config = load_llm_config()
    try:
        with get_llm_client(config) as client:
            response = client.chat.completions.create(
                model=config.model,
                messages=[{"role": "system", "content": "你是一个专业的AI助手"},
                          {"role": "user", "content": prompt}],
                temperature=0.3)
    except APIError:
        raise LLMRequestError("豆包 API 请求失败，请检查配置或稍后重试。") from None
    if not response.choices or not response.choices[0].message.content:
        raise LLMRequestError("豆包 API 未返回有效文本。")
    return response.choices[0].message.content


def request_analysis(system_prompt, input_text):
    """Analysis text response; JSON validation stays in the analyzer layer."""
    from openai import APIError
    from core.errors import AnalysisError
    try:
        response = get_chat_model(temperature=0).invoke([
            ("system", system_prompt), ("user", input_text)])
    except (APIError, LLMConfigurationError, LLMRequestError):
        raise AnalysisError("llm_error", "豆包分析请求失败，请检查配置或稍后重试。") from None
    if not isinstance(response.content, str) or not response.content.strip():
        raise AnalysisError("empty_response", "豆包未返回有效的分析文本，请重试。")
    return response.content
