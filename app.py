import streamlit as st
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import pandas as pd
import re
import os
import tempfile

st.set_page_config(page_title="Scan Cartes Pokémon", layout="centered")
st.title("🧾 Scan Automatique de Cartes Pokémon")
st.write("Uploadez vos scans (.jpg ou .png) pour extraire les informations clés.")

uploaded_files = st.file_uploader("Uploader les cartes :", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

results = []

if uploaded_files:
    for uploaded_file in uploaded_files:
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(uploaded_file.read())
            tmp_path = tmp_file.name

        image = Image.open(tmp_path)

        # Afficher l'image originale pour debug visuel
        st.image(image, caption=f"Aperçu : {uploaded_file.name}", use_container_width=True)

        # Prétraitement de l'image pour améliorer l'OCR
        image = image.convert("L")  # Grayscale
        image = image.filter(ImageFilter.MedianFilter())
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2)

        text = pytesseract.image_to_string(image, lang='fra')

        st.markdown(f"<pre style='background-color:#111;color:#fff;padding:1em'><strong>🖼️ OCR pour le fichier : {uploaded_file.name}</strong>\n{text}</pre>", unsafe_allow_html=True)

        # Extraction par regex ou logique simple
        nom_match = re.search(r"(?i)(\b[A-Z][a-zéèêàâîïôûç-]{2,}\b)", text)
        numero_match = re.search(r"(\d{1,3}\s*/\s*\d{1,3})", text)
        illustrateur_match = re.search(r"(?:Illustrateur|Illus\.?)[ :]*([^\n]+)", text)
        extension_match = re.search(r"\d{3}/\d{3} (.+)", text)

        rarete = "Commune" if "●" in text else ("Peu commune" if "◆" in text else ("Rare" if "★" in text else "?"))
        type_ = "Électrik" if "⚡" in text else ("Feu" if "🔥" in text else ("Eau" if "💧" in text else "?"))

        nom = nom_match.group(1) if nom_match else "?"
        numero = numero_match.group(1) if numero_match else "?"
        illustrateur = illustrateur_match.group(1).strip() if illustrateur_match else "?"
        extension = extension_match.group(1).strip() if extension_match else "?"

        # Affichage des champs extraits dans les logs Streamlit avec couleur conditionnelle
        def format_result(label, value):
            color = "red" if value == "?" else "green"
            return f"<span style='color:{color}'><strong>{label}:</strong> {value}</span>"

        st.markdown(format_result("Nom", nom), unsafe_allow_html=True)
        st.markdown(format_result("Numéro", numero), unsafe_allow_html=True)
        st.markdown(format_result("Extension", extension), unsafe_allow_html=True)
        st.markdown(format_result("Illustrateur", illustrateur), unsafe_allow_html=True)
        st.markdown(format_result("Rareté", rarete), unsafe_allow_html=True)
        st.markdown(format_result("Type", type_), unsafe_allow_html=True)

        results.append({
            "Nom": nom,
            "Numéro": numero,
            "Extension": extension,
            "Illustrateur": illustrateur,
            "Rareté": rarete,
            "Type": type_,
            "Fichier": uploaded_file.name,
            "Texte OCR": text.replace('\n', ' | ')
        })

    df = pd.DataFrame(results)
    st.success("Extraction terminée ✅")
    st.dataframe(df)

    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Télécharger les résultats en CSV",
        data=csv,
        file_name="infos_cartes_pokemon.csv",
        mime="text/csv"
    )
