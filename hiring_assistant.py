import os
import json
import re
from typing import Dict, List, Optional, Any
from enum import Enum
import logging
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

try:
    import google.generativeai as genai
    from google.generativeai import types
except ImportError:
    print("Warning: Google GenAI not found. Please install google-genai")
    genai = None
    types = None

from data_validator import DataValidator

# Configure logging
logger = logging.getLogger(__name__)

# Configure the Gemini API client
if genai:
    try:
        genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
    except Exception as e:
        logger.error(f"Failed to configure Gemini API: {e}")
        genai = None

class ConversationStage(Enum):
    """Enumeration for conversation stages."""
    GREETING = "greeting"
    COLLECT_NAME = "collect_name"
    COLLECT_EMAIL = "collect_email"
    COLLECT_PHONE = "collect_phone"
    COLLECT_EXPERIENCE = "collect_experience"
    COLLECT_POSITION = "collect_position"
    COLLECT_LOCATION = "collect_location"
    COLLECT_TECH_STACK = "collect_tech_stack"
    GENERATE_QUESTIONS = "generate_questions"
    ASK_QUESTIONS = "ask_questions"
    COMPLETE = "complete"

class HiringAssistant:
    """Intelligent hiring assistant chatbot for TalentScout."""

    def __init__(self):
        """Initialize the hiring assistant."""
        self.validator = DataValidator()

        # Conversation state
        self.current_stage = ConversationStage.GREETING
        self.candidate_data = {}
        self.technical_questions = []
        self.current_question_index = 0
        self.current_message = ""
        self.conversation_complete = False

        # Conversation context for AI
        self.conversation_context = []

        # Advanced features
        self.sentiment_history = []
        self.detected_language = 'en'  # Default to English
        self.response_times = []
        self.start_time = time.time()

    def _call_gemini(self, prompt: str, system_prompt: Optional[str] = None, temperature: float = 0.5) -> Optional[str]:
        """Generic function to call the Gemini API and handle errors."""
        if not genai:
            logger.error("Gemini AI library is not available.")
            return None
        try:
            model = genai.GenerativeModel(
                model_name='gemini-1.5-flash',
                system_instruction=system_prompt
            )
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=1000
                )
            )
            return response.text.strip()
        except Exception as e:
            logger.error(f"Error calling Gemini AI: {e}")
            return None

    def start_conversation(self) -> None:
        """Start the conversation flow."""
        self.current_stage = ConversationStage.GREETING
        self.current_message = self._get_greeting_message()
        self.conversation_context.append({"role": "assistant", "content": self.current_message})

    def get_current_message(self) -> str:
        """Get the current message to display."""
        return self.current_message

    def is_conversation_complete(self) -> bool:
        """Check if conversation is complete."""
        return self.conversation_complete

    def get_candidate_summary(self) -> Dict[str, Any]:
        """Get summary of collected candidate information."""
        return self.candidate_data.copy()

    def process_user_input(self, user_input: str) -> None:
        """Process user input and advance conversation."""
        if not user_input.strip():
            return
        
        start_time = time.time()
        self._analyze_user_input(user_input)
        self.conversation_context.append({"role": "user", "content": user_input})

        if self._is_ending_keyword(user_input):
            self.end_conversation()
            return

        try:
            # Using a more explicit and stable if/elif structure for conversation flow
            if self.current_stage == ConversationStage.GREETING:
                self._process_greeting_response(user_input)
            elif self.current_stage == ConversationStage.COLLECT_NAME:
                self._process_name_collection(user_input)
            elif self.current_stage == ConversationStage.COLLECT_EMAIL:
                self._process_email_collection(user_input)
            elif self.current_stage == ConversationStage.COLLECT_PHONE:
                self._process_phone_collection(user_input)
            elif self.current_stage == ConversationStage.COLLECT_EXPERIENCE:
                self._process_experience_collection(user_input)
            elif self.current_stage == ConversationStage.COLLECT_POSITION:
                self._process_position_collection(user_input)
            elif self.current_stage == ConversationStage.COLLECT_LOCATION:
                self._process_location_collection(user_input)
            elif self.current_stage == ConversationStage.COLLECT_TECH_STACK:
                self._process_tech_stack_collection(user_input)
            elif self.current_stage == ConversationStage.ASK_QUESTIONS:
                self._process_technical_question_response(user_input)
            else:
                self._handle_fallback(user_input)
                
        except Exception as e:
            logger.error(f"Error processing user input: {e}")
            self._handle_error()
        
        response_time = time.time() - start_time
        self.response_times.append(response_time)
        logger.info(f"Response processed in {response_time:.2f} seconds")

    def end_conversation(self) -> None:
        """End the conversation gracefully."""
        self.current_message = self._get_ending_message()
        self.conversation_complete = True
        self.conversation_context.append({"role": "assistant", "content": self.current_message})

    def _get_greeting_message(self) -> str:
        return """Hello! 👋 Welcome to TalentScout's AI-powered hiring assistant. I'm here to streamline your interview process by gathering essential information. This will take about 10-15 minutes. Let's get started! Could you please tell me your full name?"""

    def _process_greeting_response(self, user_input: str):
        self._process_name_collection(user_input)
        
    def _process_name_collection(self, user_input: str) -> None:
        name = self._extract_name_with_ai(user_input)
        if name:
            self.candidate_data['full_name'] = name
            self.current_stage = ConversationStage.COLLECT_EMAIL
            self.current_message = f"Nice to meet you, {name}! 😊 Please provide your email address."
        else:
            self.current_message = "I'd like to make sure I have your name correctly. Could you please provide your full name?"

    def _process_email_collection(self, user_input: str) -> None:
        email = self.validator.extract_email(user_input)
        if email:
            self.candidate_data['email'] = email
            self.current_stage = ConversationStage.COLLECT_PHONE
            self.current_message = "Great! Now, what is your contact phone number?"
        else:
            self.current_message = "Please provide a valid email address (e.g., name@example.com)."

    def _process_phone_collection(self, user_input: str) -> None:
        phone = self.validator.extract_phone(user_input)
        if phone:
            self.candidate_data['phone'] = phone
            self.current_stage = ConversationStage.COLLECT_EXPERIENCE
            self.current_message = "Perfect! How many years of professional experience do you have?"
        else:
            self.current_message = "Please provide a valid phone number."

    def _process_experience_collection(self, user_input: str) -> None:
        experience = self.validator.extract_experience(user_input)
        if experience is not None:
            self.candidate_data['years_experience'] = experience
            self.current_stage = ConversationStage.COLLECT_POSITION
            self.current_message = "Excellent! What position(s) are you interested in?"
        else:
            self.current_message = "Please provide your years of experience as a number (e.g., 2, 3.5)."

    def _process_position_collection(self, user_input: str) -> None:
        """Process position collection."""
        if user_input.strip() and not self._is_irrelevant_response(user_input):
            self.candidate_data['desired_positions'] = user_input.strip()
            self.current_stage = ConversationStage.COLLECT_LOCATION
            self.current_message = "Great choice! What's your current location? (City, Country)"
        else:
            self.current_message = "Please tell me what position(s) you're interested in. An answer like 'nothing' is not a valid role."

    def _process_location_collection(self, user_input: str) -> None:
        """Process location collection."""
        if user_input.strip() and not self._is_irrelevant_response(user_input):
            self.candidate_data['location'] = user_input.strip()
            self.current_stage = ConversationStage.COLLECT_TECH_STACK
            self.current_message = """Perfect! Now for the technical part. 🔧 Please list your tech stack: programming languages, frameworks, databases, and any other relevant tools."""
        else:
            self.current_message = "Please provide a valid location (e.g., 'Pune, India' or 'San Francisco, CA')."

    def _process_tech_stack_collection(self, user_input: str) -> None:
        if user_input.strip() and not self._is_irrelevant_response(user_input):
            self.candidate_data['tech_stack'] = user_input.strip()
            self.current_stage = ConversationStage.GENERATE_QUESTIONS
            self.technical_questions = self._generate_technical_questions(user_input)
            if self.technical_questions:
                self.current_question_index = 0
                self.current_stage = ConversationStage.ASK_QUESTIONS
                self.current_message = f"Excellent! I've prepared {len(self.technical_questions)} questions. Let's begin:\n\n**Question 1/{len(self.technical_questions)}:**\n{self.technical_questions[0]}"
            else:
                self.current_message = "Thank you. I seem to be having trouble generating questions right now."
                self.end_conversation()
        else:
            self.current_message = "Please describe your technical skills and expertise."

    def _process_technical_question_response(self, user_input: str) -> None:
        if user_input.strip():
            self.candidate_data[f"question_{self.current_question_index + 1}_answer"] = user_input.strip()
            self.current_question_index += 1
            if self.current_question_index < len(self.technical_questions):
                self.current_message = f"Thank you. **Question {self.current_question_index + 1}/{len(self.technical_questions)}:**\n{self.technical_questions[self.current_question_index]}"
            else:
                self.end_conversation()
        else:
            self.current_message = "Please provide an answer to the question."

    def _generate_technical_questions(self, tech_stack: str) -> List[str]:
        system_prompt = "You are an expert technical interviewer. Generate 5 relevant, practical questions based on the candidate's tech stack. Return only the questions, numbered 1-5, one per line."
        user_prompt = f"Tech Stack: {tech_stack}\nExperience: {self.candidate_data.get('years_experience', 'Not specified')} years"
        response_text = self._call_gemini(user_prompt, system_prompt, temperature=0.7)
        if response_text:
            questions = [re.sub(r'^\d+\.?\s*', '', line).strip() for line in response_text.strip().split('\n') if line.strip()]
            return questions[:5]
        return self._get_fallback_questions()

    def _get_fallback_questions(self) -> List[str]:
        return ["Describe a challenging project you've worked on.", "How do you approach debugging?", "How do you stay updated with new technologies?"]

    def _extract_name_with_ai(self, user_input: str) -> Optional[str]:
        system_prompt = "Extract the full name (first and last name) from the user's response. Return only the cleaned full name, or 'NONE' if no valid full name can be identified."
        response_text = self._call_gemini(f"Extract the full name from: {user_input}", system_prompt, temperature=0.1)
        if response_text and 'NONE' not in response_text.upper() and len(response_text.split()) >= 2:
            return response_text
        return ' '.join(user_input.strip().split()[:2]) if len(user_input.strip().split()) >=2 else None

    def _is_ending_keyword(self, user_input: str) -> bool:
        return any(keyword in user_input.lower() for keyword in ['bye', 'exit', 'quit', 'end', 'stop'])

    def _is_irrelevant_response(self, user_input: str) -> bool:
        """Checks for common irrelevant or non-answers."""
        irrelevant_keywords = [
            'nothing', 'none', 'n/a', 'na', 'idk', 'i don\'t know',
            'no', 'space', 'asdf', 'no idea', 'whatever'
        ]
        # Check if the user's entire response is one of the keywords
        return user_input.lower().strip() in irrelevant_keywords

    def _handle_fallback(self, user_input: str) -> None:
        import random
        self.current_message = random.choice(["I didn't quite understand. Could you rephrase?", "Let's stay focused. Please answer the current question."])

    def _handle_error(self) -> None:
        self.current_message = "I apologize, but I encountered an issue. Please try again, or type 'end' to quit."

    def _analyze_user_input(self, user_input: str) -> None:
        sentiment_prompt = "Analyze the sentiment of this response. Return one word: POSITIVE, NEUTRAL, or NEGATIVE."
        sentiment = self._call_gemini(f"Response: \"{user_input}\"", sentiment_prompt, temperature=0.1)
        if sentiment:
            self.sentiment_history.append({'sentiment': sentiment.upper()})
            logger.info(f"Detected sentiment: {sentiment.upper()}")

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics for optimization."""
        return {
            'total_session_time': time.time() - self.start_time,
            'average_response_time': sum(self.response_times) / len(self.response_times) if self.response_times else 0,
            'sentiment_distribution': self._get_sentiment_distribution(),
            'detected_language': self.detected_language
        }

    def _get_sentiment_distribution(self) -> Dict[str, int]:
        distribution = {}
        for entry in self.sentiment_history:
            sentiment = entry['sentiment']
            distribution[sentiment] = distribution.get(sentiment, 0) + 1
        return distribution

    def _get_ending_message(self) -> str:
        name = self.candidate_data.get('full_name', 'there')
        return f"""Thank you, {name}! 🎉 I've collected all the necessary information. Our recruitment team will review your profile and contact you within 2-3 business days if there's a good match. Best of luck with your job search! 🚀"""
