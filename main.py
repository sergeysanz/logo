import os
import io
import base64
import requests
from flask import Flask, render_template, request, send_file, jsonify
from PIL import Image
from dotenv import load_dotenv
import openai

# ------------------------------
# Carga variables de entorno
# ------------------------------
load_dotenv()
app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

# ------------------------------
# Función para construir prompt profesional para logos
# ------------------------------
def build_logo_prompt(title, theme, uploaded_images):
    """
    Prompt profesional para generar logos:
    - Una sola imagen final
    - Basado en texto y opcionalmente en imágenes de referencia
    - Abstracción minimalista y limpia
    - Principios de Gestalt aplicados
    """

    reference_text = ""
    for idx, f in enumerate(uploaded_images, start=1):
        if f:
            try:
                img = Image.open(f.stream)
                buf = io.BytesIO()
                img.save(buf, format='PNG')
                img_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
                reference_text += f" Puedes usar la imagen {idx} como inspiración de forma y silueta."
            except Exception:
                continue  # Ignora si hay problema al abrir imagen

    prompt_text = f"""
Crea un logo profesional para la marca "{title}" basado en "{theme}".
{reference_text}
Transforma los elementos en una abstracción minimalista, elegante y moderna.
Aplica principios de Gestalt (simetría, cierre, figura-fondo, continuidad, proximidad) para lograr armonía visual.
El logo debe ser coherente, legible, escalable y adaptable a web e impresión.
Estilo inspirado en branding profesional de grandes agencias como Leo Burnett o Walter Thompson.
Fondo transparente, sin texturas ni efectos innecesarios, con líneas y formas definidas.
"""
    return prompt_text

# ------------------------------
# Rutas Flask
# ------------------------------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_logo():
    title = request.form.get("title", "")
    theme = request.form.get("theme", "")
    element1 = request.files.get("element1")
    element2 = request.files.get("element2")

    prompt_text = build_logo_prompt(title, theme, [element1, element2])

    try:
        # Generación de imagen usando el motor actual compatible con tu librería
        response = openai.Image.create(
            model="gpt-image-1",  # Último motor de imágenes
            prompt=prompt_text,
            n=1,                   # Solo 1 imagen
            size="1024x1024"       # Alta resolución
        )

        # Extraemos la URL de la imagen generada
        image_url = response['data'][0]['url']
        img_response = requests.get(image_url)
        img_bytes = img_response.content

        return send_file(io.BytesIO(img_bytes), mimetype='image/png')

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ------------------------------
# Main
# ------------------------------
if __name__ == '__main__':
    app.run(debug=True)
