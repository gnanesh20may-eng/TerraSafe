FROM node:20-alpine

WORKDIR /app

COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install --silent

COPY frontend .

EXPOSE 3000
CMD ["npm", "run", "dev", "--", "--hostname", "0.0.0.0"]
