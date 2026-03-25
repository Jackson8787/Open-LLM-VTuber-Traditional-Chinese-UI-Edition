# config_manager/tts.py
from pydantic import ValidationInfo, Field, model_validator
from typing import Literal, Optional, Dict, ClassVar
from .i18n import I18nMixin, Description


class AzureTTSConfig(I18nMixin):
    """Configuration for Azure TTS service."""

    api_key: str = Field(..., alias="api_key")
    region: str = Field(..., alias="region")
    voice: str = Field(..., alias="voice")
    pitch: str = Field(..., alias="pitch")
    rate: str = Field(..., alias="rate")

    DESCRIPTIONS: ClassVar[Dict[str, Description]] = {
        "api_key": Description(
            en="API key for Azure TTS service", zh="Azure TTS 服務的 API 金鑰"
        ),
        "region": Description(
            en="Azure region (e.g., eastus)", zh="Azure 區域（如 eastus）"
        ),
        "voice": Description(
            en="Voice name to use for Azure TTS", zh="Azure TTS 使用的語音名稱"
        ),
        "pitch": Description(en="Pitch adjustment percentage", zh="音高調整百分比"),
        "rate": Description(en="Speaking rate adjustment", zh="語速調整"),
    }


class BarkTTSConfig(I18nMixin):
    """Configuration for Bark TTS."""

    voice: str = Field(..., alias="voice")

    DESCRIPTIONS: ClassVar[Dict[str, Description]] = {
        "voice": Description(
            en="Voice name to use for Bark TTS", zh="Bark TTS 使用的語音名稱"
        ),
    }


class EdgeTTSConfig(I18nMixin):
    """Configuration for Edge TTS."""

    voice: str = Field(..., alias="voice")

    DESCRIPTIONS: ClassVar[Dict[str, Description]] = {
        "voice": Description(
            en="Voice name to use for Edge TTS (use 'edge-tts --list-voices' to list available voices)",
            zh="Edge TTS 使用的語音名稱（使用 'edge-tts --list-voices' 列出可用語音）",
        ),
    }


class CosyvoiceTTSConfig(I18nMixin):
    """Configuration for Cosyvoice TTS."""

    client_url: str = Field(..., alias="client_url")
    mode_checkbox_group: str = Field(..., alias="mode_checkbox_group")
    sft_dropdown: str = Field(..., alias="sft_dropdown")
    prompt_text: str = Field(..., alias="prompt_text")
    prompt_wav_upload_url: str = Field(..., alias="prompt_wav_upload_url")
    prompt_wav_record_url: str = Field(..., alias="prompt_wav_record_url")
    instruct_text: str = Field(..., alias="instruct_text")
    seed: int = Field(..., alias="seed")
    api_name: str = Field(..., alias="api_name")

    DESCRIPTIONS: ClassVar[Dict[str, Description]] = {
        "client_url": Description(
            en="URL of the CosyVoice Gradio web UI", zh="CosyVoice Gradio Web UI 的 URL"
        ),
        "mode_checkbox_group": Description(
            en="Mode checkbox group value", zh="模式核取方塊群組值"
        ),
        "sft_dropdown": Description(en="SFT dropdown value", zh="SFT 下拉選單值"),
        "prompt_text": Description(en="Prompt text", zh="提示文字"),
        "prompt_wav_upload_url": Description(
            en="URL for prompt WAV file upload", zh="提示音訊檔上傳 URL"
        ),
        "prompt_wav_record_url": Description(
            en="URL for prompt WAV file recording", zh="提示音訊錄製 URL"
        ),
        "instruct_text": Description(en="Instruction text", zh="指令文字"),
        "seed": Description(en="Random seed", zh="隨機種子"),
        "api_name": Description(en="API endpoint name", zh="API 端点名称"),
    }


class Cosyvoice2TTSConfig(I18nMixin):
    """Configuration for Cosyvoice2 TTS."""

    client_url: str = Field(..., alias="client_url")
    mode_checkbox_group: str = Field(..., alias="mode_checkbox_group")
    sft_dropdown: str = Field(..., alias="sft_dropdown")
    prompt_text: str = Field(..., alias="prompt_text")
    prompt_wav_upload_url: str = Field(..., alias="prompt_wav_upload_url")
    prompt_wav_record_url: str = Field(..., alias="prompt_wav_record_url")
    instruct_text: str = Field(..., alias="instruct_text")
    stream: bool = Field(..., alias="stream")
    seed: int = Field(..., alias="seed")
    speed: float = Field(..., alias="speed")
    api_name: str = Field(..., alias="api_name")

    DESCRIPTIONS: ClassVar[Dict[str, Description]] = {
        "client_url": Description(
            en="URL of the CosyVoice Gradio web UI", zh="CosyVoice Gradio Web UI 的 URL"
        ),
        "mode_checkbox_group": Description(
            en="Mode checkbox group value", zh="模式核取方塊群組值"
        ),
        "sft_dropdown": Description(en="SFT dropdown value", zh="SFT 下拉選單值"),
        "prompt_text": Description(en="Prompt text", zh="提示文字"),
        "prompt_wav_upload_url": Description(
            en="URL for prompt WAV file upload", zh="提示音訊檔上傳 URL"
        ),
        "prompt_wav_record_url": Description(
            en="URL for prompt WAV file recording", zh="提示音訊錄製 URL"
        ),
        "instruct_text": Description(en="Instruction text", zh="指令文字"),
        "stream": Description(en="Streaming inference", zh="串流推論"),
        "seed": Description(en="Random seed", zh="隨機種子"),
        "speed": Description(en="Speech speed multiplier", zh="語速倍率"),
        "api_name": Description(en="API endpoint name", zh="API 端點名稱"),
    }


class MeloTTSConfig(I18nMixin):
    """Configuration for Melo TTS."""

    speaker: str = Field(..., alias="speaker")
    language: str = Field(..., alias="language")
    device: str = Field("auto", alias="device")
    speed: float = Field(1.0, alias="speed")

    DESCRIPTIONS: ClassVar[Dict[str, Description]] = {
        "speaker": Description(
            en="Speaker name (e.g., EN-Default, ZH)",
            zh="說話人名稱（如 EN-Default、ZH）",
        ),
        "language": Description(
            en="Language code (e.g., EN, ZH)", zh="語言代碼（如 EN、ZH）"
        ),
        "device": Description(
            en="Device to use (auto, cpu, cuda, cuda:0, mps)",
            zh="使用的裝置（auto、cpu、cuda、cuda:0、mps）",
        ),
        "speed": Description(en="Speech speed multiplier", zh="語速倍率"),
    }


class XTTSConfig(I18nMixin):
    """Configuration for XTTS."""

    api_url: str = Field(..., alias="api_url")
    speaker_wav: str = Field(..., alias="speaker_wav")
    language: str = Field(..., alias="language")

    DESCRIPTIONS: ClassVar[Dict[str, Description]] = {
        "api_url": Description(
            en="URL of the XTTS API endpoint", zh="XTTS API 端點 URL"
        ),
        "speaker_wav": Description(
            en="Speaker reference WAV file", zh="說話人參考音訊檔"
        ),
        "language": Description(
            en="Language code (e.g., en, zh)", zh="語言代碼（如 en、zh）"
        ),
    }


class GPTSoVITSConfig(I18nMixin):
    """Configuration for GPT-SoVITS."""

    api_url: str = Field(..., alias="api_url")
    text_lang: str = Field(..., alias="text_lang")
    ref_audio_path: str = Field(..., alias="ref_audio_path")
    prompt_lang: str = Field(..., alias="prompt_lang")
    prompt_text: str = Field(..., alias="prompt_text")
    text_split_method: str = Field(..., alias="text_split_method")
    batch_size: str = Field(..., alias="batch_size")
    media_type: str = Field(..., alias="media_type")
    streaming_mode: str = Field(..., alias="streaming_mode")

    DESCRIPTIONS: ClassVar[Dict[str, Description]] = {
        "api_url": Description(
            en="URL of the GPT-SoVITS API endpoint", zh="GPT-SoVITS API 端點 URL"
        ),
        "text_lang": Description(en="Language of the input text", zh="輸入文字的語言"),
        "ref_audio_path": Description(
            en="Path to reference audio file", zh="參考音訊檔路徑"
        ),
        "prompt_lang": Description(en="Language of the prompt", zh="提示詞語言"),
        "prompt_text": Description(en="Prompt text", zh="提示文字"),
        "text_split_method": Description(
            en="Method for splitting text", zh="文字切分方式"
        ),
        "batch_size": Description(en="Batch size for processing", zh="處理批次大小"),
        "media_type": Description(en="Output media type", zh="輸出媒體類型"),
        "streaming_mode": Description(en="Enable streaming mode", zh="啟用串流模式"),
    }


class FishAPITTSConfig(I18nMixin):
    """Configuration for Fish API TTS."""

    api_key: str = Field(..., alias="api_key")
    reference_id: str = Field(..., alias="reference_id")
    latency: Literal["normal", "balanced"] = Field(..., alias="latency")
    base_url: str = Field(..., alias="base_url")

    DESCRIPTIONS: ClassVar[Dict[str, Description]] = {
        "api_key": Description(
            en="API key for Fish TTS service", zh="Fish TTS 服務的 API 金鑰"
        ),
        "reference_id": Description(
            en="Voice reference ID from Fish Audio website",
            zh="來自 Fish Audio 網站的語音參考 ID",
        ),
        "latency": Description(
            en="Latency mode (normal or balanced)", zh="延遲模式（normal 或 balanced）"
        ),
        "base_url": Description(
            en="Base URL for Fish TTS API", zh="Fish TTS API 的基礎 URL"
        ),
    }


class CoquiTTSConfig(I18nMixin):
    """Configuration for Coqui TTS."""

    model_name: str = Field(..., alias="model_name")
    speaker_wav: str = Field("", alias="speaker_wav")
    language: str = Field(..., alias="language")
    device: str = Field("", alias="device")

    DESCRIPTIONS: ClassVar[Dict[str, Description]] = {
        "model_name": Description(
            en="Name of the TTS model to use", zh="要使用的 TTS 模型名稱"
        ),
        "speaker_wav": Description(
            en="Path to speaker WAV file for voice cloning",
            zh="用於聲音複製的說話人音訊檔路徑",
        ),
        "language": Description(
            en="Language code (e.g., en, zh)", zh="語言代碼（如 en、zh）"
        ),
        "device": Description(
            en="Device to use (cuda, cpu, or empty for auto)",
            zh="使用的裝置（cuda、cpu 或留空以自動選擇）",
        ),
    }


class SherpaOnnxTTSConfig(I18nMixin):
    """Configuration for Sherpa Onnx TTS."""

    vits_model: str = Field(..., alias="vits_model")
    vits_lexicon: Optional[str] = Field(None, alias="vits_lexicon")
    vits_tokens: str = Field(..., alias="vits_tokens")
    vits_data_dir: Optional[str] = Field(None, alias="vits_data_dir")
    vits_dict_dir: Optional[str] = Field(None, alias="vits_dict_dir")
    tts_rule_fsts: Optional[str] = Field(None, alias="tts_rule_fsts")
    max_num_sentences: int = Field(2, alias="max_num_sentences")
    sid: int = Field(1, alias="sid")
    provider: Literal["cpu", "cuda", "coreml"] = Field("cpu", alias="provider")
    num_threads: int = Field(1, alias="num_threads")
    speed: float = Field(1.0, alias="speed")
    debug: bool = Field(False, alias="debug")

    DESCRIPTIONS: ClassVar[Dict[str, Description]] = {
        "vits_model": Description(en="Path to VITS model file", zh="VITS 模型檔案路徑"),
        "vits_lexicon": Description(
            en="Path to lexicon file (optional)", zh="詞典檔案路徑（可選）"
        ),
        "vits_tokens": Description(en="Path to tokens file", zh="詞元檔案路徑"),
        "vits_data_dir": Description(
            en="Path to espeak-ng data directory (optional)",
            zh="espeak-ng 資料目錄路徑（可選）",
        ),
        "vits_dict_dir": Description(
            en="Path to Jieba dictionary directory (optional)",
            zh="結巴詞典目錄路徑（可選）",
        ),
        "tts_rule_fsts": Description(
            en="Path to rule FSTs file (optional)", zh="規則 FST 檔案路徑（可選）"
        ),
        "max_num_sentences": Description(
            en="Maximum number of sentences per batch", zh="每批次最大句子數"
        ),
        "sid": Description(
            en="Speaker ID for multi-speaker models", zh="多說話人模型的說話人 ID"
        ),
        "provider": Description(
            en="Computation provider (cpu, cuda, or coreml)",
            zh="運算提供者（cpu、cuda 或 coreml）",
        ),
        "num_threads": Description(en="Number of computation threads", zh="運算執行緒數"),
        "speed": Description(en="Speech speed multiplier", zh="語速倍率"),
        "debug": Description(en="Enable debug mode", zh="啟用除錯模式"),
    }


class SiliconFlowTTSConfig(I18nMixin):
    """Configuration for SiliconFlow TTS."""

    api_url: str = Field("https://api.siliconflow.cn/v1/audio/speech", alias="api_url")
    api_key: str = Field(..., alias="api_key")
    default_model: str = Field("FunAudioLLM/CosyVoice2-0.5B", alias="default_model")
    default_voice: str = Field(
        "speech:Dreamflowers:5bdstvc39i:xkqldnpasqmoqbakubom", alias="default_voice"
    )
    sample_rate: int = Field(32000, alias="sample_rate")
    response_format: str = Field("mp3", alias="response_format")
    stream: bool = Field(True, alias="stream")
    speed: float = Field(1, alias="speed")
    gain: int = Field(0, alias="gain")

    DESCRIPTIONS: ClassVar[Dict[str, Description]] = {
        "api_key": Description(
            en="API key for SiliconFlow TTS service",
            zh="SiliconFlow TTS 服務的 API 金鑰",
        ),
        "url": Description(
            en="API endpoint URL for SiliconFlow TTS",
            zh="SiliconFlow TTS 的 API 端點 URL",
        ),
        "model": Description(
            en="Model to use for SiliconFlow TTS", zh="SiliconFlow TTS 使用的模型"
        ),
        "voice": Description(
            en="Voice name to use for SiliconFlow TTS",
            zh="SiliconFlow TTS 使用的語音名稱",
        ),
        "sample_rate": Description(
            en="Sample rate of the output audio", zh="輸出音訊的取樣率"
        ),
        "stream": Description(en="Enable streaming mode", zh="啟用串流模式"),
        "speed": Description(en="Speaking speed multiplier", zh="語速倍率"),
        "gain": Description(en="Audio gain adjustment", zh="音訊增益調整"),
    }


class OpenAITTSConfig(I18nMixin):
    """Configuration for OpenAI-compatible TTS client."""

    model: Optional[str] = Field(None, alias="model")
    voice: Optional[str] = Field(None, alias="voice")
    api_key: Optional[str] = Field(None, alias="api_key")
    base_url: Optional[str] = Field(None, alias="base_url")
    file_extension: Literal["mp3", "wav"] = Field("mp3", alias="file_extension")

    DESCRIPTIONS: ClassVar[Dict[str, Description]] = {
        "model": Description(
            en="Model name for the TTS server (overrides default)",
            zh="TTS 伺服器的模型名稱（覆蓋預設值）",
        ),
        "voice": Description(
            en="Voice name(s) for the TTS server (overrides default)",
            zh="TTS 伺服器的語音名稱（覆蓋預設值）",
        ),
        "api_key": Description(
            en="API key if required by the TTS server (overrides default)",
            zh="TTS 伺服器所需的 API 金鑰（覆蓋預設值）",
        ),
        "base_url": Description(
            en="Base URL of the TTS server (overrides default)",
            zh="TTS 伺服器的基礎 URL（覆蓋預設值）",
        ),
        "file_extension": Description(
            en="Audio file format (mp3 or wav, defaults to mp3)",
            zh="音訊檔案格式（mp3 或 wav，預設為 mp3）",
        ),
    }


class SparkTTSConfig(I18nMixin):
    """Configuration for Spark TTS."""

    api_url: str = Field(..., alias="api_url")
    prompt_wav_upload: str = Field(..., alias="prompt_wav_upload")
    api_name: str = Field(..., alias="api_name")
    gender: str = Field(..., alias="gender")
    pitch: int = Field(..., alias="pitch")
    speed: int = Field(..., alias="speed")

    DESCRIPTIONS: ClassVar[Dict[str, Description]] = {
        "prompt_wav_upload": Description(
            en="Reference audio (used when using voice cloning)",
            zh="參考音訊（進行聲音複製時使用）",
        ),
        "api_url": Description(
            en="API address of the spark tts gradio web frontend. For example: http://127.0.0.1:7860/voice_clone",
            zh="你的 API 位址，例如：http://127.0.0.1:7860/voice_clone",
        ),
        "api_name": Description(
            en="The API endpoint name. For example: voice_clone,voice_creation",
            zh="你的 API 名稱，例如：voice_clone、voice_creation",
        ),
        "gender": Description(
            en="Gender of the voice (male or female)", zh="聲音性別（男或女）"
        ),
        "pitch": Description(
            en="Pitch shift (in semitones) default 3,range 1-5.",
            zh="音高（以半音為單位），預設 3，範圍 1-5",
        ),
        "speed": Description(
            en="Speed of the voice (in percent) default 3,range 1-5.",
            zh="聲音速度（以百分比為單位），預設 3，範圍 1-5",
        ),
    }


class MinimaxTTSConfig(I18nMixin):
    """Configuration for Minimax TTS."""

    group_id: str = Field(..., alias="group_id")
    api_key: str = Field(..., alias="api_key")
    model: str = Field("speech-02-turbo", alias="model")
    voice_id: str = Field("male-qn-qingse", alias="voice_id")
    pronunciation_dict: str = Field("", alias="pronunciation_dict")

    DESCRIPTIONS: ClassVar[Dict[str, Description]] = {
        "group_id": Description(en="Minimax group_id", zh="Minimax 的 group_id"),
        "api_key": Description(en="Minimax API key", zh="Minimax 的 API key"),
        "model": Description(en="Minimax model name", zh="Minimax 模型名稱"),
        "voice_id": Description(en="Minimax voice id", zh="Minimax 語音 ID"),
        "pronunciation_dict": Description(
            en="Custom pronunciation dictionary (string)", zh="自訂發音字典（字串）"
        ),
    }


class TTSConfig(I18nMixin):
    """Configuration for Text-to-Speech."""

    tts_model: Literal[
        "azure_tts",
        "bark_tts",
        "edge_tts",
        "cosyvoice_tts",
        "cosyvoice2_tts",
        "melo_tts",
        "coqui_tts",
        "x_tts",
        "gpt_sovits_tts",
        "fish_api_tts",
        "sherpa_onnx_tts",
        "siliconflow_tts",
        "openai_tts",  # Add openai_tts here
        "spark_tts",
        "minimax_tts",
    ] = Field(..., alias="tts_model")

    azure_tts: Optional[AzureTTSConfig] = Field(None, alias="azure_tts")
    bark_tts: Optional[BarkTTSConfig] = Field(None, alias="bark_tts")
    edge_tts: Optional[EdgeTTSConfig] = Field(None, alias="edge_tts")
    cosyvoice_tts: Optional[CosyvoiceTTSConfig] = Field(None, alias="cosyvoice_tts")
    cosyvoice2_tts: Optional[Cosyvoice2TTSConfig] = Field(None, alias="cosyvoice2_tts")
    melo_tts: Optional[MeloTTSConfig] = Field(None, alias="melo_tts")
    coqui_tts: Optional[CoquiTTSConfig] = Field(None, alias="coqui_tts")
    x_tts: Optional[XTTSConfig] = Field(None, alias="x_tts")
    gpt_sovits_tts: Optional[GPTSoVITSConfig] = Field(None, alias="gpt_sovits")
    fish_api_tts: Optional[FishAPITTSConfig] = Field(None, alias="fish_api_tts")
    sherpa_onnx_tts: Optional[SherpaOnnxTTSConfig] = Field(
        None, alias="sherpa_onnx_tts"
    )
    siliconflow_tts: Optional[SiliconFlowTTSConfig] = Field(
        None, alias="siliconflow_tts"
    )
    openai_tts: Optional[OpenAITTSConfig] = Field(None, alias="openai_tts")
    spark_tts: Optional[SparkTTSConfig] = Field(None, alias="spark_tts")
    minimax_tts: Optional[MinimaxTTSConfig] = Field(None, alias="minimax_tts")

    DESCRIPTIONS: ClassVar[Dict[str, Description]] = {
        "tts_model": Description(
            en="Text-to-speech model to use", zh="要使用的文字轉語音模型"
        ),
        "azure_tts": Description(en="Configuration for Azure TTS", zh="Azure TTS 設定"),
        "bark_tts": Description(en="Configuration for Bark TTS", zh="Bark TTS 設定"),
        "edge_tts": Description(en="Configuration for Edge TTS", zh="Edge TTS 設定"),
        "cosyvoice_tts": Description(
            en="Configuration for Cosyvoice TTS", zh="Cosyvoice TTS 設定"
        ),
        "cosyvoice2_tts": Description(
            en="Configuration for Cosyvoice2 TTS", zh="Cosyvoice2 TTS 設定"
        ),
        "melo_tts": Description(en="Configuration for Melo TTS", zh="Melo TTS 設定"),
        "coqui_tts": Description(en="Configuration for Coqui TTS", zh="Coqui TTS 設定"),
        "x_tts": Description(en="Configuration for XTTS", zh="XTTS 設定"),
        "gpt_sovits_tts": Description(
            en="Configuration for GPT-SoVITS", zh="GPT-SoVITS 設定"
        ),
        "fish_api_tts": Description(
            en="Configuration for Fish API TTS", zh="Fish API TTS 設定"
        ),
        "sherpa_onnx_tts": Description(
            en="Configuration for Sherpa Onnx TTS", zh="Sherpa Onnx TTS 設定"
        ),
        "siliconflow_tts": Description(
            en="Configuration for SiliconFlow TTS", zh="SiliconFlow TTS 設定"
        ),
        "openai_tts": Description(
            en="Configuration for OpenAI-compatible TTS", zh="OpenAI 相容 TTS 設定"
        ),
        "spark_tts": Description(en="Configuration for Spark TTS", zh="Spark TTS 設定"),
        "minimax_tts": Description(
            en="Configuration for Minimax TTS", zh="Minimax TTS 設定"
        ),
    }

    @model_validator(mode="after")
    def check_tts_config(cls, values: "TTSConfig", info: ValidationInfo):
        tts_model = values.tts_model

        # Only validate the selected TTS model
        if tts_model == "azure_tts" and values.azure_tts is not None:
            values.azure_tts.model_validate(values.azure_tts.model_dump())
        elif tts_model == "bark_tts" and values.bark_tts is not None:
            values.bark_tts.model_validate(values.bark_tts.model_dump())
        elif tts_model == "edge_tts" and values.edge_tts is not None:
            values.edge_tts.model_validate(values.edge_tts.model_dump())
        elif tts_model == "cosyvoice_tts" and values.cosyvoice_tts is not None:
            values.cosyvoice_tts.model_validate(values.cosyvoice_tts.model_dump())
        elif tts_model == "cosyvoice2_tts" and values.cosyvoice2_tts is not None:
            values.cosyvoice2_tts.model_validate(values.cosyvoice2_tts.model_dump())
        elif tts_model == "melo_tts" and values.melo_tts is not None:
            values.melo_tts.model_validate(values.melo_tts.model_dump())
        elif tts_model == "coqui_tts" and values.coqui_tts is not None:
            values.coqui_tts.model_validate(values.coqui_tts.model_dump())
        elif tts_model == "x_tts" and values.x_tts is not None:
            values.x_tts.model_validate(values.x_tts.model_dump())
        elif tts_model == "gpt_sovits_tts" and values.gpt_sovits_tts is not None:
            values.gpt_sovits_tts.model_validate(values.gpt_sovits_tts.model_dump())
        elif tts_model == "fish_api_tts" and values.fish_api_tts is not None:
            values.fish_api_tts.model_validate(values.fish_api_tts.model_dump())
        elif tts_model == "sherpa_onnx_tts" and values.sherpa_onnx_tts is not None:
            values.sherpa_onnx_tts.model_validate(values.sherpa_onnx_tts.model_dump())
        elif tts_model == "siliconflow_tts" and values.siliconflow_tts is not None:
            values.siliconflow_tts.model_validate(values.siliconflow_tts.model_dump())
        elif tts_model == "openai_tts" and values.openai_tts is not None:
            values.openai_tts.model_validate(values.openai_tts.model_dump())
        elif tts_model == "spark_tts" and values.spark_tts is not None:
            values.spark_tts.model_validate(values.spark_tts.model_dump())
        elif tts_model == "minimax_tts" and values.minimax_tts is not None:
            values.minimax_tts.model_validate(values.minimax_tts.model_dump())

        return values
