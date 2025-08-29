import requests
import json
import base64
import re
from typing import List, Dict, Optional, Generator
from flask import current_app
from flask_login import current_user


class OllamaClient:
    def __init__(self, base_url: str = None):
        self.base_url = base_url or current_app.config.get('OLLAMA_URL', 'http://localhost:11434')
    
    @classmethod
    def from_user_settings(cls, user_id: int = None):
        """Create OllamaClient using the user's saved settings, fallback to admin settings"""
        try:
            if user_id is None and current_user and current_user.is_authenticated:
                user_id = current_user.id
            
            from models import Settings, User
            
            # Try to get current user's settings first
            if user_id:
                settings = Settings.query.filter_by(user_id=user_id).first()
                if settings and settings.ollama_url:
                    ollama_url = settings.ollama_url
                    # Only auto-correct localhost URLs in Docker environment
                    if ollama_url == 'http://localhost:11434' and current_app.config.get('FLASK_ENV') == 'production':
                        ollama_url = 'http://host.docker.internal:11434'
                        current_app.logger.info(f"Auto-correcting localhost to host.docker.internal for Docker environment")
                    return cls(ollama_url)
            
            # Fallback to admin user settings
            admin_user = User.query.filter_by(is_admin=True).first()
            if admin_user:
                admin_settings = Settings.query.filter_by(user_id=admin_user.id).first()
                if admin_settings and admin_settings.ollama_url:
                    ollama_url = admin_settings.ollama_url
                    # Only auto-correct localhost URLs in Docker environment
                    if ollama_url == 'http://localhost:11434' and current_app.config.get('FLASK_ENV') == 'production':
                        ollama_url = 'http://host.docker.internal:11434'
                        current_app.logger.info(f"Using admin settings with auto-corrected URL for Docker environment")
                    return cls(ollama_url)
            
            # Final fallback to config default
            default_url = current_app.config.get('OLLAMA_URL', 'http://host.docker.internal:11434')
            return cls(default_url)
        except Exception:
            # Final fallback if anything goes wrong
            default_url = current_app.config.get('OLLAMA_URL', 'http://host.docker.internal:11434')
            return cls(default_url)
    
    @staticmethod
    def get_user_models(user_id: int = None):
        """Get user's saved chat and vision models, fallback to admin settings"""
        try:
            if user_id is None and current_user and current_user.is_authenticated:
                user_id = current_user.id
            
            from models import Settings, User
            
            # Try to get current user's settings first
            if user_id:
                settings = Settings.query.filter_by(user_id=user_id).first()
                if settings and (settings.chat_model or settings.vision_model):
                    return {
                        'chat_model': settings.chat_model,
                        'vision_model': settings.vision_model,
                        'system_prompt': settings.system_prompt
                    }
            
            # Fallback to admin user settings
            admin_user = User.query.filter_by(is_admin=True).first()
            if admin_user:
                admin_settings = Settings.query.filter_by(user_id=admin_user.id).first()
                if admin_settings:
                    return {
                        'chat_model': admin_settings.chat_model or current_app.config.get('DEFAULT_CHAT_MODEL', 'llama2'),
                        'vision_model': admin_settings.vision_model or current_app.config.get('DEFAULT_VISION_MODEL', 'llava'),
                        'system_prompt': admin_settings.system_prompt
                    }
            
            # Final fallback to config defaults
            return {
                'chat_model': current_app.config.get('DEFAULT_CHAT_MODEL', 'llama2'),
                'vision_model': current_app.config.get('DEFAULT_VISION_MODEL', 'llava'),
                'system_prompt': None
            }
        except Exception:
            # Final fallback if anything goes wrong
            return {
                'chat_model': current_app.config.get('DEFAULT_CHAT_MODEL', 'llama2'),
                'vision_model': current_app.config.get('DEFAULT_VISION_MODEL', 'llava'),
                'system_prompt': None
            }
    
    def _make_request(self, endpoint: str, method: str = 'GET', data: dict = None, timeout: int = 180) -> requests.Response:
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        
        if method == 'GET':
            response = requests.get(url, timeout=timeout)
        elif method == 'POST':
            headers = {'Content-Type': 'application/json'}
            response = requests.post(url, json=data, headers=headers, timeout=timeout)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        return response
    
    def test_connection(self) -> bool:
        try:
            response = self._make_request('api/tags')
            return response.status_code == 200
        except Exception:
            return False
    
    def list_models(self) -> List[Dict]:
        try:
            response = self._make_request('api/tags')
            if response.status_code == 200:
                data = response.json()
                return data.get('models', [])
            return []
        except Exception as e:
            current_app.logger.error(f"Error listing models: {e}")
            return []
    
    def pull_model(self, model_name: str) -> bool:
        try:
            data = {'name': model_name}
            response = self._make_request('api/pull', 'POST', data)
            return response.status_code == 200
        except Exception as e:
            current_app.logger.error(f"Error pulling model {model_name}: {e}")
            return False
    
    def chat(self, messages: List[Dict], model: str, system_prompt: str = None, stream: bool = False) -> Generator[str, None, None]:
        try:
            # Prepare the request data
            data = {
                'model': model,
                'messages': messages,
                'stream': stream
            }
            
            if system_prompt:
                # Add system message at the beginning
                system_message = {'role': 'system', 'content': system_prompt}
                data['messages'] = [system_message] + messages
            
            url = f"{self.base_url.rstrip('/')}/api/chat"
            headers = {'Content-Type': 'application/json'}
            
            response = requests.post(url, json=data, headers=headers, stream=stream, timeout=180)
            
            if stream:
                for line in response.iter_lines():
                    if line:
                        try:
                            chunk = json.loads(line.decode('utf-8'))
                            if 'message' in chunk and 'content' in chunk['message']:
                                yield chunk['message']['content']
                            elif chunk.get('done', False):
                                break
                        except json.JSONDecodeError:
                            continue
            else:
                if response.status_code == 200:
                    result = response.json()
                    if 'message' in result and 'content' in result['message']:
                        yield result['message']['content']
                else:
                    yield f"Error: {response.status_code} - {response.text}"
        
        except Exception as e:
            current_app.logger.error(f"Error in chat: {e}")
            yield f"Error communicating with AI: {str(e)}"
    
    def vision_analyze(self, image_path: str, model: str, prompt: str = "Describe what food items you see in this image.") -> Optional[str]:
        try:
            # Read and encode the image
            with open(image_path, 'rb') as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')

            # Prefer chat API for multimodal models; include image in user message
            chat_payload = {
                'model': model,
                'messages': [
                    {
                        'role': 'user',
                        'content': prompt,
                        'images': [image_data]
                    }
                ],
                # Ask for strict JSON output when supported by the model/server
                'format': 'json',
                'options': {
                    'temperature': 0.2
                },
                'stream': False
            }

            try:
                chat_url = f"{self.base_url.rstrip('/')}/api/chat"
                headers = {'Content-Type': 'application/json'}
                response = requests.post(chat_url, json=chat_payload, headers=headers, timeout=180)
                if response.status_code == 200:
                    result = response.json()
                    if 'message' in result and 'content' in result['message']:
                        return result['message']['content']
                else:
                    current_app.logger.warning(f"Vision chat returned {response.status_code}: {response.text}")
            except Exception as e:
                current_app.logger.warning(f"Vision chat path failed, falling back to generate: {e}")

            # Fallback to generate API with images if chat path fails
            generate_payload = {
                'model': model,
                'prompt': prompt,
                'images': [image_data],
                'format': 'json',
                'options': {
                    'temperature': 0.2
                },
                'stream': False
            }

            response = self._make_request('api/generate', 'POST', generate_payload)
            if response.status_code == 200:
                result = response.json()
                # Some servers return { response: "..." }
                if isinstance(result, dict):
                    return result.get('response') or result.get('message', {}).get('content', '')
                return None
            else:
                current_app.logger.error(f"Vision generate returned {response.status_code}: {response.text}")
                return None

        except Exception as e:
            current_app.logger.error(f"Error in vision analysis: {e}")
            return None
    
    def vision_classify(self, image_path: str, model: str) -> List[Dict]:
        try:
            prompt = """Identify the food items in this image. For each food item, provide:
1. Name of the food item
2. Estimated portion size
3. Confidence level (0-1)

Return the response as a JSON array with objects containing 'name', 'portion', and 'confidence' fields."""
            
            result = self.vision_analyze(image_path, model, prompt)
            
            if result:
                try:
                    # Try to extract JSON from the response
                    import re
                    json_match = re.search(r'\[.*\]', result, re.DOTALL)
                    if json_match:
                        return json.loads(json_match.group())
                    else:
                        # Fallback: parse the text response
                        return self._parse_vision_text(result)
                except json.JSONDecodeError:
                    return self._parse_vision_text(result)
            
            return []
        
        except Exception as e:
            current_app.logger.error(f"Error in vision classification: {e}")
            return []
    
    def _parse_vision_text(self, text: str) -> List[Dict]:
        """Parse vision response text into structured data"""
        items = []
        lines = text.split('\n')
        
        current_item = {}
        for line in lines:
            line = line.strip()
            if 'name' in line.lower() or 'food' in line.lower():
                if current_item:
                    items.append(current_item)
                current_item = {'name': line, 'portion': '100g', 'confidence': 0.7}
            elif 'portion' in line.lower() or 'size' in line.lower():
                current_item['portion'] = line
            elif 'confidence' in line.lower():
                try:
                    conf = float(re.search(r'(\d+\.?\d*)', line).group())
                    if conf > 1:
                        conf = conf / 100
                    current_item['confidence'] = conf
                except:
                    current_item['confidence'] = 0.7
        
        if current_item:
            items.append(current_item)
        
        return items[:5]  # Limit to 5 items