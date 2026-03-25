# config_manager/character.py
from pydantic import Field, field_validator
from typing import Dict, ClassVar
from .i18n import I18nMixin, Description
from .asr import ASRConfig
from .tts import TTSConfig
from .vad import VADConfig
from .tts_preprocessor import TTSPreprocessorConfig

from .agent import AgentConfig


class CharacterConfig(I18nMixin):
    """Character configuration settings."""

    conf_name: str = Field(..., alias="conf_name")
    conf_uid: str = Field(..., alias="conf_uid")
    live2d_model_name: str = Field(..., alias="live2d_model_name")
    character_name: str = Field(default="", alias="character_name")
    human_name: str = Field(default="Human", alias="human_name")
    avatar: str = Field(default="", alias="avatar")
    persona_prompt: str = Field(..., alias="persona_prompt")
    system_prompt: str = Field(default="", alias="system_prompt")
    agent_config: AgentConfig = Field(..., alias="agent_config")
    asr_config: ASRConfig = Field(..., alias="asr_config")
    tts_config: TTSConfig = Field(..., alias="tts_config")
    vad_config: VADConfig = Field(..., alias="vad_config")
    tts_preprocessor_config: TTSPreprocessorConfig = Field(
        ..., alias="tts_preprocessor_config"
    )

    DESCRIPTIONS: ClassVar[Dict[str, Description]] = {
        "conf_name": Description(
            en="Name of the character configuration", zh="角色設定名稱"
        ),
        "conf_uid": Description(
            en="Unique identifier for the character configuration",
            zh="角色設定唯一識別碼",
        ),
        "live2d_model_name": Description(
            en="Name of the Live2D model to use", zh="使用的 Live2D 模型名稱"
        ),
        "character_name": Description(
            en="Name of the AI character in conversation", zh="對話中 AI 角色的名稱"
        ),
        "persona_prompt": Description(
            en="Persona prompt. The persona of your character.", zh="角色人設提示詞"
        ),
        "system_prompt": Description(
            en="Custom system prompt override for the character",
            zh="角色自訂 system prompt 覆寫內容",
        ),
        "agent_config": Description(
            en="Configuration for the conversation agent", zh="對話代理設定"
        ),
        "asr_config": Description(
            en="Configuration for Automatic Speech Recognition", zh="語音辨識設定"
        ),
        "tts_config": Description(
            en="Configuration for Text-to-Speech", zh="語音合成設定"
        ),
        "vad_config": Description(
            en="Configuration for Voice Activity Detection", zh="語音活動偵測設定"
        ),
        "tts_preprocessor_config": Description(
            en="Configuration for Text-to-Speech Preprocessor",
            zh="語音合成前處理器設定",
        ),
        "human_name": Description(
            en="Name of the human user in conversation", zh="對話中人類使用者的名稱"
        ),
        "avatar": Description(
            en="Avatar image path for the character", zh="角色頭像圖片路徑"
        ),
    }

    @field_validator("persona_prompt")
    def check_default_persona_prompt(cls, v):
        if not v:
            raise ValueError(
                "Persona_prompt cannot be empty. Please provide a persona prompt."
            )
        return v

    @field_validator("character_name")
    def set_default_character_name(cls, v, values):
        if not v and "conf_name" in values:
            return values["conf_name"]
        return v
