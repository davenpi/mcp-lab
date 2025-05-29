import asyncio

from fastmcp import Client

client = Client("/Users/ian/Code/mcp-lab/servers/oura/server.py")


async def main():
    async with client:
        print(f"Client connected: {client.is_connected()}")

        tools = await client.list_tools()
        print(f"Available tools: {tools}")

        result = await client.call_tool(
            name="get_daily_sleep",
            arguments={"start_date": "2025-05-28"},
        )
        print(f"Result: {result}")


if __name__ == "__main__":
    asyncio.run(main())
