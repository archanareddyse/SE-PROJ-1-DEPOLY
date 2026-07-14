# Use Node image
FROM node:20

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy project
COPY . .

# Expose Vite port
EXPOSE 5173

# Start Vite
CMD ["npm", "run", "dev", "--", "--host"]
