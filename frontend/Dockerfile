# 1) Build stage
FROM node:18-alpine AS builder

WORKDIR /app

# copy package manifests
COPY frontend/package.json frontend/package-lock.json ./

# install deps
RUN npm ci --legacy-peer-deps

# copy the rest of your Next.js code
COPY frontend/app ./app
COPY frontend/public ./public

# build the Next.js app
RUN npm run build

# 2) Production image
FROM node:18-alpine

WORKDIR /app

# only copy over the build output + production deps
COPY --from=builder /app/package.json ./
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public

# expose the port Next.js listens on
EXPOSE 3000

# run in production mode
ENV NODE_ENV=production
CMD ["npm", "run", "start"]
