from flask import Flask, request, jsonify, Response, render_template_string
from flasgger import Swagger
from web_scraper import WebScraper
from main import generar_swagger_con_ia, remove_yaml_codeblock_header

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
    "specs_route": "/docs/"  # con barra final obligatoria
})

HTML_FORM = """
<!DOCTYPE html>
<html>
<head>
    <title>Generador de Swagger</title>
</head>
<body>
    <h2>🚀 API de Generación de Swagger</h2>
    <form method="post" action="/">
        <label for="url">Pega la URL o texto:</label>
        <input type="text" id="url" name="url" style="width:400px;" required>
        <button type="submit">Generar Swagger</button>
    </form>
    {% if yaml %}
        <h3>Resultado YAML:</h3>
        <pre style="background:#f4f4f4;padding:10px;">{{ yaml }}</pre>
    {% elif error %}
        <h3 style="color:red;">{{ error }}</h3>
    {% endif %}
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def home():
    yaml = None
    error = None
    if request.method == "POST":
        url = request.form.get("url")
        if not url:
            error = "⚠️ Debes enviar una URL o texto para scrapear."
        else:
            try:
                scraper = WebScraper(url)
                data = scraper.scrape_page(url)
                if not data:
                    error = "❌ No se pudo obtener datos de la página."
                else:
                    swagger_result = generar_swagger_con_ia(data)
                    if swagger_result:
                        yaml = remove_yaml_codeblock_header(swagger_result)
                    else:
                        error = "⚠️ No se pudo generar la documentación Swagger."
            except Exception as e:
                error = f"💥 Error al procesar la URL: {str(e)}"
    return render_template_string(HTML_FORM, yaml=yaml, error=error)


@app.route('/generate-swagger', methods=['POST'])
def generate_swagger():
    """
    Genera un archivo Swagger OpenAPI 3.0 en formato YAML a partir del contenido scrapeado de una URL o texto.
    ---
    tags:
      - Scraping
    summary: Genera Swagger YAML desde una URL scrapeada
    consumes:
      - application/json
    produces:
      - text/yaml
    parameters:
      - in: body
        name: body
        required: true
        description: JSON con la URL o texto a scrapear
        schema:
          type: object
          properties:
            url:
              type: string
              example: "https://developer.adobe.com/commerce/webapi/rest/"
    responses:
      200:
        description: YAML Swagger generado exitosamente
        content:
          text/yaml:
            schema:
              type: string
      400:
        description: Parámetro URL ausente
      500:
        description: Fallo durante el scraping o la generación
    """
    req_data = request.get_json()
    url = req_data.get('url')
    if not url:
        return jsonify({"error": "⚠️ Debes enviar una URL o texto."}), 400

    try:
        scraper = WebScraper(url)
        data = scraper.scrape_page(url)
        if not data:
            return jsonify({"error": "❌ No se pudo obtener datos de la página."}), 500
        swagger_result = generar_swagger_con_ia(data)
        yaml = remove_yaml_codeblock_header(swagger_result)
        return Response(yaml, mimetype='text/yaml')
    except Exception as e:
        return jsonify({"error": f"💥 Error interno: {str(e)}"}), 500


@app.route("/page-content", methods=["GET"])
def page_content():
    """
    ---
    tags:
      - Scraping
    summary: Obtiene el contenido scrapeado de una página web.
    parameters:
      - name: url
        in: query
        required: true
        schema:
          type: string
    responses:
      200:
        description: Contenido scrapeado exitosamente
        content:
          application/json:
            schema:
              type: object
      400:
        description: Falta parámetro URL
      500:
        description: Error al hacer scraping
    """
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "⚠️ Debes enviar una URL."}), 400
    try:
        scraper = WebScraper(url)
        data = scraper.scrape_page(url)
        if not data:
            return jsonify({"error": "❌ No se pudo obtener datos de la página."}), 500
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": f"💥 Error interno: {str(e)}"}), 500


@app.route("/state", methods=["GET"])
def state():
    return jsonify({
        "status": "✅ ok",
        "message": "API funcionando correctamente",
        "endpoints": ["/", "/generate-swagger", "/page-content", "/state", "/docs/"]
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
