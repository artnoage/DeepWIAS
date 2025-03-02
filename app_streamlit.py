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

# Define a function to handle message submission
def handle_message():
    if st.session_state.user_input and st.session_state.user_input.strip():
        user_message = st.session_state.user_input
        # Test connection first
        connection_test = test_connection()
        if not connection_test['success']:
            st.error(f"Error: {connection_test['error']}")
        else:
            # Add user message to chat
            st.session_state.messages.append({"role": "user", "content": user_message})
            
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
                    
            except Exception as e:
                st.error(f"Error: {str(e)}")
            
        # Clear the input box
        st.session_state.user_input = ""

# User input with send button
col1, col2 = st.columns([5, 1])
with col1:
    st.text_input("Type your message...", key="user_input")
with col2:
    st.button("Send", on_click=handle_message)

# Check if enter was pressed in the input field
if "user_input" in st.session_state and st.session_state.user_input:
    handle_message()
