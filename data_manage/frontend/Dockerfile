FROM node:20-alpine AS builder

WORKDIR /app
COPY frontend/package*.json ./
RUN if [ -f package-lock.json ]; then npm ci; else npm install; fi
COPY frontend/ .
RUN npm run build

FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY frontend/nginx.conf /etc/nginx/templates/default.conf.template

ENV API_PROXY_URL=http://backend:8000

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
