import streamlit as st
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import pandas as pd
import re
import os
import tempfile

# 🔧 Spécifie manuellement le chemin de Tesseract
pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

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

        original_image = Image.open(tmp_path)
        st.image(original_image, caption=f"Image originale : {uploaded_file.name}", use_container_width=True)

        # Test OCR brut sans traitement
        try:
            raw_text = pytesseract.image_to_string(original_image, lang='fra').strip()
        except Exception as e:
            st.error(f"❌ OCR brut échoué : {e}")
            raw_text = ""

        if raw_text:
            st.info("✅ Texte détecté sur image originale sans traitement :")
            st.code(raw_text)
            text = raw_text  # Utiliser le texte brut s'il est meilleur
        else:
            st.warning("❌ Aucun texte détecté en OCR brut. Tentative avec image prétraitée...")

            # Prétraitement de l'image pour améliorer l'OCR
            pre_image = original_image.convert("L")
            pre_image = pre_image.filter(ImageFilter.MedianFilter())
            enhancer = ImageEnhance.Contrast(pre_image)
            pre_image = enhancer.enhance(2)
            st.image(pre_image, caption="Image après traitement (debug)", use_container_width=True)

            try:
                text = pytesseract.image_to_string(pre_image, lang='fra').strip()
            except Exception as e:
                st.error(f"❌ OCR échoué sur image prétraitée : {e}")
                text = ""

            if not text:
                st.error("❌ Toujours aucun texte détecté. Tesseract ne voit rien sur cette image.")

        st.markdown(f"**🖼️ OCR pour le fichier : {uploaded_file.name}**")
        st.code(text if text else "(vide)")

        # Extraction améliorée par regex
        premieres_lignes = text.split('\n')[:5]
        nom_match = None
        for ligne in premieres_lignes:
            mots = re.findall(r"\b([A-ZÉ][a-zéèêàâîïôûç-]{2,})\b", ligne)
            for mot in mots:
                if mot.lower() != "pokémon":
                    nom_match = re.match(r".*", mot)
                    break
            if nom_match:
                break

        numero_match = re.search(r"(\d{1,3})\s*[/lI|]{1}\s*(\d{1,3})", text)
        illustrateur_match = re.search(r"(?:Illustrateur|Illus\.?)[ :]*([^\n]+)", text)
        extension_match = re.search(r"\d{3}/\d{3} (.+)", text)

        rarete = "Commune" if "●" in text else ("Peu commune" if "◆" in text else ("Rare" if "★" in text else "?"))

        nom = nom_match.group(0) if nom_match else "?"
        numero = f"{numero_match.group(1)}/{numero_match.group(2)}" if numero_match else "?"
        illustrateur = illustrateur_match.group(1).strip() if illustrateur_match else "?"
        extension = extension_match.group(1).strip() if extension_match else "?"

        def format_result(label, value):
            color = "red" if value == "?" else "green"
            return f"<span style='color:{color}'><strong>{label}:</strong> {value}</span>"

        st.markdown(format_result("Nom", nom), unsafe_allow_html=True)
        st.markdown(format_result("Numéro", numero), unsafe_allow_html=True)
        st.markdown(format_result("Extension", extension), unsafe_allow_html=True)
        st.markdown(format_result("Illustrateur", illustrateur), unsafe_allow_html=True)
        st.markdown(format_result("Rareté", rarete), unsafe_allow_html=True)

        results.append({
            "Nom": nom,
            "Numéro": numero,
            "Extension": extension,
            "Illustrateur": illustrateur,
            "Rareté": rarete,
            "Fichier": uploaded_file.name,
            "Texte OCR": text.replace('\n', ' | ').strip()
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
