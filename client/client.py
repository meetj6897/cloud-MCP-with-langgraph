import asyncio
from dotenv import load_dotenv
from langchain_core.messages import ToolMessage
from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.client import MultiServerMcpClient

# Load API keys from the .env file (OpenAI API Key)
load_dotenv()

async def main():
    # Step 1: Define configuration for multiple MCP servers
    # This dictionary supports local servers via 'stdio' and remote servers via 'sse'
    servers = {
        # Local Math MCP Server using the standard input/output transport layer
        "math": {
            "transport": "stdio",
            "command": "uv",
            "args": [
                "run", 
                "fastmcp", 
                "run", 
                "/path/to/your/local/math_server/main.py"
            ]
        },
        # Remote Expense Tracker MCP Server hosted over HTTP Server-Sent Events (SSE)
        "expense": {
            "transport": "sse",
            "url": "https://your-remote-mcp-server-endpoint.cloud"
        }
    }

    # Step 2: Initialize the Multi-Server MCP Client with the configurations
    print("Initializing MultiServerMcpClient...")
    client = MultiServerMcpClient(servers=servers)

    # Step 3: Fetch all exposure tools from the connected MCP servers
    # The client handles launching local servers and connecting to remote endpoints internally
    tools_list = await client.get_tools()
    
    # Restructure the tools into a dictionary mapping tool names to tool objects 
    # for cleaner routing and easy runtime execution
    named_tools = {tool.name: tool for tool in tools_list}
    print(f"Successfully loaded {len(named_tools)} tools: {list(named_tools.keys())}")

    # Step 4: Initialize the Chat Model and Bind the MCP Tools
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    llm_with_tools = llm.bind_tools(tools_list)

    # Step 5: Define the user prompt (Requires either tool calling or generic response)
    # Example 1 (Math Tool): "What is the remainder of 231423 divided by 7?"
    # Example 2 (Expense Tool): "Add an expense of 800 INR for groceries on 4th November"
    prompt = "What is the remainder of 231423 divided by 7?"
    print(f"\nUser Prompt: {prompt}")

    # Step 6: Invoke the LLM with tool capabilities to check for execution requirements
    initial_response = await llm_with_tools.ainvoke(prompt)

    # Step 7: Evaluate if the LLM needs to call external tools
    if not initial_response.tool_calls:
        # If no tool is needed, print the direct generic response and exit
        print(f"LLM Direct Response: {initial_response.content}")
        return

    # Step 8: Execute requested tools in a loop (Supports multiple simultaneous tool calls)
    tool_messages = []
    for tool_call in initial_response.tool_calls:
        selected_tool_name = tool_call["name"]
        selected_tool_args = tool_call["args"]
        selected_tool_id = tool_call["id"]

        print(f"\n[Tool Call Requested] Name: '{selected_tool_name}' | Arguments: {selected_tool_args}")

        if selected_tool_name in named_tools:
            # Dynamically execute the specific tool asynchronously using its arguments
            tool_object = named_tools[selected_tool_name]
            tool_result = await tool_object.ainvoke(selected_tool_args)
            
            # Format the output into a structured ToolMessage along with the execution ID
            tool_message = ToolMessage(
                content=str(tool_result),
                tool_call_id=selected_tool_id
            )
            tool_messages.append(tool_message)
            print(f"[Tool Execution Result]: {tool_result}")
        else:
            print(f"Error: Tool '{selected_tool_name}' was requested but not found.")

    # Step 9: Pass the entire conversation history back to the LLM to get the final answer
    if tool_messages:
        final_history = [
            {"role": "user", "content": prompt},
            initial_response,
            *tool_messages
        ]
        
        final_response = await llm_with_tools.ainvoke(final_history)
        print(f"\nFinal Answer: {final_response.content}")

if __name__ == "__main__":
    # Run the main asynchronous event loop
    asyncio.run(main())