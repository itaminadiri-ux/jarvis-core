import os
from flask import Flask, request, jsonify
from google import genai

app = Flask(__name__)

# Cargar la API key desde la variable de entorno de Render
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None

SYSTEM_INSTRUCTION = """
Eres Jarvis, un asistente de IA personal avanzado, rápido, educado y leal.
Te diriges al usuario como 'señor' o 'Ilyas'.
Tus respuestas deben ser concisas, precisas y directas al grano.
"""

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "status": "online",
        "system": "Jarvis Core",
        "message": "Sistemas operativos, Ilyas. ¿En qué puedo ayudarle hoy?"
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
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=user_message,
            config={'system_instruction': SYSTEM_INSTRUCTION}
        )
        return jsonify({
            "jarvis_response": response.text
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
