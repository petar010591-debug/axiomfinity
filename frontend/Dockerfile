FROM node:20-alpine AS build

WORKDIR /app

COPY package.json ./
COPY yarn.lock* ./
RUN yarn install

COPY . .

ARG REACT_APP_BACKEND_URL
ENV REACT_APP_BACKEND_URL=$REACT_APP_BACKEND_URL

RUN yarn build
RUN echo "$REACT_APP_BACKEND_URL" > /tmp/backend_url

FROM node:20-alpine

WORKDIR /app

RUN npm install express

COPY --from=build /app/build ./build
COPY --from=build /tmp/backend_url /tmp/backend_url
COPY server.js .

EXPOSE 3000

CMD ["node", "server.js"]
