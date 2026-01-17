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
openai.api_key = os.getenv("OPENAI_API_KEY")  # tu API Key de OpenAI

# ------------------------------
# Función para construir prompt
# ------------------------------
def build_logo_prompt(title, theme, uploaded_images, corpus_dir="corpus"):
    """
    Prompt optimizado para generar un logo conceptual:
    - Principios de Gestalt
    - Técnicas Kamon
    - Referencias de usuario y corpus
    - Concepto emocional basado en palabra clave
    """
    user_images_base64 = []
    for f in uploaded_images:
        if f:
            img = Image.open(f.stream)
            buf = io.BytesIO()
            img.save(buf, format='PNG')
            b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
            user_images_base64.append(b64)

    corpus_images_base64 = []
    if os.path.exists(corpus_dir):
        for folder in sorted(os.listdir(corpus_dir)):
            folder_path = os.path.join(corpus_dir, folder)
            if os.path.isdir(folder_path):
                for step in ["a.png","b.png","c.png"]:
                    img_path = os.path.join(folder_path, step)
                    if os.path.exists(img_path):
                        with open(img_path,"rb") as f:
                            b64 = base64.b64encode(f.read()).decode("utf-8")
                            corpus_images_base64.append(b64)

    # Prompt optimizado <1000 chars
    prompt_text = f"""
Crea un **logo único** para la marca "{title}" basado en "{theme}".
Usa hasta 2 imágenes de referencia y {len(corpus_images_base64)} del corpus.
Aplica Gestalt: proximidad, similitud, cierre, figura-fondo, pregnancia, continuidad.
Aplica Kamon japonés: simetría radial, repetición concéntrica.
Recursividad creativa: adapta formas, tipografía y colores según emoción de la palabra clave.
Integra el nombre de la marca dentro del icono.
Entrega **una sola imagen PNG**.
"""
    return prompt_text, user_images_base64, corpus_images_base64


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

    # Generar prompt
    prompt_text, user_images_base64, corpus_images_base64 = build_logo_prompt(
        title, theme, [element1, element2]
    )

    try:
        # Generar imagen usando DALL·E
        response = openai.Image.create(
            prompt=prompt_text,
            n=1,               # Solo 1 imagen
            size="512x512"     # Tamaño estándar de alta calidad
        )

        image_url = response['data'][0]['url']

        # Descargar la imagen generada
        img_response = requests.get(image_url)
        img_bytes = img_response.content

        return send_file(io.BytesIO(img_bytes), mimetype='image/png')

    except Exception as e:
        # En caso de error, enviar mensaje JSON
        return jsonify({"error": str(e)}), 500

# ------------------------------
# Main
# ------------------------------
if __name__ == '__main__':
    app.run(debug=True)
