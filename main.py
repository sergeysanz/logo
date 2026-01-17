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
                continue

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
# Función para generar insights y estrategia
# ------------------------------
def generate_brand_strategy(title, theme, target_gender, target_age_range):
    """
    Genera:
    - Lema corto o insight de marca
    - Estrategia de comunicación y marketing para redes sociales y eventos
    - Identificación del grupo generacional y rasgos de personalidad
    """
    prompt_text = f"""
Eres un experto en branding y marketing. 
Crea para la marca "{title}" con el tema "{theme}" lo siguiente:

1. Un lema o insight corto y poderoso para la marca.
2. Estrategia de marketing digital para redes sociales y eventos.
3. Identifica el público objetivo: género {target_gender}, edad {target_age_range}, grupo generacional, y rasgos de personalidad.
4. Sugiere mensajes y tono de comunicación más efectivos para ese grupo generacional.

Entrega la información de forma clara y organizada.
"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",  # Modelo más potente para texto
            messages=[{"role": "user", "content": prompt_text}],
            max_tokens=500
        )
        content = response.choices[0].message['content']
        return content
    except Exception as e:
        return str(e)

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
    target_gender = request.form.get("gender", "mujer")
    target_age_range = request.form.get("age_range", "18-35")
    element1 = request.files.get("element1")
    element2 = request.files.get("element2")

    # Genera prompt para logo
    logo_prompt = build_logo_prompt(title, theme, [element1, element2])

    # Genera logo
    try:
        response = openai.Image.create(
            model="gpt-image-1",
            prompt=logo_prompt,
            n=1,
            size="1024x1024"
        )
        image_url = response['data'][0]['url']
        img_response = requests.get(image_url)
        img_bytes = img_response.content
    except Exception as e:
        return jsonify({"error": f"Error generando logo: {str(e)}"}), 500

    # Genera estrategia de marca e insight
    brand_strategy = generate_brand_strategy(title, theme, target_gender, target_age_range)

    # Retornamos todo en JSON
    return jsonify({
        "logo": base64.b64encode(img_bytes).decode("utf-8"),
        "brand_strategy": brand_strategy
    })

# ------------------------------
# Main
# ------------------------------
if __name__ == '__main__':
    app.run(debug=True)
