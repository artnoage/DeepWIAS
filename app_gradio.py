import gradio as gr
import requests
import json

# Store conversation history
messages = []

def test_connection():
    try:
        response = requests.post(
            'http://10.8.85.181:9000/v1/chat/completions',
            headers={
                'Content-Type': 'application/json',
                'Authorization': 'Bearer EMPTY'
            },
            json={
                'model': 'unsloth/Phi-4',
                'messages': [{
                    'role': 'user',
                    'content': 'test'
                }],
                'max_tokens': 1,
                'temperature': 0
            }
        )
        
        if not response.ok:
            return {
                'success': False,
                'error': f'Server error: {response.status_code} - {response.text}'
            }
        
        return {
            'success': True
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Connection error: {str(e)}'
        }

def chat_with_bot(message, history):
    global messages
    
    if not message.strip():
        return "", history
    
    # Test connection first
    connection_test = test_connection()
    if not connection_test['success']:
        return f"Error: {connection_test['error']}", history
    
    # Add user message to history
    messages.append({
        'role': 'user',
        'content': message
    })
    
    try:
        response = requests.post(
            'http://10.8.85.181:9000/v1/chat/completions',
            headers={
                'Content-Type': 'application/json',
                'Authorization': 'Bearer EMPTY'
            },
            json={
                'model': 'unsloth/Phi-4',
                'messages': messages,
                'max_tokens': 50,
                'temperature': 0
            }
        )
        
        data = response.json()
        bot_response = data['choices'][0]['message']['content']
        
        # Add assistant response to history
        messages.append({
            'role': 'assistant',
            'content': bot_response
        })
        
        return "", history + [[message, bot_response]]
    except Exception as e:
        error_message = f"Error: {str(e)}"
        return "", history + [[message, error_message]]

# Create Gradio interface
with gr.Blocks(css="footer {visibility: hidden}") as demo:
    gr.Markdown("# DeepWIAS")
    
    chatbot = gr.Chatbot(height=400)
    msg = gr.Textbox(placeholder="Type your message...", show_label=False)
    clear = gr.Button("Clear")
    
    msg.submit(chat_with_bot, [msg, chatbot], [msg, chatbot])
    clear.click(lambda: None, None, chatbot, queue=False)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=9001)
