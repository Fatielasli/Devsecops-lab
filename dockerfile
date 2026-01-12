FROM python:3.9-slim

# Variables d’environnement
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Répertoire de travail
WORKDIR /app

# Copier les dépendances
COPY api/requirements.txt .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code source
COPY api/ .

# Exposer le port Flask
EXPOSE 5000

# Lancer l’application
CMD ["python", "app.py"]
