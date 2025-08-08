from flask import Flask, request, jsonify
from flasgger import Swagger
import requests
import os

app = Flask(__name__)

swagger = Swagger(app, template={
    "swagger": "2.0",
    "info": {
        "title": "API de Generación de Swagger",
        "description": "Endpoints para scraping y generación de documentación Swagger",
        "version": "1.0"
    },
    "basePath": "/",
    "schemes": [
        "http"
    ]
}, config={
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec_1',
            "route": '/apispec_1.json',
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/docs/"
})

@app.route("/", methods=["GET"])
def root():
    """
    Respuesta básica indicando que el servicio está en ejecución.
    ---
    responses:
      200:
        description: Servicio en ejecución
        examples:
          text/plain: "Microservicio activo"
    """
    return "Microservicio activo"

@app.route("/health", methods=["GET"])
def health():
    """
    Verifica el estado del sistema o de una URL externa.
    ---
    parameters:
      - name: url
        in: query
        type: string
        required: false
        description: URL externa a verificar
    responses:
      200:
        description: Estado OK o código de respuesta de la URL externa
        examples:
          application/json: {"status": "ok"}
      503:
        description: Servicio externo no disponible
    """
    url = request.args.get("url")
    if not url:
        return jsonify({"status": "ok"})
    try:
        resp = requests.get(url, timeout=5)
        return jsonify({"url": url, "status_code": resp.status_code, "reason": resp.reason})
    except Exception as e:
        return jsonify({"url": url, "error": str(e)}), 503

@app.route("/generate", methods=["POST"])
def generate():
    """
    Descarga y guarda la documentación Swagger (OpenAPI) desde una URL.
    ---
    parameters:
      - name: url
        in: body
        required: true
        schema:
          type: object
          properties:
            url:
              type: string
              example: "https://petstore.swagger.io/v2/swagger.json"
    responses:
      200:
        description: Archivo Swagger guardado exitosamente
        examples:
          application/json: {"saved_to": "repo/swagger.json"}
      400:
        description: Parámetro URL ausente
      500:
        description: Error al descargar o guardar el archivo
    """
    req_data = request.get_json()
    url = req_data.get("url") if req_data else None
    if not url:
        return jsonify({"error": "Debes enviar una URL."}), 400
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            os.makedirs("repo", exist_ok=True)
            filename = os.path.join("repo", os.path.basename(url))
            with open(filename, "wb") as f:
                f.write(resp.content)
            return jsonify({"saved_to": filename})
        else:
            return jsonify({"error": f"Error al descargar: {resp.status_code}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
