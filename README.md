# MailPilot

MailPilot is a comprehensive email management system that leverages machine learning and AI to classify, summarize, and manage emails efficiently. This project includes a backend service for processing emails and a frontend React Native application for user interaction.

## Table of Contents

- [MailPilot](#mailpilot)
  - [Table of Contents](#table-of-contents)
  - [Project Description](#project-description)
  - [Features](#features)
  - [Setup](#setup)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
  - [Usage](#usage)
    - [Running the Backend](#running-the-backend)
    - [Running the Frontend](#running-the-frontend)
  - [Configuration](#configuration)

## Project Description

MailPilot is designed to help users manage their emails more effectively by classifying emails into different categories, summarizing email content, and providing a user-friendly interface for interaction. The backend service processes emails using machine learning models, while the frontend React Native application provides a seamless user experience.

## Features

- **Email Classification**: Automatically classify emails into predefined categories.
- **Email Summarization**: Generate concise summaries of email content.
- **User-Friendly Interface**: Intuitive React Native application for managing emails.
- **Integration with Gmail API**: Fetch and process emails from Gmail.

## Setup

### Prerequisites

- [Docker](https://www.docker.com/get-started)
- [Node.js](https://nodejs.org/) (for local development)
- [Python 3.8+](https://www.python.org/downloads/) (for backend development)

### Installation

1. **Clone the Repository**:

    ```sh
    git clone https://github.com/yourusername/mailpilot.git
    cd mailpilot
    ```

2. **Backend Setup**:

    - Navigate to the backend directory:

        ```sh
        cd backend
        ```

    - Create a virtual environment and activate it:

        ```sh
        python3 -m venv venv
        source venv/bin/activate
        ```

    - Install the required Python packages:

        ```sh
        pip install -r requirements.txt
        ```

3. **Frontend Setup**:

    - Navigate to the frontend directory:

        ```sh
        cd frontend/MailPilotApp
        ```

    - Install the required Node.js packages:

        ```sh
        npm install
        ```

## Usage

### Running the Backend

1. **Start the Backend Service**:

    ```sh
    cd backend
    source venv/bin/activate
    python app.py
    ```

### Running the Frontend

1. **Start the React Native Application**:

    ```sh
    cd frontend/MailPilotApp
    npm start
    ```

2. **Run on iOS**:

    ```sh
    npx react-native run-ios
    ```

3. **Run on Android**:

    ```sh
    npx react-native run-android
    ```

## Configuration

1. **Backend Configuration**:

    - Create a [`config.json`](command:_github.copilot.openRelativePath?%5B%7B%22scheme%22%3A%22file%22%2C%22authority%22%3A%22%22%2C%22path%22%3A%22%2FUsers%2Fshreyasrai%2FDocuments%2Fmailpilot%2Fconfig.json%22%2C%22query%22%3A%22%22%2C%22fragment%22%3A%22%22%7D%2C%229c934445-ea61-43dd-b9e7-32e42923b145%22%5D "/Users/shreyasrai/Documents/mailpilot/config.json") file in the [`backend`](command:_github.copilot.openRelativePath?%5B%7B%22scheme%22%3A%22file%22%2C%22authority%22%3A%22%22%2C%22path%22%3A%22%2FUsers%2Fshreyasrai%2FDocuments%2Fmailpilot%2Fbackend%22%2C%22query%22%3A%22%22%2C%22fragment%22%3A%22%22%7D%2C%229c934445-ea61-43dd-b9e7-32e42923b145%22%5D "/Users/shreyasrai/Documents/mailpilot/backend") directory with the following structure:

        ```json
        {
            "openai": {
                "api_key": "your-openai-api-key"
            },
            "pinecone": {
                "api_key": "your-pinecone-api-key",
                "environment": "your-pinecone-environment",
                "index": "your-pinecone-index"
            },
            "gmail_api": {
                "date_range": "your-date-range"
            }
        }
        ```

2. **Frontend Configuration**:

    - Ensure that the `MailPilotApp` directory contains all necessary configuration files, such as `babel.config.js`, `metro.config.js`, and others.