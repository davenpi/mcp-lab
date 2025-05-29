"""
The goal is to build an MCP server that can get my sleep data from my Oura Ring.

Oura API: https://cloud.ouraring.com/v2/docs
"""

import os
from datetime import date
from typing import Annotated

import httpx
from dotenv import load_dotenv
from fastmcp import FastMCP
from pydantic import Field

# FastMCP server
mcp = FastMCP(
    name="Oura Server",
    instructions="Built to get sleep data from my Oura Ring.",
)


@mcp.tool()
def get_daily_sleep(
    start_date: Annotated[date, Field(description="The start date of the sleep data.")],
    end_date: Annotated[
        date | None,
        Field(
            description=(
                "The end date of the sleep data. If None, will use the start date."
            ),
        ),
    ] = None,
) -> dict:
    """
    Get sleep data for a given date range.

    All sleep data is in the form of scores from 0 to 100. There are various
    contributors and one overall score for each day.

    Parameters
    ----------
    start_date : date
        The start date of the sleep data.
    end_date : date | None
        The end date of the sleep data. If None, will use the start date.

    Returns
    -------
    dict
        The sleep data. JSON object.
    """
    params = {
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat() if end_date else start_date.isoformat(),
    }
    url = "https://api.ouraring.com/v2/usercollection/daily_sleep"
    headers = {"Authorization": f"Bearer {os.getenv('OURA_API_KEY')}"}
    response = httpx.get(url, headers=headers, params=params)
    return response.json()


if __name__ == "__main__":
    load_dotenv()
    mcp.run()
