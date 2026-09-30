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
Tus respuestas deben ser claras, directas, objetivas y bien estructuradas.
"""

# ==========================================
# INTERFAZ WEB MULTIMODAL (TEXTO Y VOZ)
# ==========================================
HTML_INTERFACE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>J.A.R.V.I.S. Control System</title>
    <style>
        * { box-sizing: border-box; }
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
            padding: 15px;
        }
        .jarvis-container {
            text-align: center;
            background: rgba(16, 24, 48, 0.85);
            border: 1px solid #00f0ff;
            padding: 30px 20px;
            border-radius: 20px;
            box-shadow: 0 0 30px rgba(0, 240, 255, 0.25);
            max-width: 600px;
            width: 100%;
        }
        h1 {
            letter-spacing: 5px;
            margin-top: 0;
            margin-bottom: 20px;
            text-shadow: 0 0 12px #00f0ff;
            font-size: 1.8em;
        }
        .mic-btn {
            background: transparent;
            border: 2px solid #00f0ff;
            border-radius: 50%;
            width: 90px;
            height: 90px;
            font-size: 38px;
            color: #00f0ff;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 0 15px rgba(0, 240, 255, 0.3);
            outline: none;
            margin-bottom: 15px;
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
        .input-group {
            display: flex;
            gap: 10px;
            margin-top: 15px;
        }
        input[type="text"] {
            flex: 1;
            padding: 12px 15px;
            border-radius: 10px;
            border: 1px solid #00f0ff;
            background: rgba(0, 240, 255, 0.05);
            color: #ffffff;
            font-size: 1em;
            outline: none;
        }
        input[type="text"]:focus {
            box-shadow: 0 0 10px rgba(0, 240, 255, 0.5);
        }
        .send-btn {
            padding: 12px 20px;
            border-radius: 10px;
            border: 1px solid #00f0ff;
            background: rgba(0, 240, 255, 0.15);
            color: #00f0ff;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        .send-btn:hover {
            background: #00f0ff;
            color: #0b0f19;
        }
        #status {
            margin-top: 15px;
            font-size: 0.95em;
            color: #88a0c0;
        }
        #response-box {
            margin-top: 20px;
            padding: 15px;
            border-radius: 10px;
            background: rgba(0, 240, 255, 0.05);
            border: 1px solid rgba(0, 240, 255, 0.2);
            min-height: 100px;
            color: #ffffff;
            font-size: 0.98em;
            line-height: 1.5;
            text-align: left;
            white-space: pre-wrap;
            max-height: 350px;
            overflow-y: auto;
        }
    </style>
</head>
<body>
    <div class="jarvis-container">
        <h1>J.A.R.V.I.S.</h1>
        
        <button id="micBtn" class="mic-btn" onclick="toggleRecording()">🎙️</button>
        
        <div class="input-group">
            <input type="text" id="textInput" placeholder="Escriba su mensaje para Jarvis..." onkeypress="handleKeyPress(event)">
            <button class="send-btn" onclick="sendTextMessage()">Enviar</button>
        </div>

        <div id="status">Sistemas en espera, señor.</div>
        <div id="response-box">A la espera de sus órdenes, Ilyas.</div>
    </div>

    <script>
        const micBtn = document.getElementById('micBtn');
        const statusDiv = document.getElementById('status');
        const responseBox = document.getElementById('response-box');
        const textInput = document.getElementById('textInput');

        let mediaRecorder;
        let audioChunks = [];
        let isRecording = false;

        async function sendTextMessage() {
            const text = textInput.value.trim();
            if (!text) return;

            textInput.value = '';
            statusDiv.innerText = "Procesando mensaje...";
            responseBox.innerText = "Jarvis está procesando la solicitud...";

            try {
                const res = await fetch('/ask', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: text })
                });
                const data = await res.json();
                const reply = data.jarvis_response || "No pude procesar la solicitud, señor.";
                
                responseBox.innerText = reply;
                statusDiv.innerText = "Sistemas en espera, señor.";
            } catch (err) {
                responseBox.innerText = "Error de conexión con el servidor de Jarvis.";
                statusDiv.innerText = "Error al enviar";
            }
        }

        function handleKeyPress(event) {
            if (event.key === 'Enter') {
                sendTextMessage();
            }
        }

        async function toggleRecording() {
            if (!isRecording) {
                try {
                    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                    mediaRecorder = new MediaRecorder(stream);
                    audioChunks = [];

                    mediaRecorder.ondataavailable = event => {
                        if (event.data.size > 0) audioChunks.push(event.data);
                    };

                    mediaRecorder.onstop = async () => {
                        const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                        await sendAudioToJarvis(audioBlob);
                    };

                    mediaRecorder.start();
                    isRecording = true;
                    micBtn.classList.add('recording');
                    statusDiv.innerText = "Escuchando... Vuelve a pulsar para enviar.";
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
            responseBox.innerText = "Jarvis está escuchando y pensando...";
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
                    const reply = data.jarvis_response || "No pude procesar el mensaje de audio.";
                    
                    responseBox.innerText = reply;
                    statusDiv.innerText = "Sistemas en espera, señor.";
                } catch (err) {
                    responseBox.innerText = "Error de conexión con el servidor.";
                    statusDiv.innerText = "Intente de nuevo";
                }
            };
        }
    </script>
</body>
</html>
"""

@app.route('/', methods=['GET'])
def home():
    return render_template_string(HTML_INTERFACE)

@app.route('/ask', methods=['POST'])
def ask():
    if not client:
        return jsonify({"error": "GEMINI_API_KEY no configurada en Render."}), 500

    data = request.get_json() or {}
    user_message = data.get("message", "")

    if not user_message:
        return jsonify({"jarvis_response": "Esperando sus órdenes, señor."}), 400

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=user_message,
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
