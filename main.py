import os
import io
import base64
import requests
from flask import Flask, render_template, request, jsonify
from PIL import Image
from dotenv import load_dotenv
import openai

# ------------------------------
# Configuración inicial
# ------------------------------
load_dotenv()
app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

# ------------------------------
# Función: Construir prompt para logo
# ------------------------------
def build_logo_prompt(title, theme, uploaded_images):
    reference_text = ""
    for idx, f in enumerate(uploaded_images, start=1):
        if f:
            try:
                img = Image.open(f.stream)
                buf = io.BytesIO()
                img.save(buf, format='PNG')
                # No necesitamos el base64, solo para referencia en el prompt
                reference_text += f" Puedes usar la imagen {idx} como inspiración de forma y silueta."
            except Exception:
                continue

    prompt_text = f"""
Crea un logo profesional para la marca "{title}" basado en "{theme}".
{reference_text}
Transforma los elementos en una abstracción minimalista, elegante y moderna.
Aplica principios de Gestalt (simetría, cierre, figura-fondo, continuidad, proximidad) para lograr armonía visual.
El logo debe ser coherente, legible, escalable y adaptable a web e impresión.
Estilo inspirado en branding profesional de grandes agencias.
Fondo transparente si es posible, sin texturas ni efectos innecesarios, con líneas y formas definidas.
"""
    return prompt_text

# ------------------------------
# Función: Generar insight y estrategia de marca
# ------------------------------
def generate_brand_strategy(title, theme, target_gender, target_age_range):
    prompt_text = f"""
Eres un experto en branding y marketing. 
Crea para la marca "{title}" con el tema "{theme}" lo siguiente:

1. Un lema o insight corto y poderoso para la marca.
2. Estrategia de marketing digital para redes sociales y eventos, adaptada a mujeres de edad {target_age_range}.
3. Identifica el grupo generacional y los rasgos de personalidad típicos.
4. Sugiere mensajes, tono y estilo de comunicación más efectivos.

Entrega la información de forma clara y organizada.
"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt_text}],
            max_tokens=500
        )
        return response.choices[0].message['content']
    except Exception as e:
        return f"Error generando estrategia: {str(e)}"

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

    logo_prompt = build_logo_prompt(title, theme, [element1, element2])

    img_bytes = None
    logo_error = None

    # ------------------------------
    # Intentar generar logo con DALL·E 3
    # ------------------------------
    try:
        response = openai.Image.create(
            model="dall-e-3",
            prompt=logo_prompt,
            n=1,
            size="1024x1024"
        )
        image_url = response['data'][0].get('url')
        if image_url:
            img_response = requests.get(image_url, timeout=15)
            if img_response.status_code == 200:
                img_bytes = img_response.content
            else:
                logo_error = f"No se pudo descargar la imagen, status code {img_response.status_code}"
        else:
            logo_error = "No se obtuvo URL de la imagen desde la API."
    except Exception as e:
        logo_error = f"No se pudo generar logo dinámico: {str(e)}"

    # ------------------------------
    # Fallback: usar placeholder local
    # ------------------------------
    if not img_bytes:
        try:
            with open("static/placeholder.png", "rb") as f:
                img_bytes = f.read()
            logo_error = logo_error or "Se usó placeholder local porque falló la generación de logo."
        except Exception:
            img_bytes = None
            logo_error = logo_error or "No hay imagen disponible."

    # ------------------------------
    # Generar insight y estrategia de marca
    # ------------------------------
    brand_strategy = generate_brand_strategy(title, theme, target_gender, target_age_range)
    if not brand_strategy:
        brand_strategy = "No se pudo generar la estrategia."

    # ------------------------------
    # Respuesta JSON segura
    # ------------------------------
    return jsonify({
        "logo": base64.b64encode(img_bytes).decode("utf-8") if img_bytes else None,
        "brand_strategy": brand_strategy,
        "error": logo_error
    })

# ------------------------------
# Main
# ------------------------------
if __name__ == '__main__':
    app.run(debug=True)
