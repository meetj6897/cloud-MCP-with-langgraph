import asyncio
from langchain_mcp_adapters.client import MultiServerMcpClient #becasue we want to connect client with multiple server

#we need to add server configuration for multiple servers, we can add local server and remote server which we want to connect with client, we can add multiple server configuration in dictionary format, where key is server name and value is server configuration
servers = {}



async def main():
    print("Starting MultiServerMcpClient...by making the object")
    client = MultiServerMcpClient(servers=servers)
    print("Fetching tools from all connected MCP servers...")

    
if __name__ == "__main__":  # we 
    asyncio.run(main())