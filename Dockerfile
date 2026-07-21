
# Usar uma imagem base do Python mais recente (Debian Bookworm)
FROM python:3.11-slim-bookworm

# Definir o diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema necessárias para o Playwright
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Copiar o arquivo de requisitos e instalar as dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Instalar os navegadores do Playwright e suas dependências de sistema
RUN playwright install --with-deps chromium

# Copiar o script Python
COPY benner_rpa.py .

# Comando padrão
CMD ["python", "benner_rpa.py"]
