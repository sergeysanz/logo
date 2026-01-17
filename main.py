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
    Prompt avanzado para generar logos profesionales:
    - Se basa en siluetas y formas de imágenes de referencia
    - Transformación a abstracción minimalista
    - Una sola imagen final coherente y armoniosa
    - Principios de Gestalt aplicados para equilibrio visual
    - Adaptable a web e impresión
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
Crea un logo profesional para la marca "{title}" basado en "{theme}".
Usa las formas y siluetas de las imágenes de referencia como guía conceptual, 
transformándolas en una abstracción minimalista y armoniosa.
Fusiona los elementos de manera equilibrada, aplicando principios de Gestalt 
(simetría, cierre, figura-fondo, continuidad, proximidad).
Entrega una sola imagen final coherente, elegante, legible y escalable.
El resultado debe ser adaptable a web e impresión, con fondo transparente, 
evitando exceso de detalle, estilos infantiles o efectos innecesarios.
"""
    # Confirmamos que el prompt es <1000 caracteres
    prompt_text = prompt_text.strip()[:995]
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
            size="1024x1024"  # Mayor resolución para logos profesionales
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
