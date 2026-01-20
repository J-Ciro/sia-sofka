FROM node:22-alpine

# Set working directory
WORKDIR /app

# Copy package files
COPY package.json ./

# Install dependencies (npm install works even without package-lock.json)
RUN npm install

# Copy application code
COPY . .

# Expose port
EXPOSE 3000

# Start: install deps (sync with host package.json) and run dev server
CMD ["sh", "-c", "npm install && npm run dev -- --host 0.0.0.0"]

