from flask import Flask, render_template, request, send_file, jsonify
from io import BytesIO
from PIL import Image

app = Flask(__name__)

# Control de creación por usuario/IP
created_logos = {}

# Carpeta corpus
CORPUS_FOLDER = "corpus"

def build_logo_json(title, style_corpus, theme, uploaded_elements):
    elements_features = []
    for i, elem in enumerate(uploaded_elements):
        if elem:
            features = {
                "filename": elem.filename,
                "layer": i+1,
                "gestalt": ["figura_fondo","cierre"] if i == 0 else ["proximidad","similitud"],
                "simplification": "geometrica"
            }
            elements_features.append(features)

    logo_json = {
        "brand": {
            "name": title,
            "industry": theme.get("industry", "general"),
            "values": theme.get("values", [])
        },
        "logo_specs": {
            "type": "iconic",
            "format": "vector",
            "colors": theme.get("colors", ["#1B998B", "#E6F0EA"]),
            "style": theme.get("style", "minimalista, elegante, geométrico")
        },
        "composition": {
            "elements": elements_features,
            "radial_mesh": {
                "layers": 2,
                "sectors": 5,
                "radius": 100,
                "concentric_divisions": [50,80]
            },
            "rules": {
                "symmetry": "radial",
                "proportions": "armonicos, regla_aurica",
                "balance": "visual"
            }
        },
        "typography": {
            "integration": True,
            "letters_in_icon": True,
            "style": "geométrica, minimalista"
        },
        "gestalt_principles": ["proximidad","similitud","continuidad","cierre","figura_fondo","pregnancia"],
        "output_instructions": {
            "file_type": "SVG",
            "scalable": True,
            "space_negative": True,
            "minimalism": True,
            "readability": "alta"
        },
        "creative_instructions": {
            "merge_elements": True,
            "abstract_shapes": True,
            "harmonic_arrangement": True,
            "repetition": "radial o concéntrica",
            "simplification": "maxima pero reconocible"
        },
        "style_corpus": style_corpus
    }

    return logo_json

def generate_prompt_from_json(logo_json):
    brand = logo_json["brand"]
    specs = logo_json["logo_specs"]
    comp = logo_json["composition"]
    gestalt = logo_json["gestalt_principles"]
    creative = logo_json["creative_instructions"]

    prompt = f"""
Crea un logo minimalista y elegante para la marca {brand['name']}, enfocada en {brand['industry']} y con valores {', '.join(brand['values'])}.
El diseño debe ser {specs['style']} en formato {specs['format']} con colores {', '.join(specs['colors'])}.

Elementos principales:
"""
    for el in comp["elements"]:
        prompt += f"- {el['filename']}, capa {el['layer']}, simplificación {el['simplification']}, aplicando Gestalt: {', '.join(el['gestalt'])}\n"

    prompt += f"""
Organiza los elementos con malla radial de {comp['radial_mesh']['layers']} capas y {comp['radial_mesh']['sectors']} sectores,
simetría {comp['rules']['symmetry']}, proporciones {comp['rules']['proportions']}, balance {comp['rules']['balance']}.

Integrar tipografía geométrica y minimalista dentro de los elementos si es necesario.

Aplicar principios Gestalt: {', '.join(gestalt)}.

Seguir instrucciones creativas: {', '.join([f'{k}: {v}' for k,v in creative.items()])}.

Resultado escalable, vectorial, con espacio negativo y legible.
"""
    return prompt.strip()

def generate_logo_image(prompt_text):
    img = Image.new("RGBA", (1024,1024), (255,255,255,0))
    return img

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    user_ip = request.remote_addr

    title = request.form.get("title","").strip()
    theme_text = request.form.get("theme","")
    style_corpus = request.form.getlist("style_corpus") or ["estilo1"]

    element1 = request.files.get("element1")
    element2 = request.files.get("element2")
    uploaded_elements = [element1, element2]

    if not title:
        return jsonify({"error":"Title is required"}),400

    if user_ip in created_logos and created_logos[user_ip] == title:
        return jsonify({"error":"Logo already created for this title"}),403

    theme = {
        "industry": "sostenibilidad y medio ambiente",
        "values": theme_text.split(",") if theme_text else ["naturaleza","innovación","armonía"],
        "colors": ["#1B998B", "#E6F0EA"],
        "style": "minimalista, elegante, geométrico"
    }

    logo_json = build_logo_json(title, style_corpus, theme, uploaded_elements)
    prompt_text = generate_prompt_from_json(logo_json)

    logo_img = generate_logo_image(prompt_text)

    created_logos[user_ip] = title

    img_io = BytesIO()
    logo_img.save(img_io, 'PNG')
    img_io.seek(0)
    return send_file(img_io, mimetype='image/png', download_name=f"{title}.png")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
