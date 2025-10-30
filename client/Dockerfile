FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy application code
COPY . .

# Build for production
RUN npm run build

# Install serve to serve static files
RUN npm install -g serve

# Expose port
EXPOSE 8080

# Serve built files
CMD ["serve", "-s", "dist", "-l", "8080"]
