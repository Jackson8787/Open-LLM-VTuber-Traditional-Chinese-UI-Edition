const API_BASE_URL = window.location.origin;
const recorder = new AudioRecorder();

let audioContext = null;
let audioBuffers = [];
let pendingAudioPaths = new Set();
let currentAudioPath = null;
let ws = null;
let agentEditorState = null;
const AGENT_EDITOR_CACHE_KEY = 'open-llm-vtuber:agent-editor-cache';

const startRecordingBtn = document.getElementById('startRecording');
const stopRecordingBtn = document.getElementById('stopRecording');
const transcriptionArea = document.getElementById('transcription');
const asrStatus = document.getElementById('asrStatus');
const ttsInput = document.getElementById('ttsInput');
const generateSpeechBtn = document.getElementById('generateSpeech');
const ttsStatus = document.getElementById('ttsStatus');
const audioPlayer = document.getElementById('audioPlayer');
const downloadAudioBtn = document.getElementById('downloadAudio');
const audioFileInput = document.getElementById('audioFileInput');
const uploadAudioBtn = document.getElementById('uploadAudio');
const llmProviderSelect = document.getElementById('llmProvider');
const providerFields = document.getElementById('providerFields');
const systemPromptInput = document.getElementById('systemPrompt');
const saveAgentConfigBtn = document.getElementById('saveAgentConfig');
const agentConfigStatus = document.getElementById('agentConfigStatus');
const longTermMemoryEnabledInput = document.getElementById('longTermMemoryEnabled');
const memoryBackendSelect = document.getElementById('memoryBackend');
const memoryMaxItemsInput = document.getElementById('memoryMaxItems');
const clearLongTermMemoryBtn = document.getElementById('clearLongTermMemory');
const modelRoutingEnabledInput = document.getElementById('modelRoutingEnabled');
const routingDefaultModelSelect = document.getElementById('routingDefaultModel');
const routingChatModelSelect = document.getElementById('routingChatModel');
const routingVisionModelSelect = document.getElementById('routingVisionModel');
const routingToolModelSelect = document.getElementById('routingToolModel');
const routingSimpleModelSelect = document.getElementById('routingSimpleModel');
const routingSimpleQueryMaxCharsInput = document.getElementById('routingSimpleQueryMaxChars');
const mcpEnabledInput = document.getElementById('mcpEnabled');
const mcpEnabledServersInput = document.getElementById('mcpEnabledServers');
const availableMcpServersText = document.getElementById('availableMcpServers');

function setStatus(element, message, type = '') {
    element.textContent = message;
    element.className = type ? `status ${type}` : 'status';
}

function saveAgentEditorCache() {
    try {
        localStorage.setItem(AGENT_EDITOR_CACHE_KEY, JSON.stringify({
            llm_provider: llmProviderSelect.value,
            provider_config: collectProviderConfig(),
            system_prompt: systemPromptInput.value,
            long_term_memory_enabled: longTermMemoryEnabledInput.checked,
            memory_backend: memoryBackendSelect.value,
            memory_max_items: Number.parseInt(memoryMaxItemsInput.value, 10) || 80,
            use_mcpp: mcpEnabledInput.checked,
            mcp_enabled_servers: parseServerList(mcpEnabledServersInput.value),
            model_routing: collectModelRouting()
        }));
    } catch (error) {
        console.warn('Failed to save agent editor cache:', error);
    }
}

function loadAgentEditorCache() {
    try {
        const raw = localStorage.getItem(AGENT_EDITOR_CACHE_KEY);
        return raw ? JSON.parse(raw) : null;
    } catch (error) {
        console.warn('Failed to load agent editor cache:', error);
        return null;
    }
}

function applyAgentEditorCache(cache) {
    if (!cache || !agentEditorState) {
        return;
    }

    if (cache.llm_provider && agentEditorState.providers.some(provider => provider.name === cache.llm_provider)) {
        llmProviderSelect.value = cache.llm_provider;
        renderProviderFields(cache.llm_provider);
    }

    if (cache.system_prompt !== undefined) {
        systemPromptInput.value = cache.system_prompt ?? '';
    }

    if (cache.long_term_memory_enabled !== undefined) {
        longTermMemoryEnabledInput.checked = Boolean(cache.long_term_memory_enabled);
    }
    if (cache.memory_backend) {
        memoryBackendSelect.value = cache.memory_backend;
    }
    if (cache.memory_max_items !== undefined) {
        memoryMaxItemsInput.value = cache.memory_max_items;
    }
    if (cache.use_mcpp !== undefined) {
        mcpEnabledInput.checked = Boolean(cache.use_mcpp);
    }
    if (cache.mcp_enabled_servers) {
        mcpEnabledServersInput.value = cache.mcp_enabled_servers.join(', ');
    }
    if (cache.model_routing) {
        applyModelRouting(cache.model_routing);
    }

    if (!cache.provider_config) {
        return;
    }

    providerFields.querySelectorAll('[data-field-key]').forEach(input => {
        const key = input.dataset.fieldKey;
        if (!(key in cache.provider_config)) {
            return;
        }

        const value = cache.provider_config[key];
        input.value = value ?? '';
    });
}

function renderRoutingProviderSelects() {
    if (!agentEditorState) {
        return;
    }

    const selects = [
        routingDefaultModelSelect,
        routingChatModelSelect,
        routingVisionModelSelect,
        routingToolModelSelect,
        routingSimpleModelSelect
    ];
    selects.forEach(select => {
        select.innerHTML = '<option value="">Fallback to active provider</option>';
        agentEditorState.providers.forEach(provider => {
            const option = document.createElement('option');
            option.value = provider.name;
            option.textContent = provider.name;
            select.appendChild(option);
        });
    });
}

function applyModelRouting(routing = {}) {
    modelRoutingEnabledInput.checked = Boolean(routing.enabled);
    routingDefaultModelSelect.value = routing.default_model || '';
    routingChatModelSelect.value = routing.chat_model || '';
    routingVisionModelSelect.value = routing.vision_model || '';
    routingToolModelSelect.value = routing.tool_model || '';
    routingSimpleModelSelect.value = routing.simple_model || '';
    routingSimpleQueryMaxCharsInput.value = routing.simple_query_max_chars || 32;
}

function renderProviderFields(providerName) {
    if (!agentEditorState) {
        return;
    }

    const provider = agentEditorState.providers.find(item => item.name === providerName);
    providerFields.innerHTML = '';

    if (!provider) {
        return;
    }

    provider.fields.forEach(field => {
        const wrapper = document.createElement('div');
        wrapper.className = 'field-card';

        const label = document.createElement('label');
        label.textContent = field.key;
        label.htmlFor = `provider-field-${field.key}`;

        let input;
        if (field.type === 'boolean') {
            input = document.createElement('select');
            input.innerHTML = '<option value="true">true</option><option value="false">false</option>';
            input.value = String(field.value);
        } else {
            input = document.createElement('input');
            input.type = field.type === 'integer' || field.type === 'number' ? 'number' : 'text';
            if (field.type === 'number') {
                input.step = 'any';
            }
            input.value = field.value ?? '';
        }

        input.id = `provider-field-${field.key}`;
        input.dataset.fieldKey = field.key;
        input.dataset.fieldType = field.type;

        wrapper.appendChild(label);
        wrapper.appendChild(input);
        providerFields.appendChild(wrapper);
    });
}

async function loadAgentEditorConfig() {
    try {
        setStatus(agentConfigStatus, 'Loading agent settings...');
        const response = await fetch(`${API_BASE_URL}/api/config/agent-editor`);
        if (!response.ok) {
            throw new Error('Failed to load agent settings');
        }

        agentEditorState = await response.json();
        llmProviderSelect.innerHTML = '';

        agentEditorState.providers.forEach(provider => {
            const option = document.createElement('option');
            option.value = provider.name;
            option.textContent = provider.name;
            llmProviderSelect.appendChild(option);
        });

        llmProviderSelect.value = agentEditorState.llm_provider;
        systemPromptInput.value = agentEditorState.system_prompt || '';
        longTermMemoryEnabledInput.checked = Boolean(agentEditorState.long_term_memory_enabled);
        memoryBackendSelect.value = agentEditorState.memory_backend || 'json';
        memoryMaxItemsInput.value = agentEditorState.memory_max_items || 80;
        mcpEnabledInput.checked = Boolean(agentEditorState.use_mcpp);
        mcpEnabledServersInput.value = (agentEditorState.mcp_enabled_servers || []).join(', ');
        availableMcpServersText.textContent = `Available MCP servers: ${(agentEditorState.available_mcp_servers || []).join(', ') || 'none'}`;
        renderRoutingProviderSelects();
        applyModelRouting(agentEditorState.model_routing || {});
        renderProviderFields(agentEditorState.llm_provider);
        applyAgentEditorCache(loadAgentEditorCache());
        setStatus(agentConfigStatus, 'Agent settings loaded.', 'success');
    } catch (error) {
        setStatus(agentConfigStatus, `Error: ${error.message}`, 'error');
    }
}

function parseServerList(value) {
    return String(value || '')
        .split(',')
        .map(item => item.trim())
        .filter(Boolean);
}

function collectModelRouting() {
    return {
        enabled: modelRoutingEnabledInput.checked,
        default_model: routingDefaultModelSelect.value || null,
        chat_model: routingChatModelSelect.value || null,
        vision_model: routingVisionModelSelect.value || null,
        tool_model: routingToolModelSelect.value || null,
        simple_model: routingSimpleModelSelect.value || null,
        simple_query_max_chars: Number.parseInt(routingSimpleQueryMaxCharsInput.value, 10) || 32
    };
}

function collectProviderConfig() {
    const config = {};
    providerFields.querySelectorAll('[data-field-key]').forEach(input => {
        const key = input.dataset.fieldKey;
        const type = input.dataset.fieldType;
        let value = input.value;

        if (type === 'boolean') {
            value = value === 'true';
        } else if (type === 'integer') {
            value = value === '' ? null : Number.parseInt(value, 10);
        } else if (type === 'number') {
            value = value === '' ? null : Number.parseFloat(value);
        } else if (value === 'null') {
            value = null;
        }

        config[key] = value;
    });

    return config;
}

llmProviderSelect.addEventListener('change', () => {
    renderProviderFields(llmProviderSelect.value);
    saveAgentEditorCache();
});

systemPromptInput.addEventListener('input', () => {
    saveAgentEditorCache();
});

providerFields.addEventListener('input', () => {
    saveAgentEditorCache();
});

providerFields.addEventListener('change', () => {
    saveAgentEditorCache();
});

[
    longTermMemoryEnabledInput,
    memoryBackendSelect,
    memoryMaxItemsInput,
    modelRoutingEnabledInput,
    routingDefaultModelSelect,
    routingChatModelSelect,
    routingVisionModelSelect,
    routingToolModelSelect,
    routingSimpleModelSelect,
    routingSimpleQueryMaxCharsInput,
    mcpEnabledInput,
    mcpEnabledServersInput
].forEach(element => {
    element.addEventListener('input', saveAgentEditorCache);
    element.addEventListener('change', saveAgentEditorCache);
});

saveAgentConfigBtn.addEventListener('click', async () => {
    try {
        saveAgentConfigBtn.disabled = true;
        setStatus(agentConfigStatus, 'Saving agent settings...');

        const response = await fetch(`${API_BASE_URL}/api/config/agent-editor`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                llm_provider: llmProviderSelect.value,
                provider_config: collectProviderConfig(),
                system_prompt: systemPromptInput.value,
                long_term_memory_enabled: longTermMemoryEnabledInput.checked,
                memory_backend: memoryBackendSelect.value,
                memory_max_items: Number.parseInt(memoryMaxItemsInput.value, 10) || 80,
                use_mcpp: mcpEnabledInput.checked,
                mcp_enabled_servers: parseServerList(mcpEnabledServersInput.value),
                model_routing: collectModelRouting()
            })
        });

        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.error || 'Failed to save agent settings');
        }

        agentEditorState = data;
        renderRoutingProviderSelects();
        applyModelRouting(agentEditorState.model_routing || {});
        renderProviderFields(agentEditorState.llm_provider);
        saveAgentEditorCache();
        setStatus(agentConfigStatus, 'Agent settings saved. New sessions will use the updated LLM and prompt.', 'success');
    } catch (error) {
        setStatus(agentConfigStatus, `Error: ${error.message}`, 'error');
    } finally {
        saveAgentConfigBtn.disabled = false;
    }
});

clearLongTermMemoryBtn.addEventListener('click', async () => {
    try {
        clearLongTermMemoryBtn.disabled = true;
        setStatus(agentConfigStatus, 'Clearing long-term memory...');
        const response = await fetch(`${API_BASE_URL}/api/memory`, {
            method: 'DELETE'
        });
        const data = await response.json();
        if (!response.ok || !data.ok) {
            throw new Error(data.message || 'Long-term memory is not enabled');
        }
        setStatus(agentConfigStatus, 'Long-term memory cleared.', 'success');
    } catch (error) {
        setStatus(agentConfigStatus, `Error: ${error.message}`, 'error');
    } finally {
        clearLongTermMemoryBtn.disabled = false;
    }
});

uploadAudioBtn.addEventListener('click', async () => {
    const file = audioFileInput.files[0];
    if (!file) {
        asrStatus.textContent = 'Please select an audio file';
        asrStatus.className = 'status error';
        return;
    }

    try {
        asrStatus.textContent = 'Processing audio file...';
        asrStatus.className = 'status';

        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const arrayBuffer = await file.arrayBuffer();
        const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);
        
        const wavBuffer = await audioBufferToWav(audioBuffer);
        const wavBlob = new Blob([wavBuffer], { type: 'audio/wav' });

        const formData = new FormData();
        formData.append('file', wavBlob, 'recording.wav');

        const response = await fetch(`${API_BASE_URL}/asr`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) throw new Error('ASR request failed');

        const data = await response.json();
        transcriptionArea.value = data.text;
        asrStatus.textContent = 'Transcription complete!';
        asrStatus.className = 'status success';
        
        audioContext.close();
    } catch (error) {
        asrStatus.textContent = 'Error: ' + error.message;
        asrStatus.className = 'status error';
    }
});

startRecordingBtn.addEventListener('click', async () => {
    try {
        asrStatus.textContent = 'Starting recording...';
        asrStatus.className = 'status';
        await recorder.start();
        startRecordingBtn.disabled = true;
        stopRecordingBtn.disabled = false;
        asrStatus.textContent = 'Recording...';
    } catch (error) {
        asrStatus.textContent = 'Error starting recording: ' + error.message;
        asrStatus.className = 'status error';
    }
});

stopRecordingBtn.addEventListener('click', async () => {
    try {
        const audioBlob = await recorder.stop();
        startRecordingBtn.disabled = false;
        stopRecordingBtn.disabled = true;
        asrStatus.textContent = 'Processing audio...';

        const formData = new FormData();
        formData.append('file', audioBlob);

        const response = await fetch(`${API_BASE_URL}/asr`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) throw new Error('ASR request failed');

        const data = await response.json();
        transcriptionArea.value = data.text;
        asrStatus.textContent = 'Transcription complete!';
        asrStatus.className = 'status success';
    } catch (error) {
        asrStatus.textContent = 'Error: ' + error.message;
        asrStatus.className = 'status error';
        startRecordingBtn.disabled = false;
        stopRecordingBtn.disabled = true;
    }
});

function connectWebSocket() {
    const wsProtocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
    ws = new WebSocket(`${wsProtocol}://${window.location.host}/tts-ws`);
    
    ws.onopen = () => {
        console.log('WebSocket connected');
        generateSpeechBtn.disabled = false;
        ttsStatus.textContent = 'Connected to TTS service';
        ttsStatus.className = 'status success';
        
        if (!audioContext) {
            audioContext = new (window.AudioContext || window.webkitAudioContext)();
        } else if (audioContext.state === 'suspended') {
            audioContext.resume();
        }
    };

    ws.onmessage = async (event) => {
        const response = JSON.parse(event.data);
        
        if (response.status === 'partial') {
            ttsStatus.textContent = 'Generating audio...';
            ttsStatus.className = 'status';
            
            try {
                const audioPath = response.audioPath.split('/').pop();
                pendingAudioPaths.add(audioPath);
                
                if (audioContext.state === 'suspended') {
                    await audioContext.resume();
                }
                
                const audioResponse = await fetchWithRetry(`${API_BASE_URL}/cache/${audioPath}`);
                const arrayBuffer = await audioResponse.arrayBuffer();
                
                if (arrayBuffer.byteLength === 0) {
                    throw new Error('Empty audio data received');
                }
                
                const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);
                audioBuffers.push(audioBuffer);
                pendingAudioPaths.delete(audioPath);
            } catch (error) {
                console.error('Error loading audio:', error);
                ttsStatus.textContent = 'Error loading audio: ' + error.message;
                ttsStatus.className = 'status error';
                pendingAudioPaths.clear();
            }
        } else if (response.status === 'complete') {
            if (pendingAudioPaths.size > 0) {
                ttsStatus.textContent = 'Finalizing audio...';
                await new Promise(resolve => setTimeout(resolve, 500));
            }

            try {
                const targetSampleRate = 16000;
                const totalLength = audioBuffers.reduce((acc, buffer) => {
                    const ratio = targetSampleRate / buffer.sampleRate;
                    return acc + Math.ceil(buffer.length * ratio);
                }, 0);
                
                const combinedBuffer = audioContext.createBuffer(
                    1,
                    totalLength,
                    targetSampleRate
                );
                
                let offset = 0;
                for (const buffer of audioBuffers) {
                    let channelData = buffer.getChannelData(0);
                    if (buffer.sampleRate !== targetSampleRate) {
                        channelData = await resampleAudio(channelData, buffer.sampleRate, targetSampleRate);
                    }
                    combinedBuffer.copyToChannel(channelData, 0, offset);
                    offset += channelData.length;
                }
                
                const wavBlob = new Blob([await audioBufferToWav(combinedBuffer)], { type: 'audio/wav' });
                const audioUrl = URL.createObjectURL(wavBlob);
                
                audioPlayer.src = audioUrl;
                audioPlayer.load();
                downloadAudioBtn.disabled = false;
                currentAudioPath = audioUrl;
                
                ttsStatus.textContent = 'Audio generated successfully!';
                ttsStatus.className = 'status success';
            } catch (error) {
                console.error('Error combining audio:', error);
                ttsStatus.textContent = 'Error combining audio: ' + error.message;
                ttsStatus.className = 'status error';
            } finally {
                audioBuffers = [];
                pendingAudioPaths.clear();
            }
        } else if (response.status === 'error') {
            ttsStatus.textContent = 'Error: ' + response.message;
            ttsStatus.className = 'status error';
            audioBuffers = [];
            pendingAudioPaths.clear();
        }
    };

    ws.onclose = () => {
        console.log('WebSocket disconnected');
        generateSpeechBtn.disabled = true;
        ttsStatus.textContent = 'Disconnected. Trying to reconnect...';
        ttsStatus.className = 'status error';
        
        audioBuffers = [];
        pendingAudioPaths.clear();
        if (currentAudioPath) {
            URL.revokeObjectURL(currentAudioPath);
            currentAudioPath = null;
        }
        
        setTimeout(connectWebSocket, 5000);
    };

    ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        ttsStatus.textContent = 'Connection error. Retrying...';
        ttsStatus.className = 'status error';
        
        audioBuffers = [];
        pendingAudioPaths.clear();
        if (currentAudioPath) {
            URL.revokeObjectURL(currentAudioPath);
            currentAudioPath = null;
        }
    };
}

async function audioBufferToWav(buffer) {
    let audioData = buffer.getChannelData(0);
    if (buffer.sampleRate !== 16000) {
        audioData = await resampleAudio(audioData, buffer.sampleRate, 16000);
    }
    
    const numChannels = 1;
    const sampleRate = 16000;
    const format = 1;
    const bitDepth = 16;
    
    const dataLength = audioData.length * (bitDepth / 8);
    const headerLength = 44;
    const totalLength = headerLength + dataLength;
    
    const arrayBuffer = new ArrayBuffer(totalLength);
    const view = new DataView(arrayBuffer);
    
    writeString(view, 0, 'RIFF');
    view.setUint32(4, totalLength - 8, true);
    writeString(view, 8, 'WAVE');
    writeString(view, 12, 'fmt ');
    view.setUint32(16, 16, true);
    view.setUint16(20, format, true);
    view.setUint16(22, numChannels, true);
    view.setUint32(24, sampleRate, true);
    view.setUint32(28, sampleRate * numChannels * (bitDepth / 8), true);
    view.setUint16(32, numChannels * (bitDepth / 8), true);
    view.setUint16(34, bitDepth, true);
    writeString(view, 36, 'data');
    view.setUint32(40, dataLength, true);
    
    floatTo16BitPCM(view, 44, audioData);
    
    return arrayBuffer;
}

function resampleAudio(audioData, originalSampleRate, targetSampleRate) {
    const ratio = targetSampleRate / originalSampleRate;
    const newLength = Math.round(audioData.length * ratio);
    const result = new Float32Array(newLength);
    
    for (let i = 0; i < newLength; i++) {
        const position = i / ratio;
        const index = Math.floor(position);
        const fraction = position - index;
        
        if (index + 1 < audioData.length) {
            result[i] = audioData[index] * (1 - fraction) + audioData[index + 1] * fraction;
        } else {
            result[i] = audioData[index];
        }
    }
    
    return result;
}

function writeString(view, offset, string) {
    for (let i = 0; i < string.length; i++) {
        view.setUint8(offset + i, string.charCodeAt(i));
    }
}

function floatTo16BitPCM(view, offset, input) {
    for (let i = 0; i < input.length; i++, offset += 2) {
        const s = Math.max(-1, Math.min(1, input[i]));
        view.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7FFF, true);
    }
}

generateSpeechBtn.addEventListener('click', () => {
    const text = ttsInput.value.trim();
    if (!text) {
        ttsStatus.textContent = 'Please enter some text';
        ttsStatus.className = 'status error';
        return;
    }

    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ text }));
        ttsStatus.textContent = 'Generating audio...';
        ttsStatus.className = 'status';
    } else {
        ttsStatus.textContent = 'Connection lost. Reconnecting...';
        ttsStatus.className = 'status error';
        connectWebSocket();
    }
});

downloadAudioBtn.addEventListener('click', () => {
    if (currentAudioPath) {
        const link = document.createElement('a');
        link.href = currentAudioPath;
        link.download = `combined_audio_${Date.now()}.wav`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
});

window.addEventListener('beforeunload', () => {
    if (audioContext) {
        audioContext.close();
    }
    if (ws) {
        ws.close();
    }
    if (currentAudioPath) {
        URL.revokeObjectURL(currentAudioPath);
    }
    audioBuffers = [];
    pendingAudioPaths.clear();
});

connectWebSocket();
loadAgentEditorConfig();

async function fetchWithRetry(url, maxRetries = 3, retryDelay = 1000) {
    for (let i = 0; i < maxRetries; i++) {
        try {
            const response = await fetch(url);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response;
        } catch (error) {
            if (i === maxRetries - 1) throw error;
            await new Promise(resolve => setTimeout(resolve, retryDelay));
        }
    }
}
