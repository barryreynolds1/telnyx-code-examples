FROM node:20-slim

WORKDIR /app

COPY package*.json ./
RUN npm ci --omit=dev

COPY . .

RUN groupadd -r appuser && useradd -r -g appuser appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=5s CMD node -e "fetch('http://localhost:5000/health').then(r => process.exit(r.ok ? 0 : 1))"

CMD ["node", "server.js"]
