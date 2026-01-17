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
# Construir prompt conceptual/emocional
# ------------------------------
def build_logo_prompt(title, theme, uploaded_images):
    """
    Prompt optimizado para generar un logo conceptual basado en insight:
    - Interpreta emoción y sentimiento de la palabra clave
    - Colores, formas y tipografía según emoción
    - Técnicas artísticas asociadas al sentimiento
    - Composición armoniosa y estética
    - Solo 1 imagen
    """
    # Convertir imágenes subidas a base64 para referencia conceptual (no literal)
    user_images_base64 = []
    for f in uploaded_images:
        if f:
            img = Image.open(f.stream)
            buf = io.BytesIO()
            img.save(buf, format='PNG')
            b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
            user_images_base64.append(b64)

    prompt_text = f"""
Crea un **logo conceptual único** para la marca "{title}" basado en "{theme}".
Interpreta el insight de la descripción y la palabra clave para generar una solución creativa.
Usa la emoción y sentimiento asociados para definir:
- Colores: rojo = pasión/energía, amarillo = alegría, azul = calma, morado = melancolía, etc.
- Formas y tipografía: curvas suaves = confort, líneas geométricas = fuerza, dinámicas = velocidad.
- Estilo artístico: monumentalismo, brutalismo, manierismo, hiperrealismo, eclecticismo, subvertising, etc. según emoción.
Usa hasta 2 imágenes de referencia solo como guía de silueta o figura predominante, no superponer.
Asegura equilibrio, armonía visual, legibilidad y estética general.
Entrega **una sola imagen PNG de alta calidad**.
"""
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

    # Construir prompt
    prompt_text, user_images_base64 = build_logo_prompt(title, theme, [element1, element2])

    try:
        # Generar imagen usando DALL·E
        response = openai.Image.create(
            prompt=prompt_text,
            n=1,               # solo 1 imagen
            size="512x512"
        )

        image_url = response['data'][0]['url']

        # Descargar imagen generada
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
