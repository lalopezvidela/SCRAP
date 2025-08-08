import google.generativeai as genai
import os
from dotenv import load_dotenv
import json
import glob

# Carga tu API key desde .env
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Usa el mismo modelo que te funcionó en api.py
model = genai.GenerativeModel(model_name="models/gemini-2.5-flash")

# Busca todos los archivos JSON en el directorio
json_files = glob.glob("*.json")

if not json_files:
    print("No se encontraron archivos JSON en el directorio actual.")
    exit(1)

print("Archivos JSON encontrados:")
for idx, json_file in enumerate(json_files):
    print(f"{idx + 1}. {json_file}")

try:
    seleccion = int(input("Selecciona el número del archivo JSON que deseas convertir a YAML: "))
    if seleccion < 1 or seleccion > len(json_files):
        print("Selección inválida.")
        exit(1)
except ValueError:
    print("Entrada inválida.")
    exit(1)

json_file = json_files[seleccion - 1]
print(f"\nProcesando archivo: {json_file}\n")
with open(json_file, "r", encoding="utf-8") as f:
    json_content = f.read()

prompt = (
    "Convierte el siguiente JSON en un esquema Swagger/OpenAPI válido. "
    "Incluye los campos obligatorios y estructura el resultado para que pueda usarse en Swagger Editor. "
    "No incluyas ninguna explicación, introducción, comentario ni texto adicional, solo el contenido YAML del esquema. "
    "JSON de entrada:\n\n"
    f"{json_content}"
)

response = model.generate_content(prompt)
print("Respuesta del modelo:\n")
print(response.text)
print("\n" + "="*60 + "\n")


def limpiar_yaml(texto):
    # Elimina bloques de código Markdown y todo antes de 'openapi:'
    texto = texto.replace("```yaml", "").replace("```", "")
    openapi_index = texto.find("openapi:")
    if openapi_index != -1:
        texto = texto[openapi_index:]
    return texto.strip()


yaml_content = limpiar_yaml(response.text)

yaml_filename = os.path.splitext(json_file)[0] + ".swagger.yaml"
with open(yaml_filename, "w", encoding="utf-8") as yaml_file:
    yaml_file.write(yaml_content)
