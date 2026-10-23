const avatar = document.getElementById('avatar');
const emotionLabel = document.getElementById('emotion-label');
const stelleText = document.getElementById('stelle-text');
const messageInput = document.getElementById('message-input');
const sendBtn = document.getElementById('send-btn');
const statusDiv = document.getElementById('status');
let useLive2D = false;
let live2dModel = null;
let pixiApp = null;

if (typeof PIXI !== 'undefined' && PIXI.live2d) {
    PIXI.live2d.config.sound = false;
}

const SPRITES = {
    "annoyed": new Image(),
    "soft": new Image(),
    "smug": new Image(),
    "surprised": new Image(),
    "sad": new Image(),
    "normal": new Image()
};

const LIVE2D_CONFIG = window.LIVE2D_CONFIG || {
    modelPath: "/web/live2d/runtime/hibiki.model3.json",
    expressions: {
        "annoyed": "Angry",
        "soft": "Blushing",
        "smug": "f01",
        "surprised": "Surprised",
        "sad": "Sad",
        "normal": "Normal"
    }
};

const LIVE2D_MODEL_PATH = LIVE2D_CONFIG.modelPath;
const EXPRESSION_MAP = LIVE2D_CONFIG.expressions;

for (const [emotion, img] of Object.entries(SPRITES)) {
    img.src = `/web/sprites/${emotion}.png`;
}

let ttsEnabled = false;
let voiceMode = false;
let ws = null;
let audioCtx = new window.AudioContext();
let myvad = null;

document.getElementById('reset-btn').addEventListener('click', () => {
    if (!ws || ws.readyState !== WebSocket.OPEN) return;
    ws.send(JSON.stringify({ command: "reset" }));
    stelleText.textContent = "Reset.";
    emotionLabel.textContent = "Emotion : —";
    if (useLive2D && live2dModel) {
        live2dModel.expression("Normal");
    } else {
        document.getElementById('avatar').src = SPRITES["normal"].src;
    }
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
            model: "v5",
            baseAssetPath: "/web/vad/",
            onnxWASMBasePath: "/web/vad/"
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
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws`;
    ws = new WebSocket(wsUrl);
    ws.binaryType = "arraybuffer";

    ws.onopen = () => {
        statusDiv.textContent = "Connected";
        statusDiv.style.color = "#a6e3a1";
        sendBtn.disabled = false;
        messageInput.disabled = false;
    };

    ws.onclose = () => {
        statusDiv.textContent = "Disconnected";
        statusDiv.style.color = "#f38ba8";
        sendBtn.disabled = true;
        messageInput.disabled = true;
        stelleText.textContent = "Connection lost. Reconnecting...";
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
                sendBtn.disabled = false;
                messageInput.disabled = false;
                return;
            }

            if (data.emotion) {
                if (useLive2D && live2dModel) {
                    const expressionName = EXPRESSION_MAP[data.emotion] || "Normal";
                    try {
                        await live2dModel.expression(expressionName);
                    } catch (e) {
                        console.warn("Expression not found:", expressionName);
                    }
                } else {
                    const sprite = SPRITES[data.emotion];
                    if (sprite) {
                        document.getElementById('avatar').src = sprite.src;
                    }
                }
                emotionLabel.textContent = `Emotion : ${data.emotion}`;
            } else if (useLive2D && live2dModel) {
                live2dModel.expression("Normal");
            }

            stelleText.textContent = data.reply;

            sendBtn.disabled = false;
            messageInput.disabled = false;
            messageInput.focus();
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

async function initAvatar() {
    const spriteImg = document.getElementById('avatar');
    const live2dCanvas = document.getElementById('live2d-canvas');
    if (typeof PIXI == 'undefined' || !PIXI.live2d) {
        console.warn("Live2D libraries not found. Falling back to sprites.");
        useLive2D = false;
        spriteImg.style.display = 'block';
        live2dCanvas.style.display = 'none';
        spriteImg.src = SPRITES["normal"].src;
        return;
    }
    try {
        pixiApp = new PIXI.Application({
            view: live2dCanvas,
            transparent: true,
            resizeTo: window,
            autoStart: true,
        });
        live2dModel = await PIXI.live2d.Live2DModel.from(LIVE2D_MODEL_PATH);
        pixiApp.stage.addChild(live2dModel);
        const nativeHeight = live2dModel.height;

        const updateModelPosition = () => {
            const zoom = 1.7;
            const scale = (window.innerHeight * zoom) / nativeHeight;
            live2dModel.scale.set(scale);
            live2dModel.anchor.set(0.5, 0.4);
            live2dModel.x = window.innerWidth / 2;
            live2dModel.y = window.innerHeight * 0.7;
            live2dModel.scale.set(scale);
        }
        updateModelPosition();

        window.addEventListener('resize', updateModelPosition);

        useLive2D = true;
        live2dCanvas.style.display = 'block';
        spriteImg.style.display = 'none';
        live2dModel.expression("Normal");
        console.log("Mode: Live2D on");
    } catch (e) {
        console.warn("Live2D not found, utilizing sprites.", e);
        useLive2D = false;
        spriteImg.style.display = 'block';
        live2dCanvas.style.display = 'none';
        spriteImg.src = SPRITES["normal"].src;
    }
}

initAvatar();
connect();