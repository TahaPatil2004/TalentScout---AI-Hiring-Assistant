import streamlit as st
from hiring_assistant import HiringAssistant
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Main Streamlit application entry point."""
    
    # Set page configuration
    st.set_page_config(
        page_title="TalentScout - Hiring Assistant",
        page_icon="🎯",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Enhanced CSS for professional styling
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        font-family: 'Inter', sans-serif;
    }
    
    .main-header {
        text-align: center;
        color: #ffffff;
        margin-bottom: 30px;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        font-weight: 700;
        font-size: 2.5rem;
    }
    
    .chat-container {
        max-width: 900px;
        margin: 0 auto;
        background: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        padding: 30px;
        box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        backdrop-filter: blur(10px);
    }
    
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px 20px;
        border-radius: 20px 20px 5px 20px;
        margin: 15px 0;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        border: none;
        font-weight: 500;
    }
    
    .assistant-message {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 15px 20px;
        border-radius: 20px 20px 20px 5px;
        margin: 15px 0;
        box-shadow: 0 4px 15px rgba(240, 147, 251, 0.3);
        border: none;
        font-weight: 500;
    }
    
    .info-box {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        border: none;
        border-radius: 15px;
        padding: 25px;
        margin: 20px 0;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        color: #333;
    }
    
    .info-box h3 {
        color: #2d3748;
        font-weight: 600;
        margin-bottom: 15px;
    }
    
    .footer {
        text-align: center;
        margin-top: 50px;
        padding: 30px;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        color: #ffffff;
        backdrop-filter: blur(5px);
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border: none;
        border-radius: 25px;
        color: white;
        font-weight: 600;
        padding: 12px 24px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6);
    }
    
    .stTextInput > div > div > input {
        border-radius: 25px;
        border: 2px solid #e2e8f0;
        padding: 12px 20px;
        font-size: 16px;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    .stExpander {
        border: none;
        border-radius: 15px;
        background: rgba(255, 255, 255, 0.9);
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .chat-message {
        animation: slideIn 0.3s ease-out;
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    div[data-testid="stSidebar"] {
        display: none;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown('<h1 class="main-header">🎯 TalentScout Hiring Assistant</h1>', unsafe_allow_html=True)
    
    # Initialize session state
    if 'hiring_assistant' not in st.session_state:
        st.session_state.hiring_assistant = HiringAssistant()
    
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    
    if 'conversation_started' not in st.session_state:
        st.session_state.conversation_started = False
    
    # Main container
    with st.container():
        col1, col2, col3 = st.columns([1, 3, 1])
        
        with col2:
            st.markdown('<div class="chat-container">', unsafe_allow_html=True)
            
            # Welcome message if conversation hasn't started
            if not st.session_state.conversation_started:
                st.markdown("""
                <div class="info-box">
                <div style="text-align: center; margin-bottom: 20px;">
                    <div style="font-size: 60px; margin-bottom: 10px;">🎯</div>
                    <h2 style="margin: 0; color: #2d3748;">Welcome to TalentScout!</h2>
                </div>
                <p style="font-size: 16px; text-align: center; margin-bottom: 25px; color: #4a5568;">I'm your AI hiring assistant, here to help streamline your interview process. 
                I'll gather some basic information about you and ask relevant technical questions 
                based on your expertise.</p>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 25px 0;">
                    <div style="text-align: center; padding: 15px; background: rgba(255,255,255,0.7); border-radius: 10px;">
                        <div style="font-size: 24px; margin-bottom: 8px;">📝</div>
                        <strong>Information Collection</strong>
                        <div style="font-size: 14px; opacity: 0.8;">Basic details & contact info</div>
                    </div>
                    <div style="text-align: center; padding: 15px; background: rgba(255,255,255,0.7); border-radius: 10px;">
                        <div style="font-size: 24px; margin-bottom: 8px;">🔧</div>
                        <strong>Tech Stack Discussion</strong>
                        <div style="font-size: 14px; opacity: 0.8;">Share your expertise</div>
                    </div>
                    <div style="text-align: center; padding: 15px; background: rgba(255,255,255,0.7); border-radius: 10px;">
                        <div style="font-size: 24px; margin-bottom: 8px;">❓</div>
                        <strong>5 Technical Questions</strong>
                        <div style="font-size: 14px; opacity: 0.8;">Tailored to your skills</div>
                    </div>
                    <div style="text-align: center; padding: 15px; background: rgba(255,255,255,0.7); border-radius: 10px;">
                        <div style="font-size: 24px; margin-bottom: 8px;">⏱️</div>
                        <strong>10-15 Minutes</strong>
                        <div style="font-size: 14px; opacity: 0.8;">Quick & efficient</div>
                    </div>
                </div>
                <p style="text-align: center; font-weight: 600; color: #2d3748;">Ready to begin? Click the button below!</p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("🚀 Start Interview Process", type="primary", use_container_width=True):
                    st.session_state.conversation_started = True
                    st.session_state.hiring_assistant.start_conversation()
                    st.rerun()
            
            else:
                # Display conversation history
                for i, message in enumerate(st.session_state.conversation_history):
                    if message['role'] == 'user':
                        st.markdown(f"""
                        <div class="user-message chat-message" style="animation-delay: {i * 0.1}s;">
                        <div style="display: flex; align-items: center; margin-bottom: 5px;">
                            <div style="width: 30px; height: 30px; background: rgba(255,255,255,0.2); border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-right: 10px; font-weight: bold;">👤</div>
                            <strong style="font-size: 14px; opacity: 0.9;">You</strong>
                        </div>
                        <div style="margin-left: 40px; line-height: 1.5;">{message['content']}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class="assistant-message chat-message" style="animation-delay: {i * 0.1}s;">
                        <div style="display: flex; align-items: center; margin-bottom: 5px;">
                            <div style="width: 30px; height: 30px; background: rgba(255,255,255,0.2); border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-right: 10px; font-weight: bold;">🤖</div>
                            <strong style="font-size: 14px; opacity: 0.9;">TalentScout AI</strong>
                        </div>
                        <div style="margin-left: 40px; line-height: 1.6;">{message['content'].replace(chr(10), '<br>')}</div>
                        </div>
                        """, unsafe_allow_html=True)
                
                # Get current assistant message
                current_message = st.session_state.hiring_assistant.get_current_message()
                if current_message and (not st.session_state.conversation_history or 
                                      st.session_state.conversation_history[-1]['content'] != current_message):
                    st.markdown(f"""
                    <div class="assistant-message chat-message" style="animation: slideIn 0.5s ease-out;">
                    <div style="display: flex; align-items: center; margin-bottom: 5px;">
                        <div style="width: 30px; height: 30px; background: rgba(255,255,255,0.2); border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-right: 10px; font-weight: bold;">🤖</div>
                        <strong style="font-size: 14px; opacity: 0.9;">TalentScout AI</strong>
                        <div style="margin-left: auto; font-size: 12px; opacity: 0.7;">●</div>
                    </div>
                    <div style="margin-left: 40px; line-height: 1.6;">{current_message.replace(chr(10), '<br>')}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Add to conversation history
                    st.session_state.conversation_history.append({
                        'role': 'assistant',
                        'content': current_message
                    })
                
                # Check if conversation is complete
                if st.session_state.hiring_assistant.is_conversation_complete():
                    st.success("✅ Interview process completed! Thank you for your time.")
                    
                    # Display summary with advanced analytics
                    candidate_info = st.session_state.hiring_assistant.get_candidate_summary()
                    performance_stats = st.session_state.hiring_assistant.get_performance_stats()
                    
                    if candidate_info:
                        with st.expander("📋 Interview Summary", expanded=True):
                            # Candidate information
                            st.subheader("👤 Candidate Information")
                            for key, value in candidate_info.items():
                                if value and not key.startswith('question_'):  # Only show non-empty values, exclude question answers
                                    st.write(f"**{key.replace('_', ' ').title()}:** {value}")
                            
                            # Technical answers
                            st.subheader("💻 Technical Responses")
                            for key, value in candidate_info.items():
                                if key.startswith('question_') and value:
                                    question_num = key.split('_')[1]
                                    st.write(f"**Question {question_num} Answer:** {value}")
                            
                            # Advanced analytics
                            st.subheader("📊 Interview Analytics")
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.metric("Interview Duration", f"{performance_stats['total_session_time']:.1f}s")
                            with col2:
                                st.metric("Avg Response Time", f"{performance_stats['average_response_time']:.2f}s")
                            with col3:
                                st.metric("Language Detected", performance_stats['detected_language'].upper())
                            
                            # Sentiment analysis
                            if performance_stats['sentiment_distribution']:
                                st.subheader("😊 Sentiment Analysis")
                                sentiment_data = performance_stats['sentiment_distribution']
                                st.bar_chart(sentiment_data)
                    
                    # Reset button
                    if st.button("🔄 Start New Interview", type="secondary", use_container_width=True):
                        # Clear session state
                        for key in list(st.session_state.keys()):
                            del st.session_state[key]
                        st.rerun()
                
                else:
                    # Create a form to handle Enter key press
                    with st.form(key="chat_form", clear_on_submit=True):
                        user_input = st.text_input(
                            "Your response:",
                            placeholder="Type your response here and press Enter to send...",
                            label_visibility="collapsed",
                            key="chat_input"
                        )
                        
                        send_button = st.form_submit_button("📤 Send", type="primary", use_container_width=True)
                    
                    # End button outside the form
                    end_button = st.button("🔚 End", type="secondary", use_container_width=True)
                    
                    # Handle user input
                    if send_button and user_input and user_input.strip():
                        # Add user message to history
                        st.session_state.conversation_history.append({
                            'role': 'user',
                            'content': user_input
                        })
                        
                        # Process response
                        try:
                            st.session_state.hiring_assistant.process_user_input(user_input)
                            # Clear input field by rerunning
                            st.rerun()
                        except Exception as e:
                            st.error(f"An error occurred: {str(e)}")
                            logger.error(f"Error processing user input: {e}")
                    
                    # Handle end conversation
                    if end_button:
                        st.session_state.hiring_assistant.end_conversation()
                        st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown("""
    <div class="footer">
    <p>🔒 Your information is handled securely and in compliance with data privacy standards.</p>
    <p>Powered by TalentScout AI • Built with Streamlit & Google Gemini</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
