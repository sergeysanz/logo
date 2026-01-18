import os
import json
import base64
import requests
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
# Gemini (Branding & Estrategia)
# ------------------------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel("gemini-1.5-flash")

# ------------------------------
# Función: Construir prompt para logo
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
# Función: Estrategia de marca (Gemini)
# ------------------------------
def generate_brand_strategy(title, theme, target_gender, target_age_range):
    prompt = f"""
Actúa como estratega senior de branding.

Marca: {title}
Concepto: {theme}
Público: {target_gender}, {target_age_range}

Devuelve SOLO JSON válido con esta estructura:

{{
  "insight": "lema corto y poderoso",
  "marketing_strategy": {{
    "social_media": ["idea 1", "idea 2"],
    "events": ["evento 1", "evento 2"],
    "tone": "tono de comunicación"
  }}
}}
"""

    response = gemini_model.generate_content(prompt)
    text = response.text.strip()

    # Limpieza por si Gemini envuelve en ```json
    if text.startswith("```"):
        text = text.replace("```json", "").replace("```", "").strip()

    return json.loads(text)

# ------------------------------
# Rutas Flask
# ------------------------------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate_logo():
    try:
        title = request.form.get("title", "").strip()
        theme = request.form.get("theme", "").strip()
        gender = request.form.get("gender", "mujer")
        age_range = request.form.get("age_range", "18-35")

        element1 = request.files.get("element1")
        element2 = request.files.get("element2")

        # ------------------------------
        # LOGO (DALL·E)
        # ------------------------------
        img_bytes = None
        logo_error = None

        try:
            logo_prompt = build_logo_prompt(title, theme, [element1, element2])

            dalle_response = openai.Image.create(
                model="dall-e-3",
                prompt=logo_prompt,
                size="1024x1024",
                n=1
            )

            image_url = dalle_response["data"][0]["url"]
            img_response = requests.get(image_url, timeout=30)

            if img_response.status_code == 200:
                img_bytes = img_response.content
            else:
                logo_error = "No se pudo descargar la imagen generada"

        except Exception as e:
            logo_error = f"Error DALL·E: {str(e)}"

        # ------------------------------
        # Fallback placeholder
        # ------------------------------
        if not img_bytes:
            try:
                with open("static/placeholder.png", "rb") as f:
                    img_bytes = f.read()
                logo_error = logo_error or "Se usó placeholder local"
            except Exception:
                img_bytes = None

        # ------------------------------
        # Estrategia (Gemini)
        # ------------------------------
        try:
            strategy = generate_brand_strategy(
                title, theme, gender, age_range
            )
        except Exception:
            strategy = {
                "insight": "No se pudo generar insight",
                "marketing_strategy": {}
            }

        # ------------------------------
        # RESPUESTA JSON FINAL
        # ------------------------------
        return jsonify({
            "logo": base64.b64encode(img_bytes).decode("utf-8") if img_bytes else None,
            "insight": strategy.get("insight"),
            "marketing_strategy": strategy.get("marketing_strategy"),
            "error": logo_error
        })

    except Exception as e:
        return jsonify({
            "logo": None,
            "insight": None,
            "marketing_strategy": None,
            "error": f"Error inesperado: {str(e)}"
        })

# ------------------------------
# Main (Render compatible)
# ------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
