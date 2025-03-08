# Stage 1: Build the frontend using Node
FROM node:18-alpine AS builder
WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN ls -la
RUN npm ci

# Copy the rest of the project files
COPY . .

# Debug: Print directory contents before build
RUN echo "Contents before build:" && ls -la

# Run the build script
RUN npm run build

# Debug: Print directory contents after build
RUN echo "Contents after build:" && ls -la dist

# Stage 2: Serve the built static files using Nginx
FROM nginx:stable-alpine

# Set environment variables for production
ENV NODE_ENV production

# Copy the build output from the previous stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy custom Nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Debug: Print directory contents in Nginx
RUN echo "Contents of /usr/share/nginx/html:" && ls -la /usr/share/nginx/html

# Expose port 80 to serve the app
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]