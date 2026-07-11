from mcp.server.fastmcp import FastMCP


# MCP 서버 생성
mcp = FastMCP(
    name="Pet Walk MCP",
    stateless_http=True,
    json_response=True,
)


@mcp.tool()
def check_server() -> str:
    """
    MCP 서버가 정상적으로 실행 중인지 확인합니다.
    """

    return "Pet Walk MCP 서버가 정상적으로 작동하고 있습니다."


@mcp.tool()
def recommend_walk(
    dog_name: str,
    location: str,
) -> str:
    """
    반려견 이름과 현재 지역을 기준으로 산책 안내를 제공합니다.

    Args:
        dog_name: 반려견 이름
        location: 산책할 지역
    """

    return (
        f"{dog_name}와 함께 {location}에서 산책할 장소를 찾겠습니다. "
        "현재는 MCP 서버 연결을 확인하기 위한 기본 기능입니다."
    )


if __name__ == "__main__":
    mcp.run(transport="streamable-http")