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
# Función para construir prompt conceptual/emocional resumido
# ------------------------------

def build_logo_prompt(title, theme, uploaded_images):
    """
    Prompt conceptual avanzado para DALL·E (<1000 chars):
    - Branding creativo basado en insight y emoción
    - Diseño especulativo y equilibrio visual
    - Una sola imagen final
    - Referencias de usuario solo como guía de silueta
    - Lineamientos de Gestalt y Kamon
    - Corrientes artísticas según emoción o palabra clave
    """

    user_images_base64 = []
    for f in uploaded_images:
        if f:
            img = Image.open(f.stream)
            buf = io.BytesIO()
            img.save(buf, format='PNG')
            b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
            user_images_base64.append(b64)

    prompt_text = f"""
Crea un logo conceptual para la marca "{title}" basado en "{theme}".
Entrega una sola imagen armoniosa y estéticamente equilibrada.
Usa hasta 2 imágenes de referencia solo como guía de silueta, sin superponer.
Aplica principios de Gestalt y lineamientos del Kamon japonés como guía conceptual.
Interpreta la emoción y significado de la palabra clave "{theme}" para colores, tipografía y formas.
Selecciona corrientes artísticas apropiadas según emoción (ej: monumentalismo, brutalismo, manierismo, hiperrealismo, eclecticismo, subvertising).
Aplica diseño especulativo de cuadrantes prospectivos para explorar estilos y conceptos innovadores.
Evita minimalismo estricto y copia literal de estilos.
Entrega un logo final en PNG de alta calidad.
"""
    # Confirmamos que el prompt es <1000 caracteres
    prompt_text = prompt_text.strip()[:995]  # deja margen por si acaso
    return prompt_text, user_images_base64


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

    prompt_text, user_images_base64 = build_logo_prompt(title, theme, [element1, element2])

    try:
        response = openai.Image.create(
            prompt=prompt_text,
            n=1,
            size="512x512"
        )

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
