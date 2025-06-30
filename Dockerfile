FROM python:3.10-slim

# Ustaw katalog roboczy
WORKDIR /app

# Najpierw skopiuj requirements (zależności)
COPY requirements.txt /app/requirements.txt

# Instaluj zależności (przed resztą — cache!)
RUN pip install --no-cache-dir -r requirements.txt

# Następnie skopiuj resztę kodu
COPY . /app

# Domyślna komenda uruchamiająca aplikację
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
