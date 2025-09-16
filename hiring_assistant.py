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
    from google import genai
    from google.genai import types
except ImportError:
    print("Warning: Google GenAI not found. Please install google-genai")
    genai = None
    types = None

from data_validator import DataValidator

# Configure logging
logger = logging.getLogger(__name__)

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
        if genai:
            self.client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
        else:
            self.client = None
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
        self.candidate_personality_traits = {}
        self.response_times = []
        self.start_time = time.time()
        
    def start_conversation(self) -> None:
        """Start the conversation flow."""
        self.current_stage = ConversationStage.GREETING
        self.current_message = self._get_greeting_message()
        self.conversation_context.append({
            "role": "assistant",
            "content": self.current_message
        })
        
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
        
        # Detect language and sentiment (advanced features)
        self._analyze_user_input(user_input)
            
        # Add user input to context
        self.conversation_context.append({
            "role": "user", 
            "content": user_input
        })
        
        # Check for conversation ending keywords
        if self._is_ending_keyword(user_input):
            self.end_conversation()
            return
        
        # Process based on current stage
        try:
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
        
        # Record response time for performance tracking
        response_time = time.time() - start_time
        self.response_times.append(response_time)
        logger.info(f"Response processed in {response_time:.2f} seconds")
    
    def end_conversation(self) -> None:
        """End the conversation gracefully."""
        self.current_message = self._get_ending_message()
        self.conversation_complete = True
        self.conversation_context.append({
            "role": "assistant",
            "content": self.current_message
        })
    
    def _get_greeting_message(self) -> str:
        """Get the initial greeting message."""
        return """Hello! 👋 Welcome to TalentScout's AI-powered hiring assistant. 

I'm here to help streamline your interview process by gathering some essential information about your background and technical expertise. This will take about 10-15 minutes.

Here's what we'll cover:
• Basic contact information
• Your experience and career goals  
• Technical skills and expertise
• A few technical questions tailored to your background

Let's get started! Could you please tell me your full name?"""
    
    def _process_greeting_response(self, user_input: str) -> None:
        """Process response after greeting."""
        # Extract name from the response
        name = self._extract_name_with_ai(user_input)
        if name:
            self.candidate_data['full_name'] = name
            self.current_stage = ConversationStage.COLLECT_EMAIL
            base_message = f"Nice to meet you, {name}! 😊\n\nNext, I'll need your email address for our records. Please provide your email:"
            self.current_message = self._get_multilingual_response(self._get_personalized_response(base_message))
        else:
            self.current_stage = ConversationStage.COLLECT_NAME
            base_message = "I'd like to make sure I have your name correctly. Could you please provide your full name (first and last name)?"
            self.current_message = self._get_multilingual_response(base_message)
    
    def _process_name_collection(self, user_input: str) -> None:
        """Process name collection."""
        name = self._extract_name_with_ai(user_input)
        if name:
            self.candidate_data['full_name'] = name
            self.current_stage = ConversationStage.COLLECT_EMAIL
            base_message = f"Thank you, {name}! Now, please provide your email address:"
            self.current_message = self._get_multilingual_response(self._get_personalized_response(base_message))
        else:
            base_message = "I need your full name to proceed. Please provide your first and last name:"
            self.current_message = self._get_multilingual_response(base_message)
    
    def _process_email_collection(self, user_input: str) -> None:
        """Process email collection."""
        email = self.validator.extract_email(user_input)
        if email:
            self.candidate_data['email'] = email
            self.current_stage = ConversationStage.COLLECT_PHONE
            self.current_message = "Great! Now I need your phone number. Please provide your contact number:"
        else:
            self.current_message = "Please provide a valid email address (e.g., john.doe@example.com):"
    
    def _process_phone_collection(self, user_input: str) -> None:
        """Process phone collection."""
        phone = self.validator.extract_phone(user_input)
        if phone:
            self.candidate_data['phone'] = phone
            self.current_stage = ConversationStage.COLLECT_EXPERIENCE
            self.current_message = "Perfect! How many years of professional experience do you have? (Please provide a number, e.g., 3, 5.5, etc.)"
        else:
            self.current_message = "Please provide a valid phone number (e.g., +1-555-123-4567, (555) 123-4567, etc.):"
    
    def _process_experience_collection(self, user_input: str) -> None:
        """Process experience collection."""
        experience = self.validator.extract_experience(user_input)
        if experience is not None:
            self.candidate_data['years_experience'] = experience
            self.current_stage = ConversationStage.COLLECT_POSITION
            base_message = "Excellent! What position(s) are you interested in? (You can mention multiple roles if applicable)"
            self.current_message = self._get_multilingual_response(self._get_personalized_response(base_message))
        else:
            base_message = "Please provide your years of experience as a number (e.g., 2, 3.5, 0 for fresh graduate):"
            self.current_message = self._get_multilingual_response(base_message)
    
    def _process_position_collection(self, user_input: str) -> None:
        """Process position collection."""
        if user_input.strip():
            self.candidate_data['desired_positions'] = user_input.strip()
            self.current_stage = ConversationStage.COLLECT_LOCATION
            self.current_message = "Great choice! What's your current location? (City, State/Country)"
        else:
            self.current_message = "Please tell me what position(s) you're interested in:"
    
    def _process_location_collection(self, user_input: str) -> None:
        """Process location collection."""
        if user_input.strip():
            self.candidate_data['location'] = user_input.strip()
            self.current_stage = ConversationStage.COLLECT_TECH_STACK
            self.current_message = """Perfect! Now for the technical part. 🔧

Please tell me about your tech stack and areas of expertise. Include:
• Programming languages (e.g., Python, JavaScript, Java)
• Frameworks (e.g., React, Django, Spring)
• Databases (e.g., MySQL, MongoDB, PostgreSQL)  
• Tools and technologies (e.g., Docker, AWS, Git)
• Any other relevant technical skills

Feel free to be comprehensive - this helps me ask you the most relevant questions!"""
        else:
            self.current_message = "Please provide your current location:"
    
    def _process_tech_stack_collection(self, user_input: str) -> None:
        """Process tech stack collection and generate questions."""
        if user_input.strip():
            self.candidate_data['tech_stack'] = user_input.strip()
            self.current_stage = ConversationStage.GENERATE_QUESTIONS
            
            # Generate technical questions
            try:
                self.technical_questions = self._generate_technical_questions(user_input)
                self.current_question_index = 0
                self.current_stage = ConversationStage.ASK_QUESTIONS
                
                if self.technical_questions:
                    base_message = f"""Excellent! Based on your tech stack, I've prepared {len(self.technical_questions)} technical questions for you. 

Let's begin:

**Question 1/{len(self.technical_questions)}:**
{self.technical_questions[0]}

Please provide your answer:"""
                    self.current_message = self._get_multilingual_response(self._get_personalized_response(base_message))
                else:
                    base_message = "Thank you for sharing your tech stack! Let me prepare some questions for you..."
                    self.current_message = self._get_multilingual_response(base_message)
                    self.end_conversation()
                    
            except Exception as e:
                logger.error(f"Error generating questions: {e}")
                self.current_message = "I'm having trouble generating technical questions right now. Let me wrap up our session..."
                self.end_conversation()
        else:
            self.current_message = "Please describe your technical skills and expertise:"
    
    def _process_technical_question_response(self, user_input: str) -> None:
        """Process technical question responses."""
        if user_input.strip():
            # Store the answer
            question_key = f"question_{self.current_question_index + 1}_answer"
            self.candidate_data[question_key] = user_input.strip()
            
            # Move to next question
            self.current_question_index += 1
            
            if self.current_question_index < len(self.technical_questions):
                self.current_message = f"""Thank you for your answer! 

**Question {self.current_question_index + 1}/{len(self.technical_questions)}:**
{self.technical_questions[self.current_question_index]}

Please provide your answer:"""
            else:
                # All questions completed
                self.end_conversation()
        else:
            self.current_message = "Please provide an answer to the question:"
    
    def _generate_technical_questions(self, tech_stack: str) -> List[str]:
        """Generate technical questions based on tech stack using Gemini AI."""
        try:
            system_prompt = """You are an expert technical interviewer for a recruitment agency called TalentScout. 
Your task is to generate 3-5 relevant technical questions based on the candidate's declared tech stack.

Requirements:
- Generate exactly 5 questions that assess practical knowledge and problem-solving skills
- Questions should be appropriate for the technologies mentioned
- Include a mix of conceptual and practical questions
- Avoid overly basic or overly advanced questions unless the experience level suggests it
- Make questions clear and specific
- Focus on real-world scenarios when possible
- Cover different aspects: coding skills, architecture, debugging, best practices, and experience

Return only the questions, numbered 1-5, one per line. Do not include any other text or explanations."""

            user_prompt = f"""Based on this tech stack, generate exactly 5 appropriate technical interview questions:

Tech Stack: {tech_stack}

Candidate Experience: {self.candidate_data.get('years_experience', 'Not specified')} years

Generate technical questions that would help assess this candidate's proficiency in their declared technologies."""

            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    types.Content(role="user", parts=[types.Part(text=user_prompt)])
                ],
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=0.7,
                    max_output_tokens=1000
                )
            )
            
            if response.text:
                # Parse questions from response
                questions = []
                lines = response.text.strip().split('\n')
                
                for line in lines:
                    line = line.strip()
                    if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                        # Remove numbering and clean up
                        question = re.sub(r'^\d+\.?\s*', '', line)
                        question = re.sub(r'^[-•]\s*', '', question)
                        if question:
                            questions.append(question.strip())
                
                return questions[:5]  # Limit to 5 questions max
            
        except Exception as e:
            logger.error(f"Error generating technical questions: {e}")
            
        # Fallback questions if AI generation fails
        return self._get_fallback_questions(tech_stack)
    
    def _get_fallback_questions(self, tech_stack: str) -> List[str]:
        """Generate fallback questions when AI generation fails."""
        fallback_questions = [
            f"Can you describe a challenging project you've worked on using the technologies you mentioned: {tech_stack[:100]}...?",
            "What's your approach to debugging and troubleshooting issues in your code?",
            "How do you stay updated with the latest developments in your tech stack?",
            "Can you walk me through your development workflow from idea to deployment?",
            "What's one technology from your stack that you'd like to improve your skills in, and why?",
            "How do you handle version control and collaboration in your development projects?",
            "What's your experience with testing and quality assurance in your code?"
        ]
        return fallback_questions[:5]  # Return 5 fallback questions
    
    def _extract_name_with_ai(self, user_input: str) -> Optional[str]:
        """Extract full name from user input using AI."""
        try:
            system_prompt = """Extract the full name (first and last name) from the user's response. 
Return only the cleaned full name, or return 'NONE' if no valid full name can be identified.
The name should contain at least a first and last name.
Remove any titles, extra words, or formatting."""

            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    types.Content(role="user", parts=[types.Part(text=f"Extract the full name from: {user_input}")])
                ],
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=0.1,
                    max_output_tokens=50
                )
            )
            
            if response.text:
                extracted_name = response.text.strip()
                if extracted_name.upper() != 'NONE' and len(extracted_name.split()) >= 2:
                    return extracted_name
                    
        except Exception as e:
            logger.error(f"Error extracting name with AI: {e}")
        
        # Fallback to simple extraction
        words = user_input.strip().split()
        if len(words) >= 2:
            # Take first two words as first and last name
            return f"{words[0]} {words[1]}"
        
        return None
    
    def _is_ending_keyword(self, user_input: str) -> bool:
        """Check if user input contains conversation ending keywords."""
        ending_keywords = [
            'bye', 'goodbye', 'exit', 'quit', 'end', 'stop', 'finish',
            'done', 'cancel', 'terminate', 'close', 'leave'
        ]
        return any(keyword in user_input.lower() for keyword in ending_keywords)
    
    def _is_relevant_answer(self, user_input: str, expected_type: str) -> bool:
        """Check if user input is relevant to the expected question type."""
        user_input_lower = user_input.lower().strip()
        
        # Basic relevance checks
        if len(user_input_lower) < 2:
            return False
            
        # Type-specific validation
        if expected_type == "email":
            return "@" in user_input or "email" in user_input_lower or "mail" in user_input_lower
        elif expected_type == "phone":
            return any(char.isdigit() for char in user_input) or "phone" in user_input_lower or "number" in user_input_lower
        elif expected_type == "tech_stack":
            tech_keywords = ["python", "java", "javascript", "react", "node", "sql", "html", "css", "framework", "language", "programming", "coding", "development", "software", "web", "mobile", "database", "backend", "frontend"]
            return any(keyword in user_input_lower for keyword in tech_keywords) or len(user_input.split()) >= 3
        
        return True  # Default to accepting if uncertain
    
    def _handle_fallback(self, user_input: str) -> None:
        """Handle unexpected inputs with fallback responses."""
        fallback_responses = [
            "I didn't quite understand that. Could you please rephrase your response?",
            "I'm here to help with your interview process. Could you please provide the information I requested?",
            "Let's stay focused on gathering your information. Could you please answer the current question?",
            "I need to collect some specific information from you. Please respond to the current question."
        ]
        
        import random
        self.current_message = random.choice(fallback_responses)
    
    def _handle_error(self) -> None:
        """Handle errors gracefully."""
        self.current_message = """I apologize, but I encountered an issue processing your response. 

Please try again, or if you'd like to end the session, just type 'end' or 'quit'."""
    
    def _analyze_user_input(self, user_input: str) -> None:
        """Analyze user input for sentiment and language (advanced feature)."""
        try:
            if not self.client or not genai or not types:
                return
            
            # Improved language detection - run on every early response
            if len(self.conversation_context) <= 6:  # More opportunities to detect language
                lang_prompt = f"""Identify the language of this text. Common languages:
- English: en
- Hindi: hi  
- Spanish: es
- French: fr
- German: de
- Chinese: zh
- Japanese: ja
- Korean: ko
- Arabic: ar
- Portuguese: pt
- Russian: ru
- Italian: it

Text: "{user_input}"

Return ONLY the 2-letter language code (hi for Hindi, en for English, etc.)"""
                
                try:
                    lang_response = self.client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=[types.Content(role="user", parts=[types.Part(text=lang_prompt)])],
                        config=types.GenerateContentConfig(
                            temperature=0.0,  # More deterministic
                            max_output_tokens=5
                        )
                    )
                    
                    if lang_response.text:
                        detected_lang = lang_response.text.strip().lower()
                        if detected_lang != 'en' and len(detected_lang) == 2:
                            self.detected_language = detected_lang
                            logger.info(f"Detected language: {detected_lang}")
                except Exception as e:
                    logger.error(f"Language detection error: {e}")
                
            # Sentiment analysis
            sentiment_prompt = f"""Analyze the emotional tone and sentiment of this candidate response during a job interview. 
            
            Response: "{user_input}"
            
            Return only one word: POSITIVE, NEUTRAL, NEGATIVE, NERVOUS, CONFIDENT, or ENTHUSIASTIC."""
            
            try:
                sentiment_response = self.client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=[types.Content(role="user", parts=[types.Part(text=sentiment_prompt)])],
                    config=types.GenerateContentConfig(
                        temperature=0.1,
                        max_output_tokens=10
                    )
                )
                
                if sentiment_response.text:
                    sentiment = sentiment_response.text.strip().upper()
                    self.sentiment_history.append({
                        'text': user_input,
                        'sentiment': sentiment,
                        'timestamp': datetime.now()
                    })
                    logger.info(f"Detected sentiment: {sentiment}")
            except Exception as e:
                logger.error(f"Sentiment analysis error: {e}")
                        
        except Exception as e:
            logger.error(f"Error in sentiment/language analysis: {e}")
    
    def _get_personalized_response(self, base_message: str) -> str:
        """Generate personalized response based on sentiment and conversation history."""
        try:
            if not self.sentiment_history or not self.client:
                return base_message
                
            recent_sentiments = [s['sentiment'] for s in self.sentiment_history[-3:]]
            dominant_sentiment = max(set(recent_sentiments), key=recent_sentiments.count) if recent_sentiments else 'NEUTRAL'
            
            # Adjust response tone based on detected sentiment
            if dominant_sentiment in ['NERVOUS', 'NEGATIVE']:
                personalization_prompt = f"""Make this interview response more encouraging and supportive while maintaining professionalism. 
                The candidate seems nervous or hesitant based on their recent responses.
                
                Original: "{base_message}"
                
                Return an encouraging version that builds confidence."""
            elif dominant_sentiment in ['CONFIDENT', 'ENTHUSIASTIC', 'POSITIVE']:
                personalization_prompt = f"""Make this interview response match the candidate's positive energy while remaining professional.
                
                Original: "{base_message}"
                
                Return a version that matches their enthusiasm."""
            else:
                return base_message
                
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[types.Content(role="user", parts=[types.Part(text=personalization_prompt)])],
                config=types.GenerateContentConfig(
                    temperature=0.7,
                    max_output_tokens=500
                )
            )
            
            if response.text:
                return response.text.strip()
                
        except Exception as e:
            logger.error(f"Error in personalization: {e}")
            
        return base_message
    
    def _get_multilingual_response(self, message: str) -> str:
        """Translate response if non-English language detected."""
        try:
            if self.detected_language == 'en' or not self.client:
                return message
                
            language_names = {
                'es': 'Spanish', 'fr': 'French', 'de': 'German', 
                'zh': 'Chinese', 'hi': 'Hindi', 'ja': 'Japanese',
                'pt': 'Portuguese', 'ru': 'Russian', 'it': 'Italian',
                'ar': 'Arabic', 'ko': 'Korean'
            }
            
            lang_name = language_names.get(self.detected_language, 'the candidate\'s language')
            
            translation_prompt = f"""Translate this professional recruitment message to {lang_name}. 
            Maintain the same professional tone and structure:
            
            "{message}"
            
            Return only the translation."""
            
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[types.Content(role="user", parts=[types.Part(text=translation_prompt)])],
                config=types.GenerateContentConfig(
                    temperature=0.3,
                    max_output_tokens=1000
                )
            )
            
            if response.text:
                return response.text.strip()
                
        except Exception as e:
            logger.error(f"Error in translation: {e}")
            
        return message
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics for optimization."""
        total_time = time.time() - self.start_time
        avg_response_time = sum(self.response_times) / len(self.response_times) if self.response_times else 0
        
        return {
            'total_session_time': total_time,
            'average_response_time': avg_response_time,
            'total_responses': len(self.response_times),
            'sentiment_distribution': self._get_sentiment_distribution(),
            'detected_language': self.detected_language
        }
    
    def _get_sentiment_distribution(self) -> Dict[str, int]:
        """Get distribution of sentiments throughout conversation."""
        distribution = {}
        for entry in self.sentiment_history:
            sentiment = entry['sentiment']
            distribution[sentiment] = distribution.get(sentiment, 0) + 1
        return distribution
    
    def _get_ending_message(self) -> str:
        """Get the conversation ending message."""
        name = self.candidate_data.get('full_name', 'there')
        
        base_message = f"""Thank you, {name}! 🎉 

I've successfully collected all the necessary information for your initial screening. Here's what happens next:

🔍 **Next Steps:**
• Our recruitment team will review your profile and responses
• If there's a good match, we'll contact you within 2-3 business days
• We may schedule a more detailed technical interview or connect you directly with potential employers

📧 **Contact:** We have your email ({self.candidate_data.get('email', 'on file')}) and will reach out there.

💼 **TalentScout Promise:** We're committed to finding you the right opportunity that matches your skills and career goals.

Thank you for choosing TalentScout, and best of luck with your job search! 🚀

---
*This conversation has been securely recorded for recruitment purposes only.*"""
        
        # Apply personalization and multilingual support
        personalized = self._get_personalized_response(base_message)
        return self._get_multilingual_response(personalized)
