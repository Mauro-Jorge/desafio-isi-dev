# Usar uma imagem base oficial do Node que seja multi-plataforma (inclui arm64)
FROM node:20-alpine

# Definir o diretório de trabalho
WORKDIR /app

# Copiar package.json e package-lock.json (se existir) para cachear as dependências
COPY package*.json ./

# Instalar as dependências do projeto
RUN npm install

# Copiar o restante do código-fonte
COPY . .

# Expor a porta que o Vite usa
EXPOSE 5173

# Comando para iniciar o servidor de desenvolvimento Vite
# O '--host' é essencial para que o servidor seja acessível de fora do contêiner
CMD ["npm", "run", "dev", "--", "--host"]