import streamlit as st
import pytesseract
from PIL import Image
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
        text = pytesseract.image_to_string(image, lang='fra')

        # Extraction par regex ou logique simple
        nom = re.search(r"(?i)(\b[A-Z][a-zéèêàâîïôûç-]{2,}\b)", text)
        numero = re.search(r"(\d{1,3}/\d{1,3})", text)
        illustrateur = re.search(r"Illustrateur[ :]*([^\n]+)", text)
        extension = re.search(r"\d{3}/\d{3} (.+)", text)
        rarete = "Commune" if "●" in text else ("Peu commune" if "◆" in text else ("Rare" if "★" in text else "?"))
        type_ = "Électrik" if "⚡" in text else ("Feu" if "🔥" in text else ("Eau" if "💧" in text else "?"))

        results.append({
            "Nom": nom.group(1) if nom else "?",
            "Numéro": numero.group(1) if numero else "?",
            "Extension": extension.group(1).strip() if extension else "?",
            "Illustrateur": illustrateur.group(1).strip() if illustrateur else "?",
            "Rareté": rarete,
            "Type": type_,
            "Fichier": uploaded_file.name
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
