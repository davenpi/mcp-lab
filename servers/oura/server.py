"""
The goal is to build an MCP server that can get my sleep data from my Oura Ring.

Oura API: https://cloud.ouraring.com/v2/docs
"""

from fastmcp import FastMCP

mcp = FastMCP()


@mcp.tool()
def get_sleep_data(date: str) -> dict:
    """Get sleep data for a given date"""
    return {"sleep_data": "sleep_data"}


if __name__ == "__main__":
    mcp.run()
