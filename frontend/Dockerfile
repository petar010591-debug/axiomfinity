FROM node:20-alpine AS build

WORKDIR /app

COPY package.json ./
COPY yarn.lock* ./
RUN yarn install

COPY . .

ARG REACT_APP_BACKEND_URL
ENV REACT_APP_BACKEND_URL=$REACT_APP_BACKEND_URL

RUN yarn build

FROM nginx:alpine

# Re-declare ARG so it's available in this stage
ARG REACT_APP_BACKEND_URL

RUN rm -f /etc/nginx/conf.d/default.conf

COPY --from=build /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Replace placeholder with actual backend URL at build time
RUN sed -i "s|__BACKEND_URL__|${REACT_APP_BACKEND_URL}|g" /etc/nginx/conf.d/default.conf

EXPOSE 3000

CMD ["nginx", "-g", "daemon off;"]
