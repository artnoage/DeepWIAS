import requests
import json

def send_message(message, conversation_history):
    url = "http://10.8.85.181:9002/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer EMPTY"
    }
    
    conversation_history.append({"role": "user", "content": message})
    payload = {
        "model": "mistralai/Mistral-Small-24B-Instruct-2501",
        "messages": conversation_history,
        "max_tokens": 50,
        "temperature": 0
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        data = response.json()
        bot_response = data["choices"][0]["message"]["content"]
        
        conversation_history.append({"role": "assistant", "content": bot_response})
        return bot_response
    except requests.exceptions.RequestException as e:
        return f"Error: {e}"

def main():
    print("Welcome to DeepWIAS Terminal Chat! Type 'exit' to quit.")
    conversation_history = []
    
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() == "exit":
            print("Goodbye!")
            break
        
        bot_reply = send_message(user_input, conversation_history)
        print(f"Bot: {bot_reply}")

if __name__ == "__main__":
    main()