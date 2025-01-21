from datetime import datetime
import json
from functools import wraps

def json_to_dict(func):
    """
    Decorator to convert a JSON string input into a dictionary.
    """
    @wraps(func)
    def wrapper(input_str):
        try:
            input_dict = json.loads(input_str)
            return func(**input_dict)
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON input. Please provide a valid JSON string.")
    return wrapper

@json_to_dict
def get_today_date(input : str) -> str:
    import datetime
    today = datetime.date.today()
    return f"\n {today} \n"

@json_to_dict
def greeting(input: str) -> str:
    """Handle greetings and basic conversations"""
    greetings = {
        "hello": "Hello! I'm RaidenX, your crypto trading assistant. How can I help you today?",
        "hi": "Hi there! Ready to help you with your crypto trading needs!",
        "hey": "Hey! What can I do for you today?",
        "good morning": "Good morning! Ready to explore the crypto markets with you!",
        "good afternoon": "Good afternoon! How can I assist you with crypto trading today?",
        "good evening": "Good evening! Looking forward to helping you with your trading needs!"
    }
    
    input_lower = input.lower().strip()
    return greetings.get(input_lower, "Hello! I'm RaidenX. How can I assist you with crypto trading today?")

@json_to_dict
def crypto_knowledge(input: str) -> str:
    """Provide information about cryptocurrency, blockchain, trading, and market dynamics"""
    return """I can help answer questions about:
    
1. Cryptocurrency basics and specific coins
2. Blockchain technology and its applications
3. Trading strategies and analysis
4. Market trends and dynamics
5. DeFi protocols and services
6. Security and best practices

Please ask your specific question about any of these topics."""


