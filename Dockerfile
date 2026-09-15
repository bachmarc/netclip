# NetClip — LAN-Zwischenablage (Story 03-01, Design §6)
# Layer-Caching: Abhängigkeiten zuerst installieren, dann Code kopieren.
FROM python:3.12-slim

WORKDIR /app

# 1) Abhängigkeiten (seltener ändernd als Code → besserer Layer-Cache)
COPY requirements.txt pyproject.toml ./
RUN pip install --no-cache-dir -r requirements.txt

# 2) Anwendungscode
COPY src/ ./src/

# 3) Non-root User (Akzeptanzkriterium: kein Root im Container)
RUN useradd --create-home netclip
USER netclip

EXPOSE 8000

CMD ["python", "-m", "src.adapters.main"]