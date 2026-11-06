FROM alpine:3.20 AS certs

RUN apk add --no-cache openssl

RUN mkdir /certs \
    && openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -subj "/CN=localhost" \
        -addext "subjectAltName=DNS:localhost,IP:127.0.0.1" \
        -keyout /certs/server.key \
        -out /certs/server.crt

FROM nginxinc/nginx-unprivileged:1.27-alpine AS dev

COPY dev.conf /etc/nginx/conf.d/default.conf

FROM nginxinc/nginx-unprivileged:1.27-alpine AS prod

COPY --from=certs --chown=101:101 /certs/ /etc/nginx/certs/
COPY prod.conf /etc/nginx/conf.d/default.conf
