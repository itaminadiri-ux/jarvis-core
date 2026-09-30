import os
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "status": "online",
        "system": "Jarvis Core",
        "message": "Hola, Ilyas. Todos los sistemas funcionando en la nube."
    })

@app.route('/ask', methods=['POST'])
def ask():
    data = request.get_json() or {}
    user_message = data.get("message", "")
    
    if not user_message:
        return jsonify({"jarvis_response": "Esperando sus órdenes, señor."}), 400
        
    response_text = f"Servidor en Render activo. Procesando: '{user_message}'"
    
    return jsonify({
        "jarvis_response": response_text
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
