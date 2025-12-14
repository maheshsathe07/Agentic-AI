FROM node:20-alpine3.19 AS base

# stage 1: build stuff
FROM base AS builder

WORKDIR /home/build

COPY package*.json .
COPY tsconfig.json .

RUN npm install

COPY src/ src/

RUN npm run build

# stage 2: runner
FROM base AS runner

WORKDIR /home/app

# this will copy only the built files from the builder stage and delete the stage 1 files
COPY --from=builder /home/build/dist dist/
COPY --from=builder /home/build/package*.json .
# here we won't copy tsconfig.json because it's not needed to run the app
# also we won't copy src/ because we already have the built files in dist/

RUN npm install --omit=dev
# --omit=dev ensures that only production dependencies are installed, not going to install dev dependencies in the final image

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nodejs

USER nodejs

EXPOSE 3000
ENV PORT=3000

CMD ["npm", "start"]