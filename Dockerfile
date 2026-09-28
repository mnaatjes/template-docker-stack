# syntax=docker/dockerfile:1.4
# Sample multi-stage Dockerfile for bespoke container microservices

FROM alpine:3.20 AS base
# hadolint ignore=DL3018
RUN apk add --no-cache ca-certificates tzdata


FROM base AS builder
WORKDIR /build
# Add compilation steps here if applicable

FROM base AS runtime
WORKDIR /app
# Run as dedicated unprivileged user
RUN addgroup -g 1000 appgroup && \
    adduser -u 1000 -G appgroup -s /bin/sh -D appuser
USER appuser

EXPOSE 8080
CMD ["echo", "Container stack initialized"]
