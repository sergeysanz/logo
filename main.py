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
# Utils — perfil generacional
# -----------------------------------
def get_generation_profile(age):
    if age < 23:
        return "Generación Z: creativa, experimental, emocional, estética digital y gamer"
    elif age <= 38:
        return "Millennial: alta apertura a la experiencia, búsqueda de significado, sensibilidad estética y emocional"
    elif age <= 55:
        return "Generación X: racional, funcional, orientada a claridad, estructura y confianza"
    else:
        return "Audiencia senior: sobria, conservadora, institucional, orientada a estabilidad y credibilidad"

def get_gender_expression(gender):
    if gender == "mujer":
        return "expresión visual fluida, balanceada, sensible, con curvas sutiles y elegancia orgánica"
    elif gender == "hombre":
        return "expresión visual estructurada, precisa, con tensión geométrica y control formal"
    else:
        return "expresión visual neutral, modular, atemporal y universal"

# -----------------------------------
# Prompt Logo (DALL·E — PRO)
# -----------------------------------
def build_logo_prompt(brand_name, brand_description, gender, age, uploaded_images):
    reference_text = ""

    for idx, f in enumerate(uploaded_images, start=1):
        if f and f.filename:
            try:
                Image.open(f.stream)
                reference_text += f" Usa la imagen {idx} solo como referencia de silueta o ritmo visual."
            except Exception:
                pass

    generation_profile = get_generation_profile(age)
    gender_expression = get_gender_expression(gender)

    return f"""
Diseña un logo profesional de alto nivel para la marca "{brand_name}".

Contexto de marca:
{brand_description}

Perfil de audiencia:
- Edad promedio: {age}
- {generation_profile}
- Género: {gender}
- Lenguaje visual esperado: {gender_expression}

Dirección creativa:
- Branding editorial contemporáneo
- Estética de estudios premiados en Awwwards
- Conceptual antes que decorativo
- Uso inteligente del vacío y del ritmo
- Forma con intención semántica
- Alta legibilidad en pequeño tamaño

Restricciones estrictas:
- Logo vectorial
- Minimalista, pero con carácter
- Elegante y profesional
- Fondo transparente
- Sin mockups
- Sin textos adicionales
- No ilustración infantil
- No efectos 3D
- No sombras

{reference_text}

El resultado debe sentirse diseñado por un estudio de branding premium, no por un generador automático.
""".strip()

# -----------------------------------
# Prompt Estrategia (Gemini)
# -----------------------------------
def generate_brand_text(brand_name, brand_description, age):
    prompt = f"""
Eres un estratega senior de branding y psicología del consumidor.

Marca: {brand_name}
Descripción: {brand_description}
Edad promedio de la audiencia: {age}

Determina implícitamente el perfil generacional y los rasgos de personalidad dominantes.
Analiza el nombre y la descripción desde una lectura semántica y metafórica.

Genera un ÚNICO TEXTO en español con EXACTAMENTE esta estructura:

PERFIL DE AUDIENCIA:
(descripción psicológica y generacional)

INSIGHT EMOCIONAL:
(frase corta, potente y emocional)

ESTRATEGIA DE MARKETING:
(tono y narrativa de comunicación)

No uses listas.
No uses JSON.
No agregues texto adicional.
"""

    response = gemini_model.generate_content(prompt)

    if not hasattr(response, "text") or not response.text:
        raise ValueError("Gemini no devolvió texto")

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
        gender = request.form.get("gender", "todos")

        age_raw = request.form.get("age_range", "").strip()
        age = int(age_raw) if age_raw.isdigit() else 30

        element1 = request.files.get("element1")
        element2 = request.files.get("element2")

        # ---------- LOGO ----------
        img_bytes = None
        logo_error = None

        try:
            logo_prompt = build_logo_prompt(
                brand_name,
                brand_description,
                gender,
                age,
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

        # ---------- TEXTO ----------
        try:
            strategy_text = generate_brand_text(
                brand_name,
                brand_description,
                age
            )
        except Exception:
            strategy_text = "No se pudo generar el contenido estratégico."

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
