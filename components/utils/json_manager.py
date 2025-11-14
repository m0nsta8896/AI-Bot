# components/utils/json_manager.py
import json
import os

class JSON:
    def load(self, path: str) -> dict:
        try:
            if os.path.exists(path):
                with open(path, "r", encoding='utf-8') as f:
                    data = json.load(f)
                    return data
            print(f"JSON.LOAD: File not found: {path}. Returning empty dictionary.")
            return {}
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            print(f"JSON.LOAD: Error decoding JSON or file: {path}. Details: {e}")
            return {}
        except OSError as e:
            print(f"JSON.LOAD: An unexpected error occurred loading {path}. Details: {e}")
            return {}
    
    def save(self, path: str, data: dict) -> bool:
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
                return True
        except OSError as e:
            print(f"JSON.SAVE: Error saving {path}. Details: {e}")
            return False
json_file = JSON()