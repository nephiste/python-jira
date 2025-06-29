# Dockerfile
FROM python:3.10-slim

# Ustaw katalog roboczy
WORKDIR /app

# Skopiuj wszystko do obrazu
COPY . /app

# Zainstaluj zależności
RUN pip install --no-cache-dir -r requirements.txt

# Domyślna komenda (możesz też użyć gunicorn do produkcji)
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
