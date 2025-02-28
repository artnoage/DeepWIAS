import aiohttp
import json
from typing import Any, Optional

class VLLMChatClient:
    """Chat client for making requests to vLLM server using chat completion format"""
    
    def __init__(
        self,
        base_url: str = "http://10.8.85.181:9000/v1",
        model: str = "Phi-4",
        temperature: float = 0,
        api_key: str = "EMPTY"
    ):
        self.base_url = base_url
        self.model = model
        self.temperature = temperature
        self.api_key = api_key

    async def ainvoke(self, prompt: Any, **kwargs: Any) -> Any:
        """Async call to chat completion endpoint"""
        max_tokens = kwargs.get("max_tokens", 50)
        
        # Convert prompt to messages format
        if hasattr(prompt, 'content'):  # Message object
            messages = [{"role": "user", "content": prompt.content}]
        elif isinstance(prompt, list):  # List of messages
            messages = [{"role": "user", "content": prompt[-1].content}] if prompt else []
        else:  # String or other
            messages = [{"role": "user", "content": str(prompt)}]
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": max_tokens
        }

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    json=payload,
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {self.api_key}"
                    }
                ) as response:
                    if response.status != 200:
                        raise ValueError(f"Error from API: {await response.text()}")
                    
                    result = await response.json()
                    return type('Response', (), {
                        'content': result.get("choices", [{}])[0].get("message", {}).get("content", "")
                    })()
            except Exception as e:
                print(f"Exception in VLLMChatClient.ainvoke: {str(e)}")
                raise

    def test_connection(self) -> dict:
        """Test connection to the server"""
        import requests
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}"
                },
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": "test"}],
                    "max_tokens": 1,
                    "temperature": self.temperature
                }
            )
            
            if response.status_code != 200:
                return {
                    "success": False,
                    "error": f"Server error: {response.status_code} - {response.text}"
                }
            
            return {"success": True}
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Connection error: {str(e)}"
            }
