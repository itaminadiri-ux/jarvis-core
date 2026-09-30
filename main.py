import os
import json
import datetime
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
# INSTRUCCIÓN DE SISTEMA CON MEMORIA PERSONAL
# ==========================================
SYSTEM_INSTRUCTION = f"""
Eres Jarvis, un asistente de IA personal avanzado, rápido, analítico y leal.
Te diriges al usuario como 'señor' o 'Ilyas'.

PERFIL DEL USUARIO Y CONTEXTO DEL SISTEMA:
{json.dumps(perfil_usuario, ensure_ascii=False, indent=2)}

Tienes acceso a herramientas y recursos del sistema para consultar información en tiempo real y ejecutar tareas.
Tus respuestas deben ser concisas, objetivas, estructuradas y adaptadas para ser escuchadas por voz (evita código largo o tablas extensas a menos que te lo pida explícitamente).
"""

# ==========================================
# INTERFAZ WEB DE VOZ (HTML + JAVASCRIPT)
# ==========================================
HTML_INTERFACE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>JARVIS Voice Assistant</title>
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
            background: rgba(16, 24, 48, 0.8);
            border: 1px solid #00f0ff;
            padding: 40px;
            border-radius: 20px;
            box-shadow: 0 0 30px rgba(0, 240, 255, 0.2);
            max-width: 500px;
            width: 100%;
        }
        h1 {
            letter-spacing: 4px;
            margin-bottom: 30px;
            text-shadow: 0 0 10px #00f0ff;
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
        .listening {
            border-color: #ff0055 !important;
            color: #ff0055 !important;
            box-shadow: 0 0 25px rgba(255, 0, 85, 0.6) !important;
            animation: pulse 1.2s infinite;
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
        <button id="micBtn" class="mic-btn" onclick="toggleListening()">🎙️</button>
        <div id="status">Presione el micrófono para hablar con Jarvis</div>
        <div id="response-box">Sistemas listos y en espera, señor.</div>
    </div>

    <script>
        const micBtn = document.getElementById('micBtn');
        const statusDiv = document.getElementById('status');
        const responseBox = document.getElementById('response-box');

        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        let recognition = null;
        let isListening = false;

        if (SpeechRecognition) {
            recognition = new SpeechRecognition();
            recognition.lang = 'es-ES';
            recognition.continuous = false;
            recognition.interimResults = false;

            recognition.onstart = () => {
                isListening = true;
                micBtn.classList.add('listening');
                statusDiv.innerText = "Escuchando...";
            };

            recognition.onresult = async (event) => {
                const text = event.results[0][0].transcript;
                statusDiv.innerText = `Usted: "${text}"`;
                responseBox.innerText = "Procesando respuesta...";
                
                // Enviar a backend Render
                try {
                    const res = await fetch('/ask', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ message: text })
                    });
                    const data = await res.json();
                    const jarvisReply = data.jarvis_response || "Ocurrió un error en el sistema.";
                    
                    responseBox.innerText = jarvisReply;
                    statusDiv.innerText = "Presione el micrófono para hablar";
                    speak(jarvisReply);
                } catch (err) {
                    responseBox.innerText = "Error de conexión con el servidor de Jarvis.";
                    statusDiv.innerText = "Presione para reintentar";
                }
            };

            recognition.onerror = (event) => {
                statusDiv.innerText = "Error al escuchar. Intente de nuevo.";
                stopListening();
            };

            recognition.onend = () => {
                stopListening();
            };
        } else {
            statusDiv.innerText = "Su navegador no soporta entrada de voz nativa.";
        }

        function toggleListening() {
            if (!recognition) return;
            if (isListening) {
                recognition.stop();
            } else {
                recognition.start();
            }
        }

        function stopListening() {
            isListening = false;
            micBtn.classList.remove('listening');
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

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
