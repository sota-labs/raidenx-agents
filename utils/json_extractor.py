import re
import json
from typing import Optional, Any
    
def extract_json_from_text(input_str: str) -> Any:
    """
    Clean and convert JSON string to Python object, ensuring flexible handling.
    """
    cleaned_str = input_str.strip()
    
    try:
        return json.loads(cleaned_str)
    except json.JSONDecodeError:
        fixed_str = re.search(r'{.*}', cleaned_str, re.DOTALL)
        if fixed_str:
            json_data = fixed_str.group(0)
            try:
                return json.loads(json_data)
            except json.JSONDecodeError as e:
                raise ValueError(f"Error parsing JSON after cleaning: {e}")
        else:
            raise ValueError("No valid JSON found in input string.")