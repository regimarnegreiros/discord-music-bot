FROM python:3.12-slim

# Evita geração de arquivos .pyc e força flush imediato de logs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Instala ffmpeg, certificados e bibliotecas necessárias para áudio no Discord
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    ca-certificates \
    libopus0 \
    && rm -rf /var/lib/apt/lists/*

# Instala dependências Python em camada separada para aproveitar cache do Docker
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copia o restante dos arquivos da aplicação
COPY . .

CMD ["python", "main.py"]
