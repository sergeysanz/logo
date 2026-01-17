import os
import io
import base64
from flask import Flask, render_template, request, send_file, jsonify
from PIL import Image
from dotenv import load_dotenv
import openai

# Carga variables de entorno
load_dotenv()

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")  # tu API Key de OpenAI

# ------------------------------
# Función para construir prompt
# ------------------------------
def build_logo_prompt(title, theme, uploaded_images, corpus_dir="corpus"):
    """
    Construye un prompt avanzado para GPT considerando:
    - Principios de Gestalt
    - Técnicas Kamon japonesas
    - Consulta a corpus de estilos (1-8)
    """
    # Convertir imágenes subidas a base64
    user_images_base64 = []
    for f in uploaded_images:
        if f:
            img = Image.open(f.stream)
            buf = io.BytesIO()
            img.save(buf, format='PNG')
            b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
            user_images_base64.append(b64)

    # Leer corpus de estilo
    corpus_images_base64 = []
    if os.path.exists(corpus_dir):
        for folder in sorted(os.listdir(corpus_dir)):
            folder_path = os.path.join(corpus_dir, folder)
            if os.path.isdir(folder_path):
                for step in ["a.png", "b.png", "c.png"]:
                    img_path = os.path.join(folder_path, step)
                    if os.path.exists(img_path):
                        with open(img_path, "rb") as f:
                            b64 = base64.b64encode(f.read()).decode("utf-8")
                            corpus_images_base64.append(b64)

    # Construir prompt textual
    prompt_text = f"""
Genera un logo minimalista, armónico y creativo para la marca: {title}.
Tema de la marca: {theme}.
Usa hasta 2 imágenes de referencia del usuario.
Consulta {len(corpus_images_base64)} imágenes del corpus de estilos como inspiración.
Aplica principios de Gestalt: proximidad, similitud, cierre, figura-fondo, pregnancia, continuidad.
Aplica técnicas de Kamon japonés: simetría radial, repetición concéntrica, armonía visual.
Integra las letras de la marca dentro del icono de manera geométrica y estilizada.
Mantén proporciones armónicas, espacio negativo suficiente y legibilidad.
Devuelve el resultado en formato PNG codificado en base64.
No incluyas instrucciones de texto, solo la imagen codificada.
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

    # Generar prompt avanzado
    prompt_text, user_images_base64, corpus_images_base64 = build_logo_prompt(
        title, theme, [element1, element2]
    )

    try:
        # Llamada a OpenAI GPT
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role":"user", "content": prompt_text}],
            temperature=0.8
        )

        # GPT devuelve base64 de la imagen
        result_text = response.choices[0].message.content.strip()
        if "data:image/png;base64," in result_text:
            base64_data = result_text.split("data:image/png;base64,")[1]
            img_bytes = base64.b64decode(base64_data)
            return send_file(io.BytesIO(img_bytes), mimetype='image/png')
        else:
            # fallback: imagen blanca de 400x400
            img = Image.new('RGB', (400, 400), color=(255, 255, 255))
            buf = io.BytesIO()
            img.save(buf, format='PNG')
            buf.seek(0)
            return send_file(buf, mimetype='image/png')

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
