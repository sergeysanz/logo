import os
import json
import base64
import requests
import re
from flask import Flask, render_template, request, jsonify
from PIL import Image
from dotenv import load_dotenv
import openai
import google.generativeai as genai

# ------------------------------
# Configuración inicial
# ------------------------------
load_dotenv()
app = Flask(__name__)

# ------------------------------
# OpenAI (DALL·E)
# ------------------------------
openai.api_key = os.getenv("OPENAI_API_KEY")

# ------------------------------
# Gemini
# ------------------------------
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
gemini_model = genai.GenerativeModel("gemini-1.5-flash")

# ------------------------------
# Utils
# ------------------------------
def extract_json(text):
    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        raise ValueError("No se encontró JSON")
    return json.loads(match.group())

# ------------------------------
# Prompt Logo
# ------------------------------
def build_logo_prompt(title, theme, uploaded_images):
    reference_text = ""

    for idx, f in enumerate(uploaded_images, start=1):
        if f and f.filename:
            try:
                Image.open(f.stream)
                reference_text += f" Usa la imagen {idx} solo como referencia de forma y silueta."
            except Exception:
                pass

    return f"""
Crea un logo profesional para la marca "{title}" basado en "{theme}".
{reference_text}

Características:
- Minimalista
- Elegante
- Escalable
- Branding de agencia premium
- Fondo transparente
- Sin mockups
- Sin texto adicional
- Formas claras y definidas
""".strip()

# ------------------------------
# Estrategia Gemini
# ------------------------------
def generate_brand_strategy(title, theme, gender, age_range):
    prompt = f"""
Responde SOLO con JSON válido.
NO markdown. NO texto adicional.

{{
  "insight": "lema corto y poderoso",
  "marketing_strategy": {{
    "tone": "tono de comunicación",
    "social_media": ["idea 1", "idea 2"],
    "events": ["evento 1", "evento 2"]
  }}
}}

Marca: {title}
Concepto: {theme}
Público: {gender}, {age_range}
"""

    response = gemini_model.generate_content(prompt)
    return extract_json(response.text)

# ------------------------------
# Routes
# ------------------------------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate_logo():
    try:
        title = request.form.get("title", "")
        theme = request.form.get("theme", "")
        gender = request.form.get("gender", "mujer")
        age_range = request.form.get("age_range", "18-35")

        element1 = request.files.get("element1")
        element2 = request.files.get("element2")

        # ---- Logo
        img_bytes = None
        logo_error = None

        try:
            prompt = build_logo_prompt(title, theme, [element1, element2])
            dalle = openai.Image.create(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                n=1
            )
            image_url = dalle["data"][0]["url"]
            img_bytes = requests.get(image_url, timeout=30).content
        except Exception as e:
            logo_error = str(e)

        if not img_bytes:
            with open("static/placeholder.png", "rb") as f:
                img_bytes = f.read()

        # ---- Estrategia
        try:
            strategy = generate_brand_strategy(title, theme, gender, age_range)
        except Exception:
            strategy = {
                "insight": "No se pudo generar insight",
                "marketing_strategy": {}
            }

        return jsonify({
            "logo": base64.b64encode(img_bytes).decode(),
            "insight": strategy.get("insight"),
            "marketing_strategy": strategy.get("marketing_strategy"),
            "error": logo_error
        })

    except Exception as e:
        return jsonify({
            "logo": None,
            "insight": None,
            "marketing_strategy": None,
            "error": str(e)
        })

# ------------------------------
# Run
# ------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
