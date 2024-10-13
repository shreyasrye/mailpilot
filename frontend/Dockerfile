# Use an official Node.js image as the base
FROM node:18

# Set the working directory inside the container
WORKDIR /app

# Install Expo CLI globally
RUN npm install -g expo-cli

# Copy package.json and package-lock.json from MailPilotApp
COPY MailPilotApp/package*.json ./MailPilotApp/

# Navigate to MailPilotApp and install dependencies, including expo dependencies
WORKDIR /app/MailPilotApp
RUN npm install && npx expo install @expo/metro-runtime

# Copy the entire MailPilotApp directory to the container
COPY MailPilotApp/ ./MailPilotApp/

# Expose the correct web port (19006)
EXPOSE 19006

# Start the React Native application for web using Expo
CMD ["npx", "expo", "start", "--web"]
