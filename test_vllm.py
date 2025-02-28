import asyncio
from chat_client import VLLMChatClient

async def test_vllm_request(prompt="Hello, how are you?"):
    client = VLLMChatClient()
    
    # Test connection first
    connection_test = client.test_connection()
    if not connection_test["success"]:
        print(f"Connection test failed: {connection_test['error']}")
        return
    
    try:
        response = await client.ainvoke(prompt)
        print("\nUser prompt:")
        print(prompt)
        print("\nAI Response:")
        print(response.content)
            
    except Exception as e:
        print(f"Error making request: {e}")

if __name__ == "__main__":
    asyncio.run(test_vllm_request())
