import json
from datetime import datetime
from pathlib import Path

class ToolHistoryLogger:
    def __init__(self, log_dir="temp/tool_history"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def save_tool_history(self, query, used_tools, response):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.log_dir / f"tool_history_{timestamp}.json"
        
        history_data = {
            "timestamp": timestamp,
            "query": query,
            "used_tools": used_tools,
            "response": response
        }
        
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(history_data, f, ensure_ascii=False, indent=2)
        
        return filename 