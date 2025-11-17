#!/usr/bin/env python3
"""Interactive UK Housing Agent - Talk to the housing expert."""

import asyncio
from langgraph_sdk import get_client


async def main():
    """Main interactive loop for UK Housing Agent."""
    
    print("\n" + "="*60)
    print("🏠 UK HOUSING AGENT - Aegra")
    print("="*60)
    print("Ask your housing-related questions to the AI expert!")
    print("Type 'quit' to exit\n")
    
    try:
        # Connect to Aegra
        client = get_client(url="http://localhost:8000")
        
        # Create assistant for UK Housing graph
        print("🤖 Initializing UK Housing Agent...")
        assistant = await client.assistants.create(
            graph_id="uk_housing",
            if_exists="do_nothing",
        )
        assistant_id = assistant["assistant_id"]
        print(f"✅ Assistant ready\n")
        
        # Create thread for conversation
        thread = await client.threads.create()
        thread_id = thread["thread_id"]
        
        # Interactive conversation loop
        conversation_turn = 1
        while True:
            # Get user input
            user_input = input(f"\n🔹 Question #{conversation_turn}: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye! Thanks for using UK Housing Agent.\n")
                break
            
            if not user_input:
                print("Please enter a question.")
                continue
            
            print(f"\n⏳ Thinking...\n")
            
            try:
                # Stream response from agent
                last_message = None
                issue_type = None
                
                stream = client.runs.stream(
                    thread_id=thread_id,
                    assistant_id=assistant_id,
                    input={
                        "messages": [
                            {
                                "type": "human",
                                "content": [
                                    {"type": "text", "text": user_input}
                                ]
                            }
                        ]
                    },
                    stream_mode=["values"],
                )
                
                # Collect response from stream
                async for chunk in stream:
                    if hasattr(chunk, 'data'):
                        if 'messages' in chunk.data:
                            messages = chunk.data['messages']
                            if messages:
                                last_msg = messages[-1]
                                # Handle both dict and message objects
                                if isinstance(last_msg, dict):
                                    if last_msg.get('type') == 'ai':
                                        last_message = last_msg.get('content', '')
                                elif hasattr(last_msg, 'type') and last_msg.type == 'ai':
                                    last_message = last_msg.content
                        if 'issue_type' in chunk.data:
                            issue_type = chunk.data['issue_type']
                
                # Display response
                if last_message:
                    print("🤖 Agent Response:")
                    print("-" * 50)
                    print(last_message)
                    if issue_type:
                        print(f"\n[Issue Type Detected: {issue_type.upper()}]")
                    print("-" * 50)
                else:
                    print("⚠️  No response received.")
                
                conversation_turn += 1
                
            except Exception as e:
                print(f"❌ Error getting response: {e}")
                print("Try again or type 'quit' to exit.\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure Aegra is running:")
        print("  cd /home/aegra && docker-compose up aegra")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted. Goodbye!\n")

