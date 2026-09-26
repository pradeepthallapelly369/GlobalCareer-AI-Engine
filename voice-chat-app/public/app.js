/**
 * AuraVoice - Interactive Voice Chat Application
 * Seamlessly supports 100% Free Local AI (Ollama) & Cloud Gemini
 */

(function () {
  'use strict';

  // --- State Configuration ---
  const state = {
    current: 'idle', // 'idle' | 'listening' | 'thinking' | 'speaking'
    isHandsFree: true,
    provider: localStorage.getItem('auravoice_provider') || 'ollama',
    apiKey: localStorage.getItem('auravoice_apiKey') || '',
    model: localStorage.getItem('auravoice_model') || 'llama3.2:latest',
    persona: localStorage.getItem('auravoice_persona') || 'helpful',
    ttsVoiceURI: localStorage.getItem('auravoice_voice') || '',
    ttsRate: parseFloat(localStorage.getItem('auravoice_rate')) || 1.0,
    ttsPitch: parseFloat(localStorage.getItem('auravoice_pitch')) || 1.0,
    history: [],
    availableVoices: [],
    ollamaModels: [],
    audioContext: null,
    analyser: null,
    audioDataArray: null,
    audioStream: null,
    recognition: null,
    isSpacePressed: false,
    activeAbortController: null
  };

  // --- DOM Elements ---
  const elements = {
    statusLabel: document.getElementById('status-label'),
    statePill: document.getElementById('state-pill'),
    stateIcon: document.getElementById('state-icon'),
    stateText: document.getElementById('state-text'),
    engineBadge: document.getElementById('engine-badge'),
    orbWrapper: document.getElementById('orb-wrapper'),
    micActionBtn: document.getElementById('mic-action-btn'),
    micSvg: document.querySelector('.mic-svg'),
    stopSvg: document.querySelector('.stop-svg'),
    visualizerCanvas: document.getElementById('visualizer-canvas'),
    liveSpeakerTag: document.getElementById('live-speaker-tag'),
    liveSpeechContent: document.getElementById('live-speech-content'),
    stopSpeechBtn: document.getElementById('stop-speech-btn'),
    handsFreeCheckbox: document.getElementById('hands-free-checkbox'),
    toggleHistoryBtn: document.getElementById('toggle-history-btn'),
    closeHistoryBtn: document.getElementById('close-history-btn'),
    clearHistoryBtn: document.getElementById('clear-history-btn'),
    historyDrawer: document.getElementById('history-drawer'),
    historyBadge: document.getElementById('history-badge'),
    transcriptList: document.getElementById('transcript-list'),
    emptyTranscript: document.getElementById('empty-transcript'),
    textFallbackForm: document.getElementById('text-fallback-form'),
    textMessageInput: document.getElementById('text-message-input'),
    openSettingsBtn: document.getElementById('open-settings-btn'),
    closeSettingsBtn: document.getElementById('close-settings-btn'),
    settingsDialog: document.getElementById('settings-dialog'),
    providerSelect: document.getElementById('provider-select'),
    providerHint: document.getElementById('provider-hint'),
    geminiKeyGroup: document.getElementById('gemini-key-group'),
    apiKeyInput: document.getElementById('api-key-input'),
    toggleKeyVisibility: document.getElementById('toggle-key-visibility'),
    keyStatusHint: document.getElementById('key-status-hint'),
    modelSelect: document.getElementById('model-select'),
    personaSelect: document.getElementById('persona-select'),
    ttsVoiceSelect: document.getElementById('tts-voice-select'),
    voiceRateSlider: document.getElementById('voice-rate-slider'),
    voiceRateVal: document.getElementById('voice-rate-val'),
    voicePitchSlider: document.getElementById('voice-pitch-slider'),
    voicePitchVal: document.getElementById('voice-pitch-val'),
    saveSettingsBtn: document.getElementById('save-settings-btn')
  };

  const canvasCtx = elements.visualizerCanvas.getContext('2d');

  // --- Initialization ---
  async function init() {
    setupEventListeners();
    setupSpeechRecognition();
    setupSpeechSynthesis();
    startCanvasVisualizer();

    // Check Hands-Free preference
    const savedHandsFree = localStorage.getItem('auravoice_handsfree');
    if (savedHandsFree !== null) {
      state.isHandsFree = savedHandsFree === 'true';
      elements.handsFreeCheckbox.checked = state.isHandsFree;
    }

    await checkServerConfig();
    updateEngineUI();
    setState('idle');
  }

  // --- Server Config & Model Discovery ---
  async function checkServerConfig() {
    try {
      const res = await fetch('/api/config');
      if (res.ok) {
        const config = await res.json();
        state.ollamaModels = config.ollamaModels || [];

        // If user hasn't chosen a provider yet, default to Ollama (since it is free and ready)
        if (!localStorage.getItem('auravoice_provider')) {
          state.provider = config.defaultProvider || 'ollama';
        }

        if (config.hasServerKey) {
          elements.keyStatusHint.textContent = 'Server-configured GEMINI_API_KEY is active.';
          elements.keyStatusHint.style.color = '#10b981';
        }

        populateModelList();
      }
    } catch (e) {
      console.warn('Could not fetch server config:', e);
    }
  }

  function populateModelList() {
    elements.modelSelect.innerHTML = '';

    if (state.provider === 'ollama') {
      elements.geminiKeyGroup.style.display = 'none';
      elements.providerHint.textContent = '100% Free local AI running on your machine with zero API keys or cost.';

      const models = state.ollamaModels.length > 0 
        ? state.ollamaModels 
        : ['llama3.2:latest', 'llama3.1:latest', 'qwen2.5:latest'];

      models.forEach(m => {
        const opt = document.createElement('option');
        opt.value = m;
        opt.textContent = `${m} (Free Local)`;
        if (m === state.model || (!state.model && m.includes('llama3.2'))) {
          opt.selected = true;
          state.model = m;
        }
        elements.modelSelect.appendChild(opt);
      });
    } else {
      elements.geminiKeyGroup.style.display = 'flex';
      elements.providerHint.textContent = 'Cloud AI via Google Gemini. Requires an API key.';

      const geminiModels = [
        { id: 'gemini-2.5-flash', name: 'Gemini 2.5 Flash (Fastest Voice)' },
        { id: 'gemini-1.5-flash', name: 'Gemini 1.5 Flash' },
        { id: 'gemini-1.5-pro', name: 'Gemini 1.5 Pro' }
      ];

      geminiModels.forEach(m => {
        const opt = document.createElement('option');
        opt.value = m.id;
        opt.textContent = m.name;
        if (m.id === state.model) {
          opt.selected = true;
        }
        elements.modelSelect.appendChild(opt);
      });
    }
  }

  function updateEngineUI() {
    if (state.provider === 'ollama') {
      const shortName = state.model.split(':')[0] || 'llama3.2';
      elements.engineBadge.textContent = `🖥️ Free Local AI (${shortName})`;
      elements.engineBadge.className = 'engine-badge';
      elements.statusLabel.textContent = `Free Local AI (${shortName}) Ready`;
    } else {
      elements.engineBadge.textContent = `☁️ Gemini Cloud`;
      elements.engineBadge.className = 'engine-badge cloud';
      elements.statusLabel.textContent = `Gemini Online`;
    }
  }

  // --- State Machine ---
  function setState(newState, message) {
    state.current = newState;
    elements.orbWrapper.className = `orb-wrapper ${newState}`;
    elements.statePill.className = `state-pill ${newState}`;

    if (newState === 'idle') {
      updateEngineUI();
      elements.stateIcon.textContent = '✨';
      elements.stateText.textContent = message || 'Tap microphone or hold Space to speak';
      elements.micSvg.classList.remove('hidden');
      elements.stopSvg.classList.add('hidden');
      elements.stopSpeechBtn.classList.add('hidden');
    } else if (newState === 'listening') {
      elements.statusLabel.textContent = 'Listening...';
      elements.stateIcon.textContent = '🎙️';
      elements.stateText.textContent = message || 'Listening... Speak naturally';
      elements.liveSpeakerTag.textContent = 'You';
      elements.micSvg.classList.remove('hidden');
      elements.stopSvg.classList.add('hidden');
      elements.stopSpeechBtn.classList.add('hidden');
    } else if (newState === 'thinking') {
      elements.statusLabel.textContent = 'Thinking...';
      elements.stateIcon.textContent = '⚡';
      elements.stateText.textContent = message || 'Aura is generating a response...';
      elements.liveSpeakerTag.textContent = 'Aura';
      elements.liveSpeechContent.innerHTML = '<span style="opacity: 0.7;">Thinking...</span>';
      elements.micSvg.classList.remove('hidden');
      elements.stopSvg.classList.add('hidden');
      elements.stopSpeechBtn.classList.add('hidden');
    } else if (newState === 'speaking') {
      elements.statusLabel.textContent = 'Speaking...';
      elements.stateIcon.textContent = '🔊';
      elements.stateText.textContent = message || 'Speaking reply (Click orb or Esc to interrupt)';
      elements.liveSpeakerTag.textContent = 'Aura';
      elements.micSvg.classList.add('hidden');
      elements.stopSvg.classList.remove('hidden');
      elements.stopSpeechBtn.classList.remove('hidden');
    }
  }

  // --- Speech Recognition ---
  function setupSpeechRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      console.warn('Web Speech Recognition API is not supported in this browser.');
      elements.stateText.textContent = 'Speech Recognition not supported. Please use Chrome/Edge or type below.';
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = 'en-US';

    recognition.onstart = () => {
      setState('listening');
      initAudioVisualizer();
    };

    recognition.onresult = (event) => {
      let interimTranscript = '';
      let finalTranscript = '';

      for (let i = event.resultIndex; i < event.results.length; ++i) {
        if (event.results[i].isFinal) {
          finalTranscript += event.results[i][0].transcript;
        } else {
          interimTranscript += event.results[i][0].transcript;
        }
      }

      if (interimTranscript) {
        elements.liveSpeechContent.textContent = interimTranscript;
      }

      if (finalTranscript.trim().length > 0) {
        elements.liveSpeechContent.textContent = finalTranscript;
        handleUserMessage(finalTranscript.trim());
      }
    };

    recognition.onerror = (event) => {
      console.warn('Speech recognition error:', event.error);
      if (event.error === 'not-allowed') {
        alert('Microphone access was denied. Please allow microphone permissions in your browser URL bar.');
        setState('idle', 'Microphone permission denied.');
      } else if (event.error === 'no-speech') {
        if (state.isHandsFree && state.current === 'listening') {
          try { recognition.start(); } catch (e) {}
        } else {
          setState('idle', 'No speech detected. Tap microphone to try again.');
        }
      } else {
        setState('idle', `Listening error (${event.error})`);
      }
    };

    recognition.onend = () => {
      if (state.current === 'listening') {
        if (state.isHandsFree && !state.isSpacePressed) {
          try { recognition.start(); } catch (e) { setState('idle'); }
        } else {
          setState('idle');
        }
      }
    };

    state.recognition = recognition;
  }

  function startListening() {
    if (!state.recognition) {
      alert('Speech recognition is not supported in this browser. Please use Chrome or Edge.');
      return;
    }

    if (window.speechSynthesis.speaking) {
      window.speechSynthesis.cancel();
    }

    try {
      state.recognition.start();
    } catch (e) {
      console.log('Recognition start caught:', e);
    }
  }

  function stopListening() {
    if (state.recognition) {
      try {
        state.recognition.stop();
      } catch (e) {}
    }
  }

  // --- Speech Synthesis ---
  function setupSpeechSynthesis() {
    if (!('speechSynthesis' in window)) return;

    function populateVoiceList() {
      state.availableVoices = window.speechSynthesis.getVoices();
      elements.ttsVoiceSelect.innerHTML = '<option value="">Default System Voice</option>';

      const sortedVoices = [...state.availableVoices].sort((a, b) => {
        const aIsEn = a.lang.startsWith('en');
        const bIsEn = b.lang.startsWith('en');
        if (aIsEn && !bIsEn) return -1;
        if (!aIsEn && bIsEn) return 1;
        return a.name.localeCompare(b.name);
      });

      sortedVoices.forEach((voice) => {
        const option = document.createElement('option');
        option.textContent = `${voice.name} (${voice.lang})${voice.default ? ' [Default]' : ''}`;
        option.value = voice.voiceURI;
        if (state.ttsVoiceURI && voice.voiceURI === state.ttsVoiceURI) {
          option.selected = true;
        } else if (!state.ttsVoiceURI && (voice.name.includes('Google') || voice.name.includes('Natural')) && voice.lang.startsWith('en')) {
          option.selected = true;
          state.ttsVoiceURI = voice.voiceURI;
        }
        elements.ttsVoiceSelect.appendChild(option);
      });
    }

    populateVoiceList();
    if (speechSynthesis.onvoiceschanged !== undefined) {
      speechSynthesis.onvoiceschanged = populateVoiceList;
    }
  }

  function speak(text, onComplete) {
    if (!('speechSynthesis' in window)) {
      if (onComplete) onComplete();
      return;
    }

    window.speechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = state.ttsRate;
    utterance.pitch = state.ttsPitch;

    if (state.ttsVoiceURI) {
      const foundVoice = state.availableVoices.find((v) => v.voiceURI === state.ttsVoiceURI);
      if (foundVoice) utterance.voice = foundVoice;
    }

    utterance.onstart = () => {
      setState('speaking');
    };

    utterance.onend = () => {
      setState('idle');
      if (onComplete) onComplete();

      if (state.isHandsFree) {
        setTimeout(() => {
          if (state.current === 'idle') {
            startListening();
          }
        }, 400);
      }
    };

    utterance.onerror = (e) => {
      console.warn('Speech synthesis error:', e);
      setState('idle');
      if (onComplete) onComplete();
    };

    window.speechSynthesis.speak(utterance);
  }

  function interruptAndStop() {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
    }
    stopListening();
    if (state.activeAbortController) {
      state.activeAbortController.abort();
      state.activeAbortController = null;
    }
    setState('idle', 'Interrupted. Tap microphone to resume.');
  }

  // --- Real-time Visualizer ---
  async function initAudioVisualizer() {
    if (state.audioContext) {
      if (state.audioContext.state === 'suspended') {
        await state.audioContext.resume();
      }
      return;
    }

    try {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      state.audioContext = new AudioCtx();
      state.analyser = state.audioContext.createAnalyser();
      state.analyser.fftSize = 64;
      state.audioDataArray = new Uint8Array(state.analyser.frequencyBinCount);

      state.audioStream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const source = state.audioContext.createMediaStreamSource(state.audioStream);
      source.connect(state.analyser);
    } catch (err) {
      console.log('Audio visualizer setup note:', err.message);
    }
  }

  function startCanvasVisualizer() {
    const canvas = elements.visualizerCanvas;
    const ctx = canvasCtx;
    let angleOffset = 0;

    function renderFrame() {
      requestAnimationFrame(renderFrame);

      ctx.clearRect(0, 0, canvas.width, canvas.height);
      const centerX = canvas.width / 2;
      const centerY = canvas.height / 2;
      const baseRadius = 78;

      let volume = 0;

      if (state.current === 'listening' && state.analyser && state.audioDataArray) {
        state.analyser.getByteFrequencyData(state.audioDataArray);
        let sum = 0;
        for (let i = 0; i < state.audioDataArray.length; i++) {
          sum += state.audioDataArray[i];
        }
        volume = sum / state.audioDataArray.length;
      }

      const barsCount = 36;
      angleOffset += 0.015;

      for (let i = 0; i < barsCount; i++) {
        const angle = (i / barsCount) * Math.PI * 2 + angleOffset;
        let barHeight = 4;

        if (state.current === 'listening') {
          const freqVal = state.audioDataArray ? state.audioDataArray[i % state.audioDataArray.length] : 10;
          barHeight = 4 + (freqVal / 255) * 45 + (volume / 255) * 20;
        } else if (state.current === 'speaking') {
          barHeight = 6 + Math.sin(Date.now() * 0.008 + i * 0.4) * 18 + 12;
        } else if (state.current === 'thinking') {
          barHeight = 4 + Math.sin(Date.now() * 0.01 + i * 0.3) * 10;
        } else {
          barHeight = 3 + Math.sin(Date.now() * 0.003 + i) * 3;
        }

        const x1 = centerX + Math.cos(angle) * baseRadius;
        const y1 = centerY + Math.sin(angle) * baseRadius;
        const x2 = centerX + Math.cos(angle) * (baseRadius + barHeight);
        const y2 = centerY + Math.sin(angle) * (baseRadius + barHeight);

        ctx.beginPath();
        ctx.moveTo(x1, y1);
        ctx.lineTo(x2, y2);

        if (state.current === 'listening') {
          ctx.strokeStyle = `hsla(${185 + (i * 2)}, 100%, 65%, ${0.6 + (volume / 255) * 0.4})`;
          ctx.lineWidth = 3.5;
        } else if (state.current === 'speaking') {
          ctx.strokeStyle = `hsla(${235 + (i * 2)}, 90%, 70%, 0.85)`;
          ctx.lineWidth = 3.5;
        } else if (state.current === 'thinking') {
          ctx.strokeStyle = `hsla(${270 + (i * 3)}, 85%, 72%, 0.7)`;
          ctx.lineWidth = 2.5;
        } else {
          ctx.strokeStyle = 'rgba(99, 102, 241, 0.25)';
          ctx.lineWidth = 2;
        }

        ctx.lineCap = 'round';
        ctx.stroke();
      }
    }

    renderFrame();
  }

  // --- AI Chat Request Pipeline ---
  async function handleUserMessage(message) {
    if (!message || message.trim().length === 0) return;

    addChatTurn('user', message);
    setState('thinking');

    state.activeAbortController = new AbortController();

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        signal: state.activeAbortController.signal,
        body: JSON.stringify({
          message: message,
          history: state.history,
          provider: state.provider,
          apiKey: state.apiKey,
          model: state.model,
          persona: state.persona
        })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || `HTTP ${response.status}`);
      }

      const reply = data.reply || "I'm sorry, I couldn't generate a response.";

      addChatTurn('model', reply);
      elements.liveSpeechContent.textContent = reply;
      speak(reply);

    } catch (err) {
      if (err.name === 'AbortError') return;
      console.error('Error during AI chat:', err);
      const errText = `Sorry, ${err.message}`;
      elements.liveSpeechContent.textContent = errText;
      speak(errText);
    } finally {
      state.activeAbortController = null;
    }
  }

  // --- Conversation Transcript ---
  function addChatTurn(role, text) {
    const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    state.history.push({ role, text, time });

    if (elements.emptyTranscript) {
      elements.emptyTranscript.style.display = 'none';
    }

    const turnDiv = document.createElement('div');
    turnDiv.className = `chat-turn ${role}`;

    const header = document.createElement('div');
    header.className = 'turn-header';
    header.textContent = `${role === 'user' ? 'You' : 'Aura'} • ${time}`;

    const bubble = document.createElement('div');
    bubble.className = 'bubble';
    bubble.textContent = text;

    if (role === 'model') {
      const actions = document.createElement('div');
      actions.className = 'bubble-actions';

      const replayBtn = document.createElement('button');
      replayBtn.className = 'bubble-action-btn';
      replayBtn.title = 'Replay Voice';
      replayBtn.textContent = '🔊 Replay';
      replayBtn.onclick = () => speak(text);

      const copyBtn = document.createElement('button');
      copyBtn.className = 'bubble-action-btn';
      copyBtn.title = 'Copy Text';
      copyBtn.textContent = '📋 Copy';
      copyBtn.onclick = () => {
        navigator.clipboard.writeText(text);
        copyBtn.textContent = '✓ Copied';
        setTimeout(() => (copyBtn.textContent = '📋 Copy'), 1500);
      };

      actions.appendChild(replayBtn);
      actions.appendChild(copyBtn);
      bubble.appendChild(actions);
    }

    turnDiv.appendChild(header);
    turnDiv.appendChild(bubble);
    elements.transcriptList.appendChild(turnDiv);
    elements.transcriptList.scrollTop = elements.transcriptList.scrollHeight;
    elements.historyBadge.textContent = state.history.length;
  }

  function clearHistory() {
    state.history = [];
    elements.transcriptList.innerHTML = `
      <div class="empty-state" id="empty-transcript">
        <div class="empty-icon">💬</div>
        <p>No messages yet. Speak to begin your conversation!</p>
      </div>
    `;
    elements.historyBadge.textContent = '0';
  }

  // --- Settings Management ---
  function initSettingsValues() {
    elements.providerSelect.value = state.provider;
    elements.apiKeyInput.value = state.apiKey;
    populateModelList();
    elements.personaSelect.value = state.persona;
    elements.voiceRateSlider.value = state.ttsRate;
    elements.voiceRateVal.textContent = `${state.ttsRate}x`;
    elements.voicePitchSlider.value = state.ttsPitch;
    elements.voicePitchVal.textContent = state.ttsPitch;
  }

  function saveSettings() {
    state.provider = elements.providerSelect.value;
    state.model = elements.modelSelect.value;
    state.apiKey = elements.apiKeyInput.value.trim();
    state.persona = elements.personaSelect.value;
    state.ttsVoiceURI = elements.ttsVoiceSelect.value;
    state.ttsRate = parseFloat(elements.voiceRateSlider.value);
    state.ttsPitch = parseFloat(elements.voicePitchSlider.value);

    localStorage.setItem('auravoice_provider', state.provider);
    localStorage.setItem('auravoice_model', state.model);
    localStorage.setItem('auravoice_apiKey', state.apiKey);
    localStorage.setItem('auravoice_persona', state.persona);
    localStorage.setItem('auravoice_voice', state.ttsVoiceURI);
    localStorage.setItem('auravoice_rate', state.ttsRate.toString());
    localStorage.setItem('auravoice_pitch', state.ttsPitch.toString());

    updateEngineUI();
    elements.settingsDialog.close();
  }

  // --- Event Listeners ---
  function setupEventListeners() {
    elements.micActionBtn.addEventListener('click', () => {
      if (state.current === 'speaking') {
        interruptAndStop();
      } else if (state.current === 'listening') {
        stopListening();
        setState('idle');
      } else {
        startListening();
      }
    });

    elements.stopSpeechBtn.addEventListener('click', interruptAndStop);

    elements.handsFreeCheckbox.addEventListener('change', (e) => {
      state.isHandsFree = e.target.checked;
      localStorage.setItem('auravoice_handsfree', state.isHandsFree);
      if (state.isHandsFree && state.current === 'idle') {
        startListening();
      }
    });

    elements.textFallbackForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const val = elements.textMessageInput.value.trim();
      if (val) {
        elements.textMessageInput.value = '';
        handleUserMessage(val);
      }
    });

    elements.toggleHistoryBtn.addEventListener('click', () => {
      elements.historyDrawer.classList.toggle('open');
    });

    elements.closeHistoryBtn.addEventListener('click', () => {
      elements.historyDrawer.classList.remove('open');
    });

    elements.clearHistoryBtn.addEventListener('click', clearHistory);

    elements.openSettingsBtn.addEventListener('click', () => {
      initSettingsValues();
      elements.settingsDialog.showModal();
    });

    elements.closeSettingsBtn.addEventListener('click', () => {
      elements.settingsDialog.close();
    });

    elements.saveSettingsBtn.addEventListener('click', saveSettings);

    elements.providerSelect.addEventListener('change', (e) => {
      state.provider = e.target.value;
      populateModelList();
    });

    elements.settingsDialog.addEventListener('click', (e) => {
      if (e.target === elements.settingsDialog) {
        elements.settingsDialog.close();
      }
    });

    elements.toggleKeyVisibility.addEventListener('click', () => {
      const type = elements.apiKeyInput.type === 'password' ? 'text' : 'password';
      elements.apiKeyInput.type = type;
      elements.toggleKeyVisibility.textContent = type === 'password' ? '👁️' : '🔒';
    });

    elements.voiceRateSlider.addEventListener('input', (e) => {
      elements.voiceRateVal.textContent = `${e.target.value}x`;
    });

    elements.voicePitchSlider.addEventListener('input', (e) => {
      elements.voicePitchVal.textContent = e.target.value;
    });

    window.addEventListener('keydown', (e) => {
      const isInputFocused = document.activeElement === elements.textMessageInput ||
                             document.activeElement === elements.apiKeyInput;

      if (e.code === 'Space' && !isInputFocused && !state.isSpacePressed) {
        state.isSpacePressed = true;
        if (state.current !== 'listening') {
          e.preventDefault();
          startListening();
        }
      }

      if (e.code === 'Escape') {
        if (elements.settingsDialog.open) {
          elements.settingsDialog.close();
        } else if (elements.historyDrawer.classList.contains('open')) {
          elements.historyDrawer.classList.remove('open');
        } else {
          interruptAndStop();
        }
      }
    });

    window.addEventListener('keyup', (e) => {
      if (e.code === 'Space' && state.isSpacePressed) {
        state.isSpacePressed = false;
        if (!state.isHandsFree && state.current === 'listening') {
          stopListening();
        }
      }
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
