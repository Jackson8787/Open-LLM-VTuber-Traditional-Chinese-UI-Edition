import os
import json
from uuid import uuid4
from typing import Any
import numpy as np
from datetime import datetime
from fastapi import APIRouter, WebSocket, UploadFile, File, Response
from pydantic import BaseModel, Field
from starlette.responses import JSONResponse
from starlette.websockets import WebSocketDisconnect
from loguru import logger
from .service_context import ServiceContext
from .websocket_handler import WebSocketHandler
from .proxy_handler import ProxyHandler
from .config_manager import (
    read_yaml,
    read_yaml_roundtrip,
    save_yaml_roundtrip,
    validate_config,
)


class AgentConfigUpdateRequest(BaseModel):
    llm_provider: str = Field(..., min_length=1)
    provider_config: dict[str, Any] = Field(default_factory=dict)
    system_prompt: str = ""
    long_term_memory_enabled: bool = False
    memory_backend: str = "json"
    memory_max_items: int = 80
    use_mcpp: bool = False
    mcp_enabled_servers: list[str] = Field(default_factory=list)
    model_routing: dict[str, Any] = Field(default_factory=dict)


def init_client_ws_route(default_context_cache: ServiceContext) -> APIRouter:
    """
    Create and return API routes for handling the `/client-ws` WebSocket connections.

    Args:
        default_context_cache: Default service context cache for new sessions.

    Returns:
        APIRouter: Configured router with WebSocket endpoint.
    """

    router = APIRouter()
    ws_handler = WebSocketHandler(default_context_cache)

    @router.websocket("/client-ws")
    async def websocket_endpoint(websocket: WebSocket):
        """WebSocket endpoint for client connections"""
        await websocket.accept()
        client_uid = str(uuid4())

        try:
            await ws_handler.handle_new_connection(websocket, client_uid)
            await ws_handler.handle_websocket_communication(websocket, client_uid)
        except WebSocketDisconnect:
            await ws_handler.handle_disconnect(client_uid)
        except Exception as e:
            logger.error(f"Error in WebSocket connection: {e}")
            await ws_handler.handle_disconnect(client_uid)
            raise

    return router


def init_proxy_route(server_url: str) -> APIRouter:
    """
    Create and return API routes for handling proxy connections.

    Args:
        server_url: The WebSocket URL of the actual server

    Returns:
        APIRouter: Configured router with proxy WebSocket endpoint
    """
    router = APIRouter()
    proxy_handler = ProxyHandler(server_url)

    @router.websocket("/proxy-ws")
    async def proxy_endpoint(websocket: WebSocket):
        """WebSocket endpoint for proxy connections"""
        try:
            await proxy_handler.handle_client_connection(websocket)
        except Exception as e:
            logger.error(f"Error in proxy connection: {e}")
            raise

    return router


def init_webtool_routes(default_context_cache: ServiceContext) -> APIRouter:
    """
    Create and return API routes for handling web tool interactions.

    Args:
        default_context_cache: Default service context cache for new sessions.

    Returns:
        APIRouter: Configured router with WebSocket endpoint.
    """

    router = APIRouter()

    def _get_agent_editor_payload() -> dict[str, Any]:
        config_data = read_yaml("conf.yaml")
        validated = validate_config(config_data)
        llm_configs = validated.character_config.agent_config.llm_configs.model_dump(
            exclude_none=False
        )
        basic_agent = (
            validated.character_config.agent_config.agent_settings.basic_memory_agent
        )
        active_provider = basic_agent.llm_provider
        mcp_servers = []
        if default_context_cache.mcp_server_registery:
            mcp_servers = sorted(default_context_cache.mcp_server_registery.servers)
        else:
            try:
                from .mcpp.server_registry import ServerRegistry

                mcp_servers = sorted(ServerRegistry().servers)
            except Exception:
                mcp_servers = []

        providers = []
        for provider_name, provider_config in llm_configs.items():
            if provider_config is None:
                provider_config = {}

            fields = []
            for key, value in provider_config.items():
                if isinstance(value, (dict, list)):
                    continue

                value_type = "string"
                if isinstance(value, bool):
                    value_type = "boolean"
                elif isinstance(value, int):
                    value_type = "integer"
                elif isinstance(value, float):
                    value_type = "number"
                elif value is None:
                    value_type = "string"

                fields.append(
                    {
                        "key": key,
                        "value": value,
                        "type": value_type,
                    }
                )

            providers.append(
                {
                    "name": provider_name,
                    "fields": fields,
                }
            )

        return {
            "llm_provider": active_provider,
            "providers": providers,
            "system_prompt": validated.character_config.system_prompt or "",
            "persona_prompt": validated.character_config.persona_prompt,
            "long_term_memory_enabled": basic_agent.long_term_memory_enabled,
            "memory_backend": basic_agent.memory_backend,
            "memory_max_items": basic_agent.memory_max_items,
            "use_mcpp": basic_agent.use_mcpp,
            "mcp_enabled_servers": basic_agent.mcp_enabled_servers or [],
            "available_mcp_servers": mcp_servers,
            "model_routing": basic_agent.model_routing.model_dump(),
        }

    @router.get("/web-tool")
    async def web_tool_redirect():
        """Redirect /web-tool to /web_tool/index.html"""
        return Response(status_code=302, headers={"Location": "/web-tool/index.html"})

    @router.get("/web_tool")
    async def web_tool_redirect_alt():
        """Redirect /web_tool to /web_tool/index.html"""
        return Response(status_code=302, headers={"Location": "/web-tool/index.html"})

    @router.get("/api/config/agent-editor")
    async def get_agent_editor_config():
        """Return the current editable agent settings for the web tool."""
        try:
            return JSONResponse(_get_agent_editor_payload())
        except Exception as e:
            logger.error(f"Failed to load agent editor config: {e}")
            return JSONResponse({"error": str(e)}, status_code=500)

    @router.put("/api/config/agent-editor")
    async def update_agent_editor_config(payload: AgentConfigUpdateRequest):
        """Persist agent settings to conf.yaml and reload the shared context."""
        try:
            raw_config = read_yaml_roundtrip("conf.yaml")
            plain_config = read_yaml("conf.yaml")

            character_config = raw_config["character_config"]
            agent_config = character_config["agent_config"]
            agent_settings = agent_config["agent_settings"]["basic_memory_agent"]
            llm_configs = agent_config["llm_configs"]

            plain_character_config = plain_config["character_config"]
            plain_agent_config = plain_character_config["agent_config"]
            plain_agent_settings = plain_agent_config["agent_settings"][
                "basic_memory_agent"
            ]
            plain_llm_configs = plain_agent_config["llm_configs"]

            if payload.llm_provider not in llm_configs:
                return JSONResponse(
                    {"error": f"Unknown LLM provider: {payload.llm_provider}"},
                    status_code=400,
                )

            agent_settings["llm_provider"] = payload.llm_provider
            plain_agent_settings["llm_provider"] = payload.llm_provider
            agent_settings["long_term_memory_enabled"] = (
                payload.long_term_memory_enabled
            )
            plain_agent_settings["long_term_memory_enabled"] = (
                payload.long_term_memory_enabled
            )
            agent_settings["memory_backend"] = payload.memory_backend
            plain_agent_settings["memory_backend"] = payload.memory_backend
            agent_settings["memory_max_items"] = payload.memory_max_items
            plain_agent_settings["memory_max_items"] = payload.memory_max_items
            agent_settings["use_mcpp"] = payload.use_mcpp
            plain_agent_settings["use_mcpp"] = payload.use_mcpp
            agent_settings["mcp_enabled_servers"] = payload.mcp_enabled_servers
            plain_agent_settings["mcp_enabled_servers"] = payload.mcp_enabled_servers
            agent_settings["model_routing"] = payload.model_routing
            plain_agent_settings["model_routing"] = payload.model_routing

            target_provider_config = llm_configs[payload.llm_provider]
            plain_target_provider_config = plain_llm_configs[payload.llm_provider]
            for key, value in payload.provider_config.items():
                if key in target_provider_config:
                    target_provider_config[key] = value
                    plain_target_provider_config[key] = value

            character_config["system_prompt"] = payload.system_prompt or ""
            plain_character_config["system_prompt"] = payload.system_prompt or ""

            validated_config = validate_config(plain_config)
            save_yaml_roundtrip(raw_config, "conf.yaml")
            await default_context_cache.load_from_config(validated_config)

            return JSONResponse(
                {
                    "ok": True,
                    "message": "Agent settings saved and reloaded.",
                    **_get_agent_editor_payload(),
                }
            )
        except Exception as e:
            logger.error(f"Failed to update agent editor config: {e}")
            return JSONResponse({"error": str(e)}, status_code=500)

    @router.get("/api/capabilities")
    async def get_capabilities():
        """Return current agent, memory, routing, and MCP capability status."""
        try:
            agent = default_context_cache.agent_engine
            agent_caps = (
                agent.get_capabilities()
                if agent and hasattr(agent, "get_capabilities")
                else {}
            )
            mcp_servers = {}
            if default_context_cache.mcp_server_registery:
                mcp_servers = {
                    name: {
                        "command": server.command,
                        "args": server.args,
                        "available": True,
                    }
                    for name, server in default_context_cache.mcp_server_registery.servers.items()
                }

            return JSONResponse(
                {
                    "agent": agent_caps,
                    "mcp_servers": mcp_servers,
                    "config": {
                        "conf_name": default_context_cache.character_config.conf_name
                        if default_context_cache.character_config
                        else None,
                        "conf_uid": default_context_cache.character_config.conf_uid
                        if default_context_cache.character_config
                        else None,
                    },
                }
            )
        except Exception as e:
            logger.error(f"Failed to get capabilities: {e}")
            return JSONResponse({"error": str(e)}, status_code=500)

    @router.get("/api/memory")
    async def get_long_term_memory():
        """Return local long-term memory items for the current default character."""
        agent = default_context_cache.agent_engine
        if not agent or not hasattr(agent, "list_long_term_memory"):
            return JSONResponse({"enabled": False, "items": []})
        return JSONResponse(
            {
                "enabled": bool(
                    getattr(agent, "get_capabilities", lambda: {})().get(
                        "long_term_memory_enabled", False
                    )
                ),
                "items": agent.list_long_term_memory(),
            }
        )

    @router.delete("/api/memory")
    async def clear_long_term_memory():
        """Clear local long-term memory for the current default character."""
        agent = default_context_cache.agent_engine
        if not agent or not hasattr(agent, "clear_long_term_memory"):
            return JSONResponse({"ok": False, "message": "Long-term memory is not available."})
        cleared = agent.clear_long_term_memory()
        return JSONResponse({"ok": cleared})

    @router.get("/live2d-models/info")
    async def get_live2d_folder_info():
        """Get information about available Live2D models"""
        live2d_dir = "live2d-models"
        if not os.path.exists(live2d_dir):
            return JSONResponse(
                {"error": "Live2D models directory not found"}, status_code=404
            )

        valid_characters = []
        supported_extensions = [".png", ".jpg", ".jpeg"]

        for entry in os.scandir(live2d_dir):
            if entry.is_dir():
                folder_name = entry.name.replace("\\", "/")
                model3_file = os.path.join(
                    live2d_dir, folder_name, f"{folder_name}.model3.json"
                ).replace("\\", "/")

                if os.path.isfile(model3_file):
                    avatar_file = None
                    for ext in supported_extensions:
                        avatar_path = os.path.join(
                            live2d_dir, folder_name, f"{folder_name}{ext}"
                        )
                        if os.path.isfile(avatar_path):
                            avatar_file = avatar_path.replace("\\", "/")
                            break

                    valid_characters.append(
                        {
                            "name": folder_name,
                            "avatar": avatar_file,
                            "model_path": model3_file,
                        }
                    )
        return JSONResponse(
            {
                "type": "live2d-models/info",
                "count": len(valid_characters),
                "characters": valid_characters,
            }
        )

    @router.post("/asr")
    async def transcribe_audio(file: UploadFile = File(...)):
        """
        Endpoint for transcribing audio using the ASR engine
        """
        logger.info(f"Received audio file for transcription: {file.filename}")

        try:
            contents = await file.read()

            if len(contents) < 44:
                raise ValueError("Invalid WAV file: File too small")

            wav_header_size = 44
            audio_data = contents[wav_header_size:]

            if len(audio_data) % 2 != 0:
                raise ValueError("Invalid audio data: Buffer size must be even")

            try:
                audio_array = (
                    np.frombuffer(audio_data, dtype=np.int16).astype(np.float32)
                    / 32768.0
                )
            except ValueError as e:
                raise ValueError(
                    f"Audio format error: {str(e)}. Please ensure the file is 16-bit PCM WAV format."
                )

            if len(audio_array) == 0:
                raise ValueError("Empty audio data")

            text = await default_context_cache.asr_engine.async_transcribe_np(
                audio_array
            )
            logger.info(f"Transcription result: {text}")
            return {"text": text}

        except ValueError as e:
            logger.error(f"Audio format error: {e}")
            return Response(
                content=json.dumps({"error": str(e)}),
                status_code=400,
                media_type="application/json",
            )
        except Exception as e:
            logger.error(f"Error during transcription: {e}")
            return Response(
                content=json.dumps(
                    {"error": "Internal server error during transcription"}
                ),
                status_code=500,
                media_type="application/json",
            )

    @router.websocket("/tts-ws")
    async def tts_endpoint(websocket: WebSocket):
        """WebSocket endpoint for TTS generation"""
        await websocket.accept()
        logger.info("TTS WebSocket connection established")

        try:
            while True:
                data = await websocket.receive_json()
                text = data.get("text")
                if not text:
                    continue

                logger.info(f"Received text for TTS: {text}")

                sentences = [s.strip() for s in text.split(".") if s.strip()]

                try:
                    for sentence in sentences:
                        sentence = sentence + "."
                        file_name = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid4())[:8]}"
                        audio_path = (
                            await default_context_cache.tts_engine.async_generate_audio(
                                text=sentence, file_name_no_ext=file_name
                            )
                        )
                        logger.info(
                            f"Generated audio for sentence: {sentence} at: {audio_path}"
                        )

                        await websocket.send_json(
                            {
                                "status": "partial",
                                "audioPath": audio_path,
                                "text": sentence,
                            }
                        )

                    await websocket.send_json({"status": "complete"})

                except Exception as e:
                    logger.error(f"Error generating TTS: {e}")
                    await websocket.send_json({"status": "error", "message": str(e)})

        except WebSocketDisconnect:
            logger.info("TTS WebSocket client disconnected")
        except Exception as e:
            logger.error(f"Error in TTS WebSocket connection: {e}")
            await websocket.close()

    return router
