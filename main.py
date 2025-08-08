from web_scraper import WebScraper
import json
import google.generativeai as genai
from dotenv import load_dotenv
import os

# Cargar claves desde .env
load_dotenv()

# Verificar clave
if not os.getenv("GEMINI_API_KEY"):
    print("❌ ERROR: No se encontró la clave 'GEMINI_API_KEY'. Verifica tu archivo .env.")
    exit(1)

# Configurar API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def remove_yaml_codeblock_header(yaml_text):
    lines = yaml_text.splitlines()
    if lines and lines[0].strip() == "```yaml":
        return "\n".join(lines[1:])
    return yaml_text

def generar_swagger_con_ia(data):
    prompt = f"""
Eres un generador automático de archivos Swagger OpenAPI 3.0. A partir del siguiente JSON, produce únicamente el archivo YAML válido, sin explicaciones, sin comentarios y sin frases introductorias.
Si generas frases como “Aquí tienes”, se considerará un error. Solo YAML.

JSON:
{json.dumps(data, indent=2, ensure_ascii=False)}
"""
    # Usa el modelo correcto según tu disponibilidad (modifica si lo cambias)
    model = genai.GenerativeModel("models/gemini-2.5-flash")
    response = model.generate_content(prompt)
    return response.text.strip()

def main():
    url = input("Introduce la URL a scrapear: ").strip()
    if not url or not (url.startswith("http://") or url.startswith("https://")):
        print("❌ ERROR: Debes ingresar una URL válida que comience con http:// o https://")
        return
    json_filename = input("Nombre del archivo JSON de salida (ejemplo: resultado.json): ").strip()
    if not json_filename:
        json_filename = "scraped_data.json"
    if not json_filename.lower().endswith('.json'):
        json_filename += '.json'

    scraper = WebScraper(url)
    data = scraper.scrape_page(url)

    if data:
        print(f"Título: {data['title']}")
        print(f"Encabezados encontrados: {len(data['headings'])}")
        print(f"Párrafos encontrados: {len(data['paragraphs'])}")
        print(f"Tablas encontradas: {len(data['tables'])}")
        scraper.save_data(data, json_filename)

        print("\n--- Primeros 3 encabezados ---")
        for heading in data['headings'][:3]:
            print(f"{heading['tag']}: {heading['text']}")

        print("\n--- Primeros 3 párrafos ---")
        for i, para in enumerate(data['paragraphs'][:3], 1):
            print(f"{i}. {para['text'][:100]}...")

        # Generar Swagger
        swagger = generar_swagger_con_ia(data)
        swagger = remove_yaml_codeblock_header(swagger)
        yaml_filename = json_filename.replace(".json", ".yaml")
        with open(yaml_filename, 'w', encoding='utf-8') as f:
            f.write(swagger)
        print(f"\n✅ Swagger guardado en: {yaml_filename}")
    else:
        print("No se pudo obtener datos de la página.")

if __name__ == "__main__":
    main()
