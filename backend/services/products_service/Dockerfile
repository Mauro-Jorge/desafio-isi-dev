# Usar uma imagem base oficial do Python que seja multi-plataforma (inclui arm64)
FROM python:3.11-slim

# Definir o diretório de trabalho dentro do contêiner
WORKDIR /app

# Instalar dependências de build necessárias pelo psycopg
RUN apt-get update && apt-get install -y build-essential

# Copiar o arquivo de dependências primeiro para aproveitar o cache do Docker
COPY ./requirements.txt /app/requirements.txt

# Instalar as dependências
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o resto do código da aplicação para o diretório de trabalho
# O volume no docker-compose irá sobrepor isso, permitindo hot-reload
COPY ./app /app

# O comando para iniciar a aplicação com uvicorn
# O host 0.0.0.0 torna a aplicação acessível de fora do contêiner
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]