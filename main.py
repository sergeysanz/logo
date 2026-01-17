import os
import io
import base64
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
    - Basado en texto y opcionalmente en la primera imagen de referencia
    - Abstracción minimalista y limpia
    - Principios de Gestalt aplicados
    """

    reference_image_text = ""
    # Si hay al menos una imagen de referencia, la codificamos y mencionamos en el prompt
    for f in uploaded_images:
        if f:
            img = Image.open(f.stream)
            buf = io.BytesIO()
            img.save(buf, format='PNG')
            img_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
            reference_image_text = " Usa la primera imagen de referencia como guía de silueta."
            break  # Solo la primera imagen

    prompt_text = f"""
Crea un logo profesional para la marca "{title}" basado en "{theme}".
{reference_image_text}
Transforma los elementos en una abstracción minimalista y elegante.
Aplica principios de Gestalt (simetría, cierre, figura-fondo, continuidad, proximidad) para lograr armonía visual.
Entrega una sola imagen final coherente, legible, escalable y adaptable a web e impresión.
El logo debe ser limpio, con formas definidas, fondo transparente, sin texturas, difuminados ni efectos innecesarios.
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
        # Usamos el motor más reciente de imágenes (DALL·E 3 / gpt-image-1)
        response = openai.images.generate(
            model="gpt-image-1",   # Último motor de OpenAI
            prompt=prompt_text,
            size="1024x1024",      # Alta resolución
            n=1,                   # Solo 1 imagen
            background="transparent"
        )

        # Extraemos la imagen
        image_b64 = response.data[0].b64_json
        img_bytes = base64.b64decode(image_b64)

        return send_file(io.BytesIO(img_bytes), mimetype='image/png')

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ------------------------------
# Main
# ------------------------------
if __name__ == '__main__':
    app.run(debug=True)
