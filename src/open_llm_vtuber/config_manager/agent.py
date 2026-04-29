"""
This module contains the pydantic model for the configurations of
different types of agents.
"""

from pydantic import BaseModel, Field
from typing import Dict, ClassVar, Optional, Literal, List
from .i18n import I18nMixin, Description
from .stateless_llm import StatelessLLMConfigs

# ======== Configurations for different Agents ========


LLMProviderName = Literal[
    "stateless_llm_with_template",
    "openai_compatible_llm",
    "claude_llm",
    "llama_cpp_llm",
    "ollama_llm",
    "lmstudio_llm",
    "openai_llm",
    "gemini_llm",
    "zhipu_llm",
    "deepseek_llm",
    "groq_llm",
    "mistral_llm",
]


class ModelRoutingConfig(I18nMixin, BaseModel):
    """Rule-based model routing configuration."""

    enabled: bool = Field(False, alias="enabled")
    default_model: Optional[LLMProviderName] = Field(None, alias="default_model")
    chat_model: Optional[LLMProviderName] = Field(None, alias="chat_model")
    vision_model: Optional[LLMProviderName] = Field(None, alias="vision_model")
    tool_model: Optional[LLMProviderName] = Field(None, alias="tool_model")
    simple_model: Optional[LLMProviderName] = Field(None, alias="simple_model")
    simple_query_max_chars: int = Field(32, alias="simple_query_max_chars")

    DESCRIPTIONS: ClassVar[Dict[str, Description]] = {
        "enabled": Description(
            en="Enable rule-based model routing",
            zh="啟用規則式模型路由",
        ),
        "default_model": Description(
            en="Fallback model provider when no route matches",
            zh="沒有符合路由時使用的預設模型提供者",
        ),
        "chat_model": Description(
            en="Model provider for normal text chat",
            zh="一般文字聊天使用的模型提供者",
        ),
        "vision_model": Description(
            en="Model provider for image, camera, or screen inputs",
            zh="圖片、攝影機或螢幕輸入使用的模型提供者",
        ),
        "tool_model": Description(
            en="Model provider for MCP/tool-use turns",
            zh="MCP 或工具呼叫回合使用的模型提供者",
        ),
        "simple_model": Description(
            en="Model provider for short, simple questions",
            zh="短小簡單問題使用的模型提供者",
        ),
        "simple_query_max_chars": Description(
            en="Maximum character count treated as a simple question",
            zh="會被視為簡單問題的最大字數",
        ),
    }


class BasicMemoryAgentConfig(I18nMixin, BaseModel):
    """Configuration for the basic memory agent."""

    llm_provider: LLMProviderName = Field(..., alias="llm_provider")

    faster_first_response: Optional[bool] = Field(True, alias="faster_first_response")
    segment_method: Literal["regex", "pysbd"] = Field("pysbd", alias="segment_method")
    use_mcpp: Optional[bool] = Field(False, alias="use_mcpp")
    mcp_enabled_servers: Optional[List[str]] = Field([], alias="mcp_enabled_servers")
    long_term_memory_enabled: bool = Field(False, alias="long_term_memory_enabled")
    memory_backend: Literal["json", "sqlite"] = Field("json", alias="memory_backend")
    memory_max_items: int = Field(80, alias="memory_max_items")
    model_routing: ModelRoutingConfig = Field(
        default_factory=ModelRoutingConfig, alias="model_routing"
    )

    DESCRIPTIONS: ClassVar[Dict[str, Description]] = {
        "llm_provider": Description(
            en="LLM provider to use for this agent",
            zh="Basic Memory Agent 使用的大型語言模型選項",
        ),
        "faster_first_response": Description(
            en="Whether to respond as soon as encountering a comma in the first sentence to reduce latency (default: True)",
            zh="是否在第一句回應遇到逗號時就直接產生音訊，以降低首句延遲（預設：True）",
        ),
        "segment_method": Description(
            en="Method for segmenting sentences: 'regex' or 'pysbd' (default: 'pysbd')",
            zh="句子切分方式：'regex' 或 'pysbd'（預設：'pysbd'）",
        ),
        "use_mcpp": Description(
            en="Whether to use MCP (Model Context Protocol) for the agent (default: True)",
            zh="是否為代理啟用 MCP（Model Context Protocol）Plus（預設：False）",
        ),
        "mcp_enabled_servers": Description(
            en="List of MCP servers to enable for the agent",
            zh="為代理啟用的 MCP 伺服器清單",
        ),
        "long_term_memory_enabled": Description(
            en="Whether to store and retrieve cross-session local long-term memory",
            zh="是否儲存並檢索跨對話的本機長期記憶",
        ),
        "memory_backend": Description(
            en="Local long-term memory backend: json or sqlite",
            zh="本機長期記憶儲存方式：json 或 sqlite",
        ),
        "memory_max_items": Description(
            en="Maximum number of local long-term memory items to keep",
            zh="保留的本機長期記憶項目上限",
        ),
        "model_routing": Description(
            en="Rule-based routing between configured LLM providers",
            zh="在已設定 LLM 提供者之間進行規則式路由",
        ),
    }


class Mem0VectorStoreConfig(I18nMixin, BaseModel):
    """Configuration for Mem0 vector store."""

    provider: str = Field(..., alias="provider")
    config: Dict = Field(..., alias="config")

    DESCRIPTIONS: ClassVar[Dict[str, Description]] = {
        "provider": Description(
            en="Vector store provider (e.g., qdrant)", zh="向量儲存提供者（如 qdrant）"
        ),
        "config": Description(
            en="Provider-specific configuration", zh="提供者專屬設定"
        ),
    }


class Mem0LLMConfig(I18nMixin, BaseModel):
    """Configuration for Mem0 LLM."""

    provider: str = Field(..., alias="provider")
    config: Dict = Field(..., alias="config")

    DESCRIPTIONS: ClassVar[Dict[str, Description]] = {
        "provider": Description(en="LLM provider name", zh="語言模型提供者名稱"),
        "config": Description(
            en="Provider-specific configuration", zh="提供者專屬設定"
        ),
    }


class Mem0EmbedderConfig(I18nMixin, BaseModel):
    """Configuration for Mem0 embedder."""

    provider: str = Field(..., alias="provider")
    config: Dict = Field(..., alias="config")

    DESCRIPTIONS: ClassVar[Dict[str, Description]] = {
        "provider": Description(en="Embedder provider name", zh="嵌入模型提供者名稱"),
        "config": Description(
            en="Provider-specific configuration", zh="提供者專屬設定"
        ),
    }


class Mem0Config(I18nMixin, BaseModel):
    """Configuration for Mem0."""

    vector_store: Mem0VectorStoreConfig = Field(..., alias="vector_store")
    llm: Mem0LLMConfig = Field(..., alias="llm")
    embedder: Mem0EmbedderConfig = Field(..., alias="embedder")

    DESCRIPTIONS: ClassVar[Dict[str, Description]] = {
        "vector_store": Description(en="Vector store configuration", zh="向量儲存設定"),
        "llm": Description(en="LLM configuration", zh="語言模型設定"),
        "embedder": Description(en="Embedder configuration", zh="嵌入模型設定"),
    }


# =================================


class HumeAIConfig(I18nMixin, BaseModel):
    """Configuration for the Hume AI agent."""

    api_key: str = Field(..., alias="api_key")
    host: str = Field("api.hume.ai", alias="host")
    config_id: Optional[str] = Field(None, alias="config_id")
    idle_timeout: int = Field(15, alias="idle_timeout")

    DESCRIPTIONS: ClassVar[Dict[str, Description]] = {
        "api_key": Description(
            en="API key for Hume AI service", zh="Hume AI 服務的 API 金鑰"
        ),
        "host": Description(
            en="Host URL for Hume AI service (default: api.hume.ai)",
            zh="Hume AI 服務的主機位址（預設：api.hume.ai）",
        ),
        "config_id": Description(
            en="Configuration ID for EVI settings", zh="EVI 設定 ID"
        ),
        "idle_timeout": Description(
            en="Idle timeout in seconds before disconnecting (default: 15)",
            zh="閒置逾時後斷線的秒數（預設：15）",
        ),
    }


# =================================


class LettaConfig(I18nMixin, BaseModel):
    """Configuration for the Letta agent."""

    host: str = Field("localhost", alias="host")
    port: int = Field(8283, alias="port")
    id: str = Field(..., alias="id")
    faster_first_response: Optional[bool] = Field(True, alias="faster_first_response")
    segment_method: Literal["regex", "pysbd"] = Field("pysbd", alias="segment_method")

    DESCRIPTIONS: ClassVar[Dict[str, Description]] = {
        "host": Description(
            en="Host address for the Letta server", zh="Letta 伺服器的主機位址"
        ),
        "port": Description(
            en="Port number for the Letta server (default: 8283)",
            zh="Letta 伺服器的連接埠（預設：8283）",
        ),
        "id": Description(
            en="Agent instance ID running on the Letta server",
            zh="指定在 Letta 伺服器上執行的 Agent 實例 ID",
        ),
    }


class AgentSettings(I18nMixin, BaseModel):
    """Settings for different types of agents."""

    basic_memory_agent: Optional[BasicMemoryAgentConfig] = Field(
        None, alias="basic_memory_agent"
    )
    mem0_agent: Optional[Mem0Config] = Field(None, alias="mem0_agent")
    hume_ai_agent: Optional[HumeAIConfig] = Field(None, alias="hume_ai_agent")
    letta_agent: Optional[LettaConfig] = Field(None, alias="letta_agent")

    DESCRIPTIONS: ClassVar[Dict[str, Description]] = {
        "basic_memory_agent": Description(
            en="Configuration for basic memory agent", zh="基礎記憶代理設定"
        ),
        "mem0_agent": Description(en="Configuration for Mem0 agent", zh="Mem0 代理設定"),
        "hume_ai_agent": Description(
            en="Configuration for Hume AI agent", zh="Hume AI 代理設定"
        ),
        "letta_agent": Description(
            en="Configuration for Letta agent", zh="Letta 代理設定"
        ),
    }


class AgentConfig(I18nMixin, BaseModel):
    """This class contains all of the configurations related to agent."""

    conversation_agent_choice: Literal[
        "basic_memory_agent", "mem0_agent", "hume_ai_agent", "letta_agent"
    ] = Field(..., alias="conversation_agent_choice")
    agent_settings: AgentSettings = Field(..., alias="agent_settings")
    llm_configs: StatelessLLMConfigs = Field(..., alias="llm_configs")

    DESCRIPTIONS: ClassVar[Dict[str, Description]] = {
        "conversation_agent_choice": Description(
            en="Type of conversation agent to use", zh="要使用的對話代理類型"
        ),
        "agent_settings": Description(
            en="Settings for different agent types", zh="不同代理類型的設定"
        ),
        "llm_configs": Description(
            en="Pool of LLM provider configurations", zh="語言模型提供者設定池"
        ),
        "faster_first_response": Description(
            en="Whether to respond as soon as encountering a comma in the first sentence to reduce latency (default: True)",
            zh="是否在第一句回應遇到逗號時就直接產生音訊，以降低首句延遲（預設：True）",
        ),
        "segment_method": Description(
            en="Method for segmenting sentences: 'regex' or 'pysbd' (default: 'pysbd')",
            zh="句子切分方式：'regex' 或 'pysbd'（預設：'pysbd'）",
        ),
    }
