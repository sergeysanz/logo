import os
import base64
import requests
from flask import Flask, render_template, request, jsonify
from PIL import Image
from dotenv import load_dotenv
import openai
import google.generativeai as genai

# -----------------------------------
# Configuración inicial
# -----------------------------------
load_dotenv()
app = Flask(__name__)

# -----------------------------------
# OpenAI (DALL·E)
# -----------------------------------
openai.api_key = os.getenv("OPENAI_API_KEY")

# -----------------------------------
# Gemini (Texto estratégico)
# -----------------------------------
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
gemini_model = genai.GenerativeModel("gemini-1.5-flash")

# -----------------------------------
# Prompt Logo (DALL·E)
# -----------------------------------
def build_logo_prompt(brand_name, brand_description, uploaded_images):
    reference_text = ""

    for idx, f in enumerate(uploaded_images, start=1):
        if f and f.filename:
            try:
                Image.open(f.stream)
                reference_text += f" Usa la imagen {idx} solo como referencia de forma y silueta."
            except Exception:
                pass

    return f"""
Crea un logo profesional para la marca "{brand_name}".

Contexto de marca:
{brand_description}

{reference_text}

Características obligatorias:
- Logo vectorial
- Minimalista
- Elegante
- Escalable
- Branding premium
- Fondo transparente
- Sin mockups
- Sin texto adicional
- Formas claras y definidas
""".strip()

# -----------------------------------
# Prompt Estrategia (Gemini)
# -----------------------------------
def generate_brand_text(brand_name, brand_description, age):
    prompt = f"""
Actúa como un estratega senior de branding, psicología del consumidor y semiótica.

Datos de entrada:
- Nombre de la marca: "{brand_name}"
- Descripción de la marca: "{brand_description}"
- Edad promedio de la audiencia: {age}

Primero, determina implícitamente el perfil generacional según la edad:
- Audiencias jóvenes: creativas, lúdicas, emocionales, con rasgos de neuroticismo, estética gamer o experimental.
- Millennials: alta apertura a la experiencia, búsqueda de significado, identidad y emociones auténticas.
- Audiencias adultas: racionales, informativas, orientadas a confianza, utilidad y claridad.

Luego:
- Define los rasgos de personalidad dominantes (Big Five de forma implícita).
- Analiza semántica y metafóricamente el nombre y la descripción de la marca.
- Identifica emociones, símbolos y palabras clave implícitas.
- Conecta esos elementos con los sentimientos dominantes de la audiencia.

Genera un ÚNICO TEXTO en español con EXACTAMENTE esta estructura:

PERFIL DE AUDIENCIA:
(descripción psicológica y generacional)

INSIGHT EMOCIONAL:
(frase corta, poderosa, basada en sentimiento y rasgos psicológicos)

ESTRATEGIA DE MARKETING:
(tono, narrativa, cómo debe comunicarse la marca para resonar con esta audiencia)

No uses listas numeradas.
No uses JSON.
No agregues explicaciones fuera de esta estructura.
"""

    response = gemini_model.generate_content(prompt)
    return response.text.strip()

# -----------------------------------
# Routes
# -----------------------------------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
    try:
        brand_name = request.form.get("title", "").strip()
        brand_description = request.form.get("theme", "").strip()
        age = int(request.form.get("age", 30))

        element1 = request.files.get("element1")
        element2 = request.files.get("element2")

        # ---------- LOGO ----------
        img_bytes = None
        logo_error = None

        try:
            logo_prompt = build_logo_prompt(
                brand_name,
                brand_description,
                [element1, element2]
            )

            dalle_response = openai.Image.create(
                model="dall-e-3",
                prompt=logo_prompt,
                size="1024x1024",
                n=1
            )

            image_url = dalle_response["data"][0]["url"]
            img_bytes = requests.get(image_url, timeout=30).content

        except Exception as e:
            logo_error = f"Error DALL·E: {str(e)}"

        if not img_bytes:
            with open("static/placeholder.png", "rb") as f:
                img_bytes = f.read()

        # ---------- TEXTO ESTRATÉGICO ----------
        try:
            strategy_text = generate_brand_text(
                brand_name,
                brand_description,
                age
            )
        except Exception:
            strategy_text = "No se pudo generar el contenido estratégico."

        # ---------- RESPUESTA ----------
        return jsonify({
            "logo": base64.b64encode(img_bytes).decode("utf-8"),
            "strategy_text": strategy_text,
            "error": logo_error
        })

    except Exception as e:
        return jsonify({
            "logo": None,
            "strategy_text": None,
            "error": f"Error inesperado: {str(e)}"
        })

# -----------------------------------
# Run
# -----------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
