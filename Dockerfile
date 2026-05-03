# Stage 1: Build the Vite React app
FROM node:20-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
# We need VITE_GEMINI_API_KEY available at build time if we are bundling it
# For Cloud Run, you can pass this during Cloud Build or deployment.
ARG VITE_GEMINI_API_KEY
ENV VITE_GEMINI_API_KEY=$VITE_GEMINI_API_KEY
RUN npm run build

# Stage 2: Serve the app with Nginx
FROM nginx:alpine
# Copy the built assets to the Nginx html directory
COPY --from=build /app/dist /usr/share/nginx/html
# Copy custom Nginx configuration if needed (optional)
# COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose the port Cloud Run expects
EXPOSE 8080

# Cloud run requires the container to listen on the port defined by the PORT environment variable.
# By default, nginx listens on port 80. We need to override the default config.
CMD sed -i -e 's/80/8080/g' /etc/nginx/conf.d/default.conf && nginx -g 'daemon off;'
