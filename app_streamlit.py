import streamlit as st
import requests
import json

# Set page title and layout
st.set_page_config(page_title="DeepWIAS", layout="centered")

# Add custom CSS
st.markdown("""
<style>
    .stApp {
        max-width: 800px;
        margin: 0 auto;
    }
    .user-message {
        background-color: #e6f7ff;
        padding: 10px;
        border-radius: 10px;
        margin: 5px 0;
        text-align: right;
    }
    .bot-message {
        background-color: #f0f0f0;
        padding: 10px;
        border-radius: 10px;
        margin: 5px 0;
        text-align: left;
    }
    .chat-title {
        text-align: center;
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for messages
if "messages" not in st.session_state:
    st.session_state.messages = []

# Function to clear chat history
def clear_chat():
    st.session_state.messages = []

# Display chat title and clear button
col1, col2 = st.columns([5, 1])
with col1:
    st.markdown("<div class='chat-title'>DeepWIAS</div>", unsafe_allow_html=True)
with col2:
    st.button("Clear Chat", on_click=clear_chat)

def test_connection():
    try:
        response = requests.post(
            'http://10.8.85.181:9002/v1/chat/completions',
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

# Display existing messages
for message in st.session_state.messages:
    if message["role"] == "user":
        st.markdown(f"<div class='user-message'>{message['content']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='bot-message'>{message['content']}</div>", unsafe_allow_html=True)

# User input with send button
col1, col2 = st.columns([5, 1])
with col1:
    user_input = st.text_input("Type your message...", key="user_input")
with col2:
    send_button = st.button("Send")

# Process input when either the input field is submitted or send button is clicked
if user_input and (st.session_state.user_input != "" or send_button):

# This block is replaced by the new input handling above
    # Test connection first
    connection_test = test_connection()
    if not connection_test['success']:
        st.error(f"Error: {connection_test['error']}")
    else:
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.markdown(f"<div class='user-message'>{user_input}</div>", unsafe_allow_html=True)
        
        # Prepare API call
        api_messages = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
        
        try:
            # Call API
            with st.spinner("Thinking..."):
                response = requests.post(
                    'http://10.8.85.181:9002/v1/chat/completions',
                    headers={
                        'Content-Type': 'application/json',
                        'Authorization': 'Bearer EMPTY'
                    },
                    json={
                        'model': 'unsloth/Phi-4',
                        'messages': api_messages,
                        'max_tokens': 50,
                        'temperature': 0
                    }
                )
                
                data = response.json()
                bot_response = data['choices'][0]['message']['content']
                
                # Add bot response to chat
                st.session_state.messages.append({"role": "assistant", "content": bot_response})
                st.markdown(f"<div class='bot-message'>{bot_response}</div>", unsafe_allow_html=True)
                
        except Exception as e:
            st.error(f"Error: {str(e)}")
        
        # Clear the input box - no need for experimental_rerun
        st.session_state.user_input = ""
