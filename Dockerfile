FROM python:3.10-slim

# Installer les dépendances système
RUN apt-get update && \
    apt-get install -y tesseract-ocr tesseract-ocr-fra libglib2.0-0 libsm6 libxrender1 libxext6 && \
    apt-get clean

# Définir la variable d'environnement Tesseract
ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata/

# Dossier de travail
WORKDIR /app

# Installer les dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier l'app
COPY . .

# Exposer le port Streamlit
EXPOSE 8501

# Lancer l'app
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.enableCORS=false"]
