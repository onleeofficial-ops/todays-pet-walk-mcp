from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations


# PlayMCP 배포 환경에서 외부 접근이 가능하도록
# 반드시 0.0.0.0에 바인딩합니다.
mcp = FastMCP(
    name="TodaysPetWalk",
    host="0.0.0.0",
    port=8000,
    stateless_http=True,
    json_response=True,
)


@mcp.tool(
    name="check_server",
    description=(
        "Checks whether the Today's Pet Walk MCP server is running normally. "
        "Use this tool only to verify the server connection."
    ),
    annotations=ToolAnnotations(
        title="Check Today's Pet Walk Server",
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    ),
)
def check_server() -> str:
    """Checks whether the MCP server is operating normally."""

    return "Today's Pet Walk MCP server is operating normally."


@mcp.tool(
    name="recommend_walk",
    description=(
        "Provides a basic walking response from Today's Pet Walk using the "
        "dog's name and the requested location. This is currently a connection "
        "verification tool and does not search live place data."
    ),
    annotations=ToolAnnotations(
        title="Recommend a Basic Dog Walk",
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    ),
)
def recommend_walk(
    dog_name: str,
    location: str,
) -> str:
    """
    Provides a basic dog-walking response.

    Args:
        dog_name: Name of the dog.
        location: Area where the user wants to walk.
    """

    return (
        f"{dog_name}와 함께 {location}에서 산책할 장소를 확인합니다. "
        "현재는 MCP 연결 검증을 위한 기본 응답입니다."
    )


if __name__ == "__main__":
    mcp.run(transport="streamable-http")