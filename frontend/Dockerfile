# Stage 1: Build the frontend using Node
FROM node:18-alpine AS builder
WORKDIR /app

# Install dependencies
# Copy package files first to leverage Docker cache
COPY package.json package-lock.json* ./
RUN npm install

# Copy the rest of the project files
COPY . .

# Run the build script as defined in package.json ("vite build" by default)
RUN npm run build

# Stage 2: Serve the built static files using Nginx
FROM nginx:stable-alpine
# Copy the build output from the previous stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Expose port 80 to serve the app
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]