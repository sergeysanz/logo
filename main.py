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
# Función para construir prompt conceptual/emocional
# ------------------------------
def build_logo_prompt(title, theme, uploaded_images):
    """
    Prompt conceptual para generar un logo único:
    - Interpreta insight y emoción de la palabra clave
    - Una sola imagen
    - Armonía, equilibrio y estética
    - Referencias de usuario solo como guía conceptual (silueta/forma)
    - Lineamientos internos de diseño: Principios de la Gestalt, lineamientos graficos del Kamon japones, proporciones, legibilidad, composición
    - Corrientes artísticas asociadas a emoción o sentimiento
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
Crea un **logo único y conceptual** para la marca "{title}" basado en "{theme}".
Entrega **una sola imagen limpia, armónica y estéticamente agradable**.
Usa hasta 2 imágenes de referencia solo como guía de silueta o forma predominante, no superponer.
Aplica principios de Gestalt: proximidad, similitud, cierre, figura-fondo, continuidad, pregnancia.
Inspírate en técnicas de Kamon japonés (simetría radial, repetición concéntrica, armonía visual) solo como lineamiento conceptual.
Adapta tipografía, formas y colores según emoción y significado de la palabra clave "{theme}":
- rojo = pasión/energía
- amarillo = alegría
- azul = calma
- morado = melancolía
Usa corrientes artísticas asociadas a emoción o sentimiento (ej: monumentalismo, brutalismo, manierismo, hiperrealismo, eclecticismo, subvertising, etc.).
Evita minimalismo estricto y copia literal de estilos.
Asegura equilibrio visual, proporciones correctas, composición conceptual y legibilidad.
Entrega un **logo final en PNG de alta calidad**.
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
            n=1,               # Solo 1 imagen
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
