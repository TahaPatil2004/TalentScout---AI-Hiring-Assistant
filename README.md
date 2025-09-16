# TalentScout - AI Hiring Assistant

An intelligent Streamlit-based chatbot that streamlines the initial candidate screening process for TalentScout, a technology recruitment agency. The assistant uses Google Gemini AI to conduct structured interviews and generate tailored technical questions based on candidates' tech stacks.

## 🎯 Features

### Core Functionality
- **Interactive Chat Interface**: Clean, professional Streamlit UI for seamless candidate interaction
- **Systematic Information Gathering**: Collects essential candidate details including:
  - Full Name
  - Email Address  
  - Phone Number
  - Years of Experience
  - Desired Position(s)
  - Current Location
  - Tech Stack & Skills

### AI-Powered Capabilities
- **Intelligent Conversation Flow**: Context-aware responses using Google Gemini AI
- **Dynamic Question Generation**: Creates 3-5 tailored technical questions based on declared tech stack
- **Smart Data Extraction**: AI-powered parsing of candidate responses
- **Fallback Handling**: Graceful handling of unexpected inputs while maintaining focus

### Technical Features
- **Data Validation**: Robust email and phone number validation with multiple format support
- **Session Management**: Maintains conversation state and candidate data throughout the session
- **Privacy Compliance**: Secure handling of sensitive information following data privacy best practices
- **Professional UI**: Clean, responsive design with conversation history and progress tracking

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- Google Gemini API key

### Local Setup

1. **Clone or download the project files**
   ```bash
   # Ensure you have all project files in your working directory
   ```

2. **Set up environment variables**
   ```bash
   # Set your Gemini API key
   export GEMINI_API_KEY="your_gemini_api_key_here"
   
   # On Windows:
   set GEMINI_API_KEY=your_gemini_api_key_here
   ```

3. **Install dependencies**
   ```bash
   pip install streamlit google-genai
   ```

4. **Run the application**
   ```bash
   streamlit run app.py --server.port 5000
   ```

5. **Access the application**
   - Open your browser and navigate to `http://localhost:5000`
   - The application will be ready for candidate interactions

## 📖 Usage Guide

### For Candidates
1. **Start Interview**: Click "Start Interview Process" to begin
2. **Provide Information**: Follow the prompts to share your details:
   - Personal information (name, email, phone)
   - Professional background (experience, desired roles, location)
   - Technical expertise (programming languages, frameworks, tools)
3. **Answer Questions**: Respond to AI-generated technical questions
4. **Complete Session**: Review your summary and next steps

### For Recruiters
- **Monitor Sessions**: View real-time candidate responses and progress
- **Review Data**: Access comprehensive candidate summaries post-interview
- **Next Steps**: Follow up with qualified candidates based on collected information

## 🔧 Technical Architecture

### Core Components

**app.py** - Main Streamlit application
- User interface and session management
- Conversation flow control
- Real-time chat display

**hiring_assistant.py** - AI-powered conversation engine
- Google Gemini AI integration
- Conversation state management
- Technical question generation
- Context-aware response processing

**data_validator.py** - Input validation and sanitization
- Email/phone format validation
- Experience extraction
- Data security and sanitization

### AI Integration
- **Model**: Google Gemini 2.5 Flash for optimal performance
- **Question Generation**: Context-aware technical questions based on tech stack
- **Data Extraction**: AI-powered parsing of natural language responses
- **Conversation Management**: Maintains context throughout multi-stage interviews

### Data Handling
- **Session State**: Streamlit session state for conversation persistence
- **Data Privacy**: No persistent storage, memory-only processing
- **Validation**: Multi-layer input validation and sanitization
- **Security**: XSS prevention and input sanitization

## 🎨 Prompt Engineering

### Core Prompts

**Greeting & Context Setting**
