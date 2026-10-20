const avatar = document.getElementById('avatar');
const emotionLabel = document.getElementById('emotion-label');
const stelleText = document.getElementById('stelle-text');
const messageInput = document.getElementById('message-input');
const sendBtn = document.getElementById('send-btn');
const statusDiv = document.getElementById('status');

const EMOTION_COLORS = {
    "annoyed": "#E74C3C",
    "soft": "#F5B7B1",
    "smug": "#F4D03F",
    "surprised": "#AF7AC5",
    "happy": "#58D68D"
};

let ttsEnabled = false;
let voiceMode = false;
let ws = null;
let audioCtx = new window.AudioContext();
let myvad = null;

document.getElementById('reset-btn').addEventListener('click', () => {
    if (!ws || ws.readyState !== WebSocket.OPEN) return;
    ws.send(JSON.stringify({ command: "reset" }));
    stelleText.textContent = "Reset.";
    avatar.style.backgroundColor = "#AAB7B8";
    emotionLabel.textContent = "Emotion : —";
});

const muteBtn = document.getElementById('mute-btn');
const iconSoundOn = muteBtn.querySelector('.icon-sound-on');
const iconSoundOff = muteBtn.querySelector('.icon-sound-off');

muteBtn.addEventListener('click', () => {
    ttsEnabled = !ttsEnabled;
    
    if (ttsEnabled) {
        iconSoundOn.style.display = 'block';
        iconSoundOff.style.display = 'none';
        muteBtn.title = "Mute";
    } else {
        iconSoundOn.style.display = 'none';
        iconSoundOff.style.display = 'block';
        muteBtn.title = "Unmute";
    }
});

const voiceBtn = document.getElementById('voice-btn');
const iconVoiceOff = voiceBtn.querySelector('.icon-voice-off');
const iconVoiceOn = voiceBtn.querySelector('.icon-voice-on');

voiceBtn.addEventListener('click', async () => {
    voiceMode = !voiceMode;
    
    if (voiceMode) {
        iconVoiceOff.style.display = 'none';
        iconVoiceOn.style.display = 'block';
        voiceBtn.classList.add('active');
        voiceBtn.title = "Voice: On";
        await unlockAudio();
        startVAD();
    } else {
        iconVoiceOff.style.display = 'block';
        iconVoiceOn.style.display = 'none';
        voiceBtn.classList.remove('active');
        voiceBtn.title = "Voice: Off";
        stopVAD();
    }
});

async function startVAD() {
    try {
        myvad = await vad.MicVAD.new({
            onSpeechStart: () => {
                console.log("Speech started");
                stelleText.textContent = "Listening...";
            },
            onSpeechEnd: (audio) => {
                console.log("Speech ended, sending audio");
                const wavBlob = vad.utils.encodeWAV(audio);
                if (ws && ws.readyState === WebSocket.OPEN) {
                    ws.send(wavBlob);
                }
            },
            onVADMisfire: () => {
                console.log("Too short, ignoring");
            },
            onnxWASMBasePath: "https://cdn.jsdelivr.net/npm/onnxruntime-web@1.22.0/dist/",
            baseAssetPath: "https://cdn.jsdelivr.net/npm/@ricky0123/vad-web@0.0.31/dist/",
        });
        
        myvad.start();
        console.log("VAD started");
    } catch (err) {
        console.error("VAD error:", err);
        alert("Cannot access microphone or load VAD.");
        voiceMode = false;
        voiceBtn.classList.remove('active');
        iconVoiceOff.style.display = 'block';
        iconVoiceOn.style.display = 'none';
    }
}

function stopVAD() {
    if (myvad) {
        myvad.destroy();
        myvad = null;
        console.log("VAD stopped");
    }
}

async function unlockAudio() {
    if (audioCtx.state === 'suspended') {
        await audioCtx.resume();
    }
}

function connect() {
    ws = new WebSocket(`ws://${window.location.host}/ws`);
    ws.binaryType = "arraybuffer";

    ws.onopen = () => {
        statusDiv.textContent = "Connected";
        statusDiv.style.color = "#a6e3a1";
        sendBtn.disabled = false;
    };

    ws.onclose = () => {
        statusDiv.textContent = "Disconnected";
        statusDiv.style.color = "#f38ba8";
        sendBtn.disabled = true;
        setTimeout(connect, 2000);
    };

    ws.onerror = (err) => {
        console.error("WS error:", err);
        statusDiv.textContent = "Connection error";
    };

    ws.onmessage = async (event) => {
        if (typeof event.data === 'string') {
            const data = JSON.parse(event.data);
            console.log("Received text:", data);

            if (data.transcription) {
                stelleText.textContent = `You: "${data.transcription}"`;
                return;
            }

            if (data.emotion) {
                const color = EMOTION_COLORS[data.emotion] || "#AAB7B8";
                avatar.style.backgroundColor = color;
                emotionLabel.textContent = `Emotion : ${data.emotion}`;
            }

            stelleText.textContent = data.reply;
        }
        else {
            if (!ttsEnabled) return;
            if (audioCtx.state === 'suspended') {
                await audioCtx.resume();
            }
            const arrayBuffer = event.data;
            const audioBuffer = await audioCtx.decodeAudioData(arrayBuffer);
            const source = audioCtx.createBufferSource();
            source.buffer = audioBuffer;
            source.connect(audioCtx.destination);
            source.start(0);
        }
    };
}

async function sendMessage() {
    const text = messageInput.value.trim();
    if (!text || !ws || ws.readyState !== WebSocket.OPEN) return;
    await unlockAudio();
    ws.send(text);
    messageInput.value = "";
    messageInput.disabled = true;
    sendBtn.disabled = true;
    stelleText.textContent = "...";
}

sendBtn.addEventListener('click', sendMessage);
messageInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
});

connect();