FROM node:20-alpine

WORKDIR /app

# Копируем package.json и package-lock.json (если есть)
COPY package*.json ./

# Устанавливаем зависимости
RUN npm install

# Копируем все исходные файлы
COPY . .

# Собираем приложение
RUN npm run build

# Экспонируем порт
EXPOSE 3000

# Используем vite preview
CMD ["npm", "run", "preview"]