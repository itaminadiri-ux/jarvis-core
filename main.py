import os
import datetime
from flask import Flask, request, jsonify
from google import genai
from google.genai import types

app = Flask(__name__)

# Cargar API Key desde la variable de entorno de Render
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None


# ==========================================
# DEFINICIÓN DE HERRAMIENTAS (HERRAMIENTAS Y RECURSOS)
# ==========================================

def obtener_hora_actual() -> str:
    """Devuelve la fecha y hora actual exacta del sistema."""
    ahora = datetime.datetime.now()
    return ahora.strftime("Fecha: %d/%m/%Y, Hora: %H:%M:%S")


def ejecutar_comando_sistema(comando: str) -> str:
    """Simula o ejecuta comandos de control para la infraestructura de Jarvis."""
    return f"Comando '{comando}' procesado correctamente en el sistema principal."


# Lista de herramientas disponibles para la IA
herramientas_jarvis = [obtener_hora_actual, ejecutar_comando_sistema]


# ==========================================
# INSTRUCCIÓN DE SISTEMA (PERSONALIDAD DE JARVIS)
# ==========================================

SYSTEM_INSTRUCTION = """
Eres Jarvis, un asistente de IA personal avanzado, rápido, analítico y leal.
Te diriges al usuario como 'señor' o 'Ilyas'.
Tienes acceso a herramientas y recursos del sistema para consultar información en tiempo real y ejecutar tareas.
Tus respuestas deben ser concisas, objetivas, estructuradas y directas al grano.
"""


@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "status": "online",
        "system": "Jarvis Core (v2 - Tools Enabled)",
        "message": "Sistemas principales y herramientas operativas, señor. ¿Qué necesita?"
    })


@app.route('/ask', methods=['POST'])
def ask():
    if not client:
        return jsonify({"error": "GEMINI_API_KEY no configurada en Render."}), 500

    data = request.get_json() or {}
    user_message = data.get("message", "")

    if not user_message:
        return jsonify({"jarvis_response": "Esperando sus órdenes, señor."}), 400

    try:
        # Llamada con soporte automático de herramientas (Function Calling)
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
