# TalentScout - AI Hiring Assistant

An intelligent Streamlit-based chatbot that streamlines the initial candidate screening process for TalentScout, a technology recruitment agency. The assistant uses Google Gemini AI to conduct structured, context-aware interviews and generates tailored technical questions based on candidates' declared tech stacks.

---

## 🌟 Features

### Core Functionality
- **Interactive Chat Interface**: A clean and professional UI built with Streamlit for seamless candidate interaction.
- **Systematic Information Gathering**: Collects essential candidate details including full name, email, phone number, years of experience, desired positions, location, and tech stack.
- **Robust Input Validation**: Implements strict checks for valid email formats, phone numbers, and rejects irrelevant or nonsensical answers (e.g., "nothing", "space") to maintain focus.

### AI-Powered Capabilities
- **Intelligent Conversation Flow**: Manages a multi-stage conversation using a state machine, ensuring a logical and coherent screening process.
- **Dynamic Question Generation**: Creates 3-5 tailored technical questions based on the candidate's declared tech stack and experience level using Google Gemini.
- **Sentiment Analysis**: Gauges candidate sentiment (Positive, Neutral, Negative) from their responses to provide high-level emotional analytics.
- **Fallback Handling**: Gracefully manages unexpected or misunderstood inputs by guiding the user back to the conversation's objective.

---

## 🛠️ Technical Architecture

### Core Components

* **`app.py`**: The main entry point for the Streamlit application. It handles the user interface, session state management, and renders the chat conversation.
* **`hiring_assistant.py`**: The core AI engine of the chatbot. It manages the conversation state, integrates with the Google Gemini API, generates questions, and processes all user input.
* **`data_validator.py`**: A utility module that provides robust data validation for user inputs like emails and phone numbers using regex, and sanitizes text to prevent security issues.

### AI Integration
* **Model**: The application utilizes Google's **Gemini 1.5 Flash** model, chosen for its balance of speed, intelligence, and cost-effectiveness.
* **API Client**: Interaction with the Gemini API is handled through the official `google-generativeai` Python library.
* **Security**: The Gemini API key is managed securely using environment variables and the `python-dotenv` library, ensuring that secrets are never hard-coded.

---

## 🧠 Prompt Engineering

The effectiveness of the chatbot relies on carefully crafted system prompts that guide the Gemini model's behavior.

* **Question Generation**: The prompt instructs the AI to act as an "expert technical interviewer" and to generate a specific number of practical questions that cover different aspects of a candidate's skills, such as coding, architecture, and best practices. It is also given the candidate's years of experience to tailor the difficulty of the questions.
* **Name Extraction**: A highly specific prompt is used to extract a candidate's full name from their introductory message. It is instructed to return only the name or the word 'NONE', which makes the model's output predictable and easy to parse.
* **Sentiment Analysis**: A concise prompt asks the model to analyze the sentiment of a candidate's response and return only a single keyword (POSITIVE, NEUTRAL, or NEGATIVE), ensuring a clean and consistent output for analytics.

---

## 🚀 Installation & Setup

### Prerequisites
- Python 3.11+
- A valid Google Gemini API key.

### Local or Cloud-Based Setup (Recommended: GitHub Codespaces)

1.  **Clone or upload the repository.**
    * For a cloud environment, upload the project to a new GitHub repository.

2.  **Set up the environment variable.**
    * Create a file named `.env` in the root of the project directory.
    * Add your Gemini API key to this file:
        ```
        GEMINI_API_KEY="your-secret-api-key-here"
        ```

3.  **Create a virtual environment and install dependencies.**
    ```bash
    # Create the environment
    python3 -m venv .venv
    
    # Activate the environment
    # On macOS/Linux:
    source .venv/bin/activate
    # On Windows:
    # .\.venv\Scripts\activate
    
    # Install required packages
    pip install streamlit google-generativeai python-dotenv
    ```

4.  **Run the application.**
    * The project is configured to run on port 8000.
    ```bash
    streamlit run app.py
    ```

5.  **Access the application.**
    * Open your browser and navigate to `http://127.0.0.1:8000` or the URL provided by your cloud environment.

---

## 💡 Challenges & Solutions

During development, a significant challenge arose where the application failed to run on a local Windows machine, throwing persistent `ImportError` and permission errors despite the environment being correctly configured.

* **Challenge**: The local development environment was fundamentally broken, preventing the Streamlit server from correctly recognizing its own installed packages. This is a common but difficult issue related to system PATHs, conflicting Python installations, and security software interference.
* **Solution**: To overcome this, the project was moved to **GitHub Codespaces**. This provided a clean, standardized, and containerized Linux environment that completely bypassed the local machine's issues. This approach not only solved the problem but also improved development efficiency and ensured reproducibility, demonstrating a practical solution to common environment-related development obstacles.

---

## 📖 Usage Guide

1.  **Start Interview**: Launch the application and click the "Start Interview Process" button.
2.  **Provide Information**: Follow the chatbot's prompts to provide your personal details, professional background, and technical skills.
3.  **Answer Technical Questions**: Respond to the 3-5 technical questions generated by the AI based on your tech stack.
4.  **Complete Session**: Once all questions are answered, the conversation will conclude, and a summary of your interview will be displayed.
