FROM node:20-alpine AS build

WORKDIR /app

COPY package.json ./
COPY yarn.lock* ./
RUN yarn install

COPY . .

ARG REACT_APP_BACKEND_URL
ENV REACT_APP_BACKEND_URL=$REACT_APP_BACKEND_URL

RUN yarn build

# Generate nginx config with backend URL baked in
RUN echo "server {" > /tmp/nginx.conf && \
    echo "    listen 3000;" >> /tmp/nginx.conf && \
    echo "    server_name _;" >> /tmp/nginx.conf && \
    echo "    root /usr/share/nginx/html;" >> /tmp/nginx.conf && \
    echo "    index index.html;" >> /tmp/nginx.conf && \
    echo "" >> /tmp/nginx.conf && \
    echo "    location = /sitemap.xml {" >> /tmp/nginx.conf && \
    echo "        proxy_pass ${REACT_APP_BACKEND_URL}/api/sitemap.xml;" >> /tmp/nginx.conf && \
    echo "        proxy_set_header Host \$host;" >> /tmp/nginx.conf && \
    echo "    }" >> /tmp/nginx.conf && \
    echo "" >> /tmp/nginx.conf && \
    echo "    location = /news-sitemap.xml {" >> /tmp/nginx.conf && \
    echo "        proxy_pass ${REACT_APP_BACKEND_URL}/api/news-sitemap.xml;" >> /tmp/nginx.conf && \
    echo "        proxy_set_header Host \$host;" >> /tmp/nginx.conf && \
    echo "    }" >> /tmp/nginx.conf && \
    echo "" >> /tmp/nginx.conf && \
    echo "    location / {" >> /tmp/nginx.conf && \
    echo "        try_files \$uri \$uri/ /index.html;" >> /tmp/nginx.conf && \
    echo "    }" >> /tmp/nginx.conf && \
    echo "" >> /tmp/nginx.conf && \
    echo "    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)\$ {" >> /tmp/nginx.conf && \
    echo "        expires 1y;" >> /tmp/nginx.conf && \
    echo "        add_header Cache-Control \"public, immutable\";" >> /tmp/nginx.conf && \
    echo "    }" >> /tmp/nginx.conf && \
    echo "}" >> /tmp/nginx.conf

FROM nginx:alpine

RUN rm -f /etc/nginx/conf.d/default.conf

COPY --from=build /app/build /usr/share/nginx/html
COPY --from=build /tmp/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 3000

CMD ["nginx", "-g", "daemon off;"]
