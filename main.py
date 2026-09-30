import os
import json
import datetime
import base64
from flask import Flask, request, jsonify, render_template_string
from google import genai
from google.genai import types

app = Flask(__name__)

api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None

# ==========================================
# CARGA DE CONTEXTO Y PERFIL DE USUARIO
# ==========================================
def cargar_perfil():
    try:
        if os.path.exists("user_profile.json"):
            with open("user_profile.json", "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        print(f"Error al cargar el perfil: {e}")
    return {}

perfil_usuario = cargar_perfil()

# ==========================================
# HERRAMIENTAS Y RECURSOS
# ==========================================
def obtener_hora_actual() -> str:
    """Devuelve la fecha y hora actual exacta del sistema."""
    ahora = datetime.datetime.now()
    return ahora.strftime("Fecha: %d/%m/%Y, Hora: %H:%M:%S")

def ejecutar_comando_sistema(comando: str) -> str:
    """Simula o ejecuta comandos de control para la infraestructura de Jarvis."""
    return f"Comando '{comando}' procesado correctamente en el sistema principal."

herramientas_jarvis = [obtener_hora_actual, ejecutar_comando_sistema]

# ==========================================
# INSTRUCCIÓN DE SISTEMA
# ==========================================
SYSTEM_INSTRUCTION = f"""
Eres Jarvis, un asistente de IA personal extremadamente rápido, analítico y leal.
Te diriges al usuario siempre como 'señor' o 'Ilyas'.

PERFIL DEL USUARIO Y CONTEXTO DEL SISTEMA:
{json.dumps(perfil_usuario, ensure_ascii=False, indent=2)}

Tienes acceso a herramientas del sistema para consultar datos en tiempo real.
Tus respuestas van a ser escuchadas por voz, por lo que deben ser directas, naturales, conversacionales y concisas (evita tablas o formateo markdown complejo).
"""

# ==========================================
# INTERFAZ WEB DE VOZ NATIVA (MEDIA RECORDER)
# ==========================================
HTML_INTERFACE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>J.A.R.V.I.S. Voice System</title>
    <style>
        body {
            background-color: #0b0f19;
            color: #00f0ff;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            margin: 0;
            padding: 20px;
            box-sizing: border-box;
        }
        .jarvis-container {
            text-align: center;
            background: rgba(16, 24, 48, 0.85);
            border: 1px solid #00f0ff;
            padding: 40px;
            border-radius: 20px;
            box-shadow: 0 0 30px rgba(0, 240, 255, 0.25);
            max-width: 500px;
            width: 100%;
        }
        h1 {
            letter-spacing: 5px;
            margin-bottom: 30px;
            text-shadow: 0 0 12px #00f0ff;
        }
        .mic-btn {
            background: transparent;
            border: 2px solid #00f0ff;
            border-radius: 50%;
            width: 120px;
            height: 120px;
            font-size: 50px;
            color: #00f0ff;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 0 15px rgba(0, 240, 255, 0.3);
            outline: none;
        }
        .mic-btn:hover {
            transform: scale(1.05);
            background: rgba(0, 240, 255, 0.1);
        }
        .recording {
            border-color: #ff0055 !important;
            color: #ff0055 !important;
            box-shadow: 0 0 30px rgba(255, 0, 85, 0.8) !important;
            animation: pulse 1s infinite;
        }
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.08); }
            100% { transform: scale(1); }
        }
        #status {
            margin-top: 25px;
            font-size: 1.1em;
            color: #88a0c0;
        }
        #response-box {
            margin-top: 25px;
            padding: 15px;
            border-radius: 10px;
            background: rgba(0, 240, 255, 0.05);
            border: 1px solid rgba(0, 240, 255, 0.2);
            min-height: 80px;
            color: #ffffff;
            font-size: 1em;
            line-height: 1.5;
            text-align: left;
        }
    </style>
</head>
<body>
    <div class="jarvis-container">
        <h1>J.A.R.V.I.S.</h1>
        <button id="micBtn" class="mic-btn" onclick="toggleRecording()">🎙️</button>
        <div id="status">Haz clic para hablarle a Jarvis</div>
        <div id="response-box">Sistemas listos y en espera, señor.</div>
    </div>

    <script>
        const micBtn = document.getElementById('micBtn');
        const statusDiv = document.getElementById('status');
        const responseBox = document.getElementById('response-box');

        let mediaRecorder;
        let audioChunks = [];
        let isRecording = false;

        async function toggleRecording() {
            if (!isRecording) {
                try {
                    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                    mediaRecorder = new MediaRecorder(stream);
                    audioChunks = [];

                    mediaRecorder.ondataavailable = event => {
                        if (event.data.size > 0) {
                            audioChunks.push(event.data);
                        }
                    };

                    mediaRecorder.onstop = async () => {
                        const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                        await sendAudioToJarvis(audioBlob);
                    };

                    mediaRecorder.start();
                    isRecording = true;
                    micBtn.classList.add('recording');
                    statusDiv.innerText = "Escuchando... Haz clic de nuevo para enviar.";
                } catch (err) {
                    statusDiv.innerText = "Error: Permiso de micrófono denegado.";
                }
            } else {
                mediaRecorder.stop();
                isRecording = false;
                micBtn.classList.remove('recording');
                statusDiv.innerText = "Procesando audio...";
            }
        }

        async function sendAudioToJarvis(blob) {
            responseBox.innerText = "Jarvis está pensando...";
            const reader = new FileReader();
            reader.readAsDataURL(blob);
            reader.onloadend = async () => {
                const base64Audio = reader.result.split(',')[1];
                try {
                    const res = await fetch('/ask-audio', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ audio: base64Audio, mime_type: 'audio/webm' })
                    });
                    const data = await res.json();
                    const reply = data.jarvis_response || "No pude procesar el mensaje, señor.";
                    
                    responseBox.innerText = reply;
                    statusDiv.innerText = "Haz clic para hablarle a Jarvis";
                    speak(reply);
                } catch (err) {
                    responseBox.innerText = "Error de conexión con el servidor de Jarvis.";
                    statusDiv.innerText = "Intente de nuevo";
                }
            };
        }

        function speak(text) {
            window.speechSynthesis.cancel();
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = 'es-ES';
            utterance.rate = 1.0;
            window.speechSynthesis.speak(utterance);
        }
    </script>
</body>
</html>
"""

@app.route('/', methods=['GET'])
def home():
    return render_template_string(HTML_INTERFACE)

@app.route('/ask-audio', methods=['POST'])
def ask_audio():
    if not client:
        return jsonify({"error": "GEMINI_API_KEY no configurada en Render."}), 500

    data = request.get_json() or {}
    audio_base64 = data.get("audio", "")
    mime_type = data.get("mime_type", "audio/webm")

    if not audio_base64:
        return jsonify({"jarvis_response": "No he recibido ningún audio, señor."}), 400

    try:
        audio_bytes = base64.b64decode(audio_base64)
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[
                types.Part.from_bytes(data=audio_bytes, mime_type=mime_type),
                "Escucha este audio del usuario y responde directamente a lo que dice o pide."
            ],
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                tools=herramientas_jarvis,
                temperature=0.2
            )
        )
        return jsonify({
            "jarvis_response": response.text
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
