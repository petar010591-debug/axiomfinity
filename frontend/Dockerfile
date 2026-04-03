FROM node:20-alpine AS build

WORKDIR /app

COPY package.json ./
COPY yarn.lock* ./
RUN yarn install

COPY . .

# Build with empty backend URL - nginx proxies /api to backend at runtime
ENV REACT_APP_BACKEND_URL=""

RUN yarn build

FROM nginx:alpine

# Remove default nginx config
RUN rm -f /etc/nginx/conf.d/default.conf

COPY --from=build /app/build /usr/share/nginx/html

# Template is auto-processed by nginx:alpine entrypoint (envsubst)
# ${BACKEND_URL} and ${PORT} are replaced at container startup
COPY nginx.conf.template /etc/nginx/templates/default.conf.template

# Railway sets PORT env var; default to 3000
ENV PORT=3000

EXPOSE 3000
