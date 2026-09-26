const express = require('express');
const cors = require('cors');
const path = require('path');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3030;
const OLLAMA_HOST = process.env.OLLAMA_HOST || 'http://127.0.0.1:11434';

app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

function getValidServerKey() {
  const k = process.env.GEMINI_API_KEY;
  if (!k || typeof k !== 'string') return null;
  const trimmed = k.trim();
  if (trimmed.length < 10 || trimmed.includes('your_gemini_api_key')) return null;
  return trimmed;
}

// Check available local Ollama models
async function getOllamaModels() {
  try {
    const res = await fetch(`${OLLAMA_HOST}/api/tags`);
    if (res.ok) {
      const data = await res.json();
      return (data.models || []).map(m => m.name);
    }
  } catch (e) {
    // Ollama not responding
  }
  return [];
}

// Configuration status endpoint
app.get('/api/config', async (req, res) => {
  const serverKey = getValidServerKey();
  const ollamaModels = await getOllamaModels();
  
  res.json({
    hasServerKey: Boolean(serverKey),
    ollamaAvailable: ollamaModels.length > 0,
    ollamaModels: ollamaModels,
    defaultProvider: ollamaModels.length > 0 ? 'ollama' : (serverKey ? 'gemini' : 'ollama'),
    defaultOllamaModel: ollamaModels.includes('llama3.2:latest') 
      ? 'llama3.2:latest' 
      : (ollamaModels[0] || 'llama3.2')
  });
});

// Clean text for speech synthesis
function cleanForSpeech(raw) {
  return raw
    .replace(/<think>[\s\S]*?<\/think>/gi, '') // Strip reasoning tags if model has them
    .replace(/[*_~`#]/g, '')
    .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
    .trim();
}

// Chat endpoint supporting both Local Ollama (Free) and Gemini
app.post('/api/chat', async (req, res) => {
  try {
    const { 
      message, 
      history = [], 
      provider = 'auto', 
      apiKey: clientApiKey, 
      model: requestedModel, 
      persona = 'helpful' 
    } = req.body;

    if (!message || typeof message !== 'string' || message.trim().length === 0) {
      return res.status(400).json({ error: 'Message cannot be empty.' });
    }

    const clientKey = clientApiKey && typeof clientApiKey === 'string' ? clientApiKey.trim() : null;
    const geminiKey = clientKey || getValidServerKey();
    
    // Check if Ollama is available
    const ollamaModels = await getOllamaModels();
    const isOllamaUsable = ollamaModels.length > 0;

    // Determine target provider
    let targetProvider = provider;
    if (targetProvider === 'auto') {
      targetProvider = isOllamaUsable ? 'ollama' : 'gemini';
    }

    // Persona instructions optimized for voice speech output
    const personaInstructions = {
      helpful: 'You are Aura, an intelligent and friendly voice AI assistant. Keep responses natural, conversational, and direct (1 to 3 short sentences by default). Never output markdown formatting, asterisks, bullet points, headers, or emojis, because your response will be read aloud.',
      concise: 'You are Aura, an ultra-concise voice assistant. Answer in 1 to 2 direct, clear, spoken sentences without preamble or formatting.',
      casual: 'You are Aura, a warm, enthusiastic voice companion. Talk casually like a good friend on a voice call.',
      technical: 'You are Aura, a sharp technical software engineer. Provide accurate, clear spoken explanations without unnecessary fluff.'
    };
    const systemInstruction = personaInstructions[persona] || personaInstructions.helpful;

    // --- Provider 1: Local Ollama (100% Free, Local) ---
    if (targetProvider === 'ollama') {
      if (!isOllamaUsable) {
        return res.status(503).json({ 
          error: 'Local Ollama is not running. Please start Ollama or switch to Gemini in Settings.' 
        });
      }

      const activeModel = requestedModel && ollamaModels.includes(requestedModel)
        ? requestedModel
        : (ollamaModels.includes('llama3.2:latest') ? 'llama3.2:latest' : ollamaModels[0]);

      const messages = [
        { role: 'system', content: systemInstruction }
      ];

      // Add recent history
      if (Array.isArray(history)) {
        for (const turn of history.slice(-8)) {
          if (turn.role && turn.text) {
            messages.push({
              role: turn.role === 'user' ? 'user' : 'assistant',
              content: turn.text
            });
          }
        }
      }

      // Add current user message
      messages.push({ role: 'user', content: message });

      const ollamaRes = await fetch(`${OLLAMA_HOST}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          model: activeModel,
          messages: messages,
          stream: false,
          options: {
            temperature: 0.7,
            num_predict: 150
          }
        })
      });

      if (!ollamaRes.ok) {
        const errText = await ollamaRes.text().catch(() => '');
        return res.status(ollamaRes.status).json({ error: `Ollama error: ${errText}` });
      }

      const ollamaData = await ollamaRes.json();
      const reply = cleanForSpeech(ollamaData.message?.content || "I'm sorry, I couldn't generate a response.");

      return res.json({
        success: true,
        reply: reply,
        model: activeModel,
        provider: 'ollama (100% Free Local)'
      });
    }

    // --- Provider 2: Google Gemini ---
    if (targetProvider === 'gemini') {
      if (!geminiKey) {
        return res.status(401).json({
          error: 'No Gemini API key provided. You can switch Provider to "Local Ollama (Free)" in Settings to chat without an API key.'
        });
      }

      const model = requestedModel || process.env.GEMINI_MODEL || 'gemini-2.5-flash';
      const contents = [];

      if (Array.isArray(history)) {
        for (const turn of history.slice(-8)) {
          if (turn.role && turn.text) {
            contents.push({
              role: turn.role === 'user' ? 'user' : 'model',
              parts: [{ text: turn.text }]
            });
          }
        }
      }

      contents.push({
        role: 'user',
        parts: [{ text: message }]
      });

      const url = `https://generativelanguage.googleapis.com/v1beta/models/${encodeURIComponent(model)}:generateContent?key=${encodeURIComponent(geminiKey)}`;

      const geminiResponse = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          system_instruction: { parts: [{ text: systemInstruction }] },
          contents: contents,
          generationConfig: {
            temperature: 0.7,
            topP: 0.95,
            maxOutputTokens: 200
          }
        })
      });

      if (!geminiResponse.ok) {
        const errorData = await geminiResponse.json().catch(() => ({}));
        return res.status(geminiResponse.status).json({ 
          error: errorData.error?.message || `Gemini API error: HTTP ${geminiResponse.status}` 
        });
      }

      const data = await geminiResponse.json();
      const rawReply = data.candidates?.[0]?.content?.parts?.[0]?.text || "I'm sorry, I couldn't generate a response.";
      const reply = cleanForSpeech(rawReply);

      return res.json({
        success: true,
        reply: reply,
        model: model,
        provider: 'gemini'
      });
    }

  } catch (err) {
    console.error('Server error during chat:', err);
    res.status(500).json({ error: 'Internal error: ' + err.message });
  }
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`🎙️ AuraVoice Live Voice Assistant is running on http://localhost:${PORT}`);
});
