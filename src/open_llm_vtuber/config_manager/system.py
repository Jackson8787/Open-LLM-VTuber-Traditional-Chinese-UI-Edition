# config_manager/system.py
from pydantic import Field, model_validator
from typing import Dict, ClassVar
from .i18n import I18nMixin, Description


class SystemConfig(I18nMixin):
    """System configuration settings."""

    conf_version: str = Field(..., alias="conf_version")
    host: str = Field(..., alias="host")
    port: int = Field(..., alias="port")
    config_alts_dir: str = Field(..., alias="config_alts_dir")
    tool_prompts: Dict[str, str] = Field(..., alias="tool_prompts")
    enable_proxy: bool = Field(False, alias="enable_proxy")

    DESCRIPTIONS: ClassVar[Dict[str, Description]] = {
        "conf_version": Description(en="Configuration version", zh="設定檔版本"),
        "host": Description(en="Server host address", zh="伺服器主機位址"),
        "port": Description(en="Server port number", zh="伺服器連接埠"),
        "config_alts_dir": Description(
            en="Directory for alternative configurations", zh="替代設定目錄"
        ),
        "tool_prompts": Description(
            en="Tool prompts to be inserted into persona prompt",
            zh="要插入角色提示詞中的工具提示詞",
        ),
        "enable_proxy": Description(
            en="Enable proxy mode for multiple clients",
            zh="啟用代理模式，讓多個客戶端共用一個 ws 連線",
        ),
    }

    @model_validator(mode="after")
    def check_port(cls, values):
        port = values.port
        if port < 0 or port > 65535:
            raise ValueError("Port must be between 0 and 65535")
        return values
