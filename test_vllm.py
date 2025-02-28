import requests
import json

def test_vllm_request(prompt="Hello, how are you?"):
    url = "http://10.8.85.181:9000/v1/completions"
    
    headers = {
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "unsloth/phi4",
        "prompt": prompt,
        "max_tokens": 50
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        result = response.json()
        print("Server Response:")
        print(json.dumps(result, indent=2))
        
        if "choices" in result and len(result["choices"]) > 0:
            print("\nAI Response:")
            print(result["choices"][0]["text"])
            
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")
    except json.JSONDecodeError:
        print("Error: Could not parse server response as JSON")
        print("Raw response:", response.text)

if __name__ == "__main__":
    test_vllm_request()
