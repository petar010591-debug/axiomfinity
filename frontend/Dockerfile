FROM node:20-alpine AS build

WORKDIR /app

COPY package.json ./
COPY yarn.lock* ./
RUN yarn install

COPY . .

ARG REACT_APP_BACKEND_URL
ENV REACT_APP_BACKEND_URL=$REACT_APP_BACKEND_URL

RUN yarn build

# Generate nginx config with proper HTTPS proxy for sitemaps
RUN BACKEND="${REACT_APP_BACKEND_URL}" && \
    cat > /tmp/nginx.conf << NGINXEOF
resolver 8.8.8.8 1.1.1.1 valid=30s;

server {
    listen 3000;
    server_name _;
    root /usr/share/nginx/html;
    index index.html;

    location = /sitemap.xml {
        proxy_pass ${BACKEND}/api/sitemap.xml;
        proxy_ssl_server_name on;
        proxy_set_header Host \$host;
        proxy_set_header Accept "application/xml";
    }

    location = /news-sitemap.xml {
        proxy_pass ${BACKEND}/api/news-sitemap.xml;
        proxy_ssl_server_name on;
        proxy_set_header Host \$host;
        proxy_set_header Accept "application/xml";
    }

    location / {
        try_files \$uri \$uri/ /index.html;
    }

    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)\$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
NGINXEOF

FROM nginx:alpine

RUN rm -f /etc/nginx/conf.d/default.conf

COPY --from=build /app/build /usr/share/nginx/html
COPY --from=build /tmp/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 3000

CMD ["nginx", "-g", "daemon off;"]
