# ============================================================================
# Lazy Rabbit Agent — Frontend
# Multi-stage build: npm build → nginx serve
# ============================================================================

# ---------- Stage 1: Build ----------
FROM node:20-alpine AS builder

WORKDIR /build

# Copy dependency files first (cache layer)
COPY package.json package-lock.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Build for production
RUN npm run build

# ---------- Stage 2: Production (static files only) ----------
FROM alpine:3.20 AS production

# Just copy the built files — nginx container will serve them via volume
WORKDIR /dist
COPY --from=builder /build/dist .
