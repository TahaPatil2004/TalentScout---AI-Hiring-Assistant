import re
from typing import Optional, Union
import logging

logger = logging.getLogger(__name__)

class DataValidator:
    """Utility class for validating and extracting data from user inputs."""
    
    def __init__(self):
        """Initialize the data validator with regex patterns."""
        # Email pattern
        self.email_pattern = re.compile(
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        )
        
        # Phone patterns - multiple formats
        self.phone_patterns = [
            re.compile(r'\+?\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'),  # +1-555-123-4567
            re.compile(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'),  # (555) 123-4567
            re.compile(r'\d{10,}'),  # 5551234567
        ]
        
        # Experience pattern - numbers with optional decimal
        self.experience_pattern = re.compile(r'\b(\d+(?:\.\d+)?)\b')
    
    def extract_email(self, text: str) -> Optional[str]:
        """Extract email address from text."""
        try:
            match = self.email_pattern.search(text)
            if match:
                email = match.group(0)
                # Basic validation
                if self.is_valid_email(email):
                    return email.lower()
        except Exception as e:
            logger.error(f"Error extracting email: {e}")
        
        return None
    
    def extract_phone(self, text: str) -> Optional[str]:
        """Extract phone number from text."""
        try:
            # Clean the text first
            cleaned_text = re.sub(r'[^\d\+\-\(\)\.\s]', '', text)
            
            for pattern in self.phone_patterns:
                match = pattern.search(cleaned_text)
                if match:
                    phone = match.group(0)
                    # Clean and validate
                    cleaned_phone = self.clean_phone_number(phone)
                    if self.is_valid_phone(cleaned_phone):
                        return cleaned_phone
        except Exception as e:
            logger.error(f"Error extracting phone: {e}")
        
        return None
    
    def extract_experience(self, text: str) -> Optional[float]:
        """Extract years of experience from text."""
        try:
            # Look for numbers in the text
            matches = self.experience_pattern.findall(text)
            
            if matches:
                # Take the first number found
                experience = float(matches[0])
                # Validate range (0-50 years is reasonable)
                if 0 <= experience <= 50:
                    return experience
                    
            # Handle special cases
            text_lower = text.lower()
            if any(word in text_lower for word in ['fresh', 'graduate', 'entry', 'new', 'beginner']):
                return 0.0
            if 'intern' in text_lower:
                return 0.5
                
        except Exception as e:
            logger.error(f"Error extracting experience: {e}")
        
        return None
    
    def is_valid_email(self, email: str) -> bool:
        """Validate email format."""
        try:
            if not email or len(email) > 254:
                return False
            
            # Check for basic email structure
            if email.count('@') != 1:
                return False
            
            local, domain = email.split('@')
            
            # Validate local part
            if not local or len(local) > 64:
                return False
            
            # Validate domain part
            if not domain or len(domain) > 253:
                return False
            
            # Domain should have at least one dot
            if '.' not in domain:
                return False
            
            return True
            
        except Exception:
            return False
    
    def is_valid_phone(self, phone: str) -> bool:
        """Validate phone number."""
        try:
            if not phone:
                return False
            
            # Remove all non-digit characters for validation
            digits_only = re.sub(r'\D', '', phone)
            
            # Should have 10-15 digits
            return 10 <= len(digits_only) <= 15
            
        except Exception:
            return False
    
    def clean_phone_number(self, phone: str) -> str:
        """Clean and format phone number."""
        try:
            # Remove extra whitespace
            phone = phone.strip()
            
            # If it's all digits, format nicely
            digits_only = re.sub(r'\D', '', phone)
            
            if len(digits_only) == 10:
                # Format as (XXX) XXX-XXXX
                return f"({digits_only[:3]}) {digits_only[3:6]}-{digits_only[6:]}"
            elif len(digits_only) == 11 and digits_only[0] == '1':
                # Format as +1 (XXX) XXX-XXXX
                return f"+1 ({digits_only[1:4]}) {digits_only[4:7]}-{digits_only[7:]}"
            else:
                # Return as-is if non-standard format
                return phone
                
        except Exception:
            return phone
    
    def sanitize_text(self, text: str) -> str:
        """Sanitize text input to prevent potential security issues."""
        try:
            if not text:
                return ""
            
            # Remove potentially dangerous characters
            sanitized = re.sub(r'[<>"\']', '', text)
            
            # Limit length
            sanitized = sanitized[:1000]
            
            # Remove extra whitespace
            sanitized = ' '.join(sanitized.split())
            
            return sanitized
            
        except Exception:
            return ""
