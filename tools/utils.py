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




