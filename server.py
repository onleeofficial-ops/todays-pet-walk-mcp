from typing import Any, Dict, Optional, Tuple

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations


# PlayMCP 배포 환경에서는 외부 접근이 가능하도록
# 반드시 0.0.0.0에 바인딩합니다.
mcp = FastMCP(
    name="TodaysPetWalk",
    host="0.0.0.0",
    port=8000,
    stateless_http=True,
    json_response=True,
)


# -------------------------------------------------------------------
# 데모용 장소 데이터
# 추후 카카오맵·로컬 API를 연결하면 실시간 검색 결과로 교체합니다.
# -------------------------------------------------------------------
PLACE_DATA: dict[str, dict[str, Any]] = {
    "판교": {
        "walk_places": [
            {
                "name": "판교 화랑공원",
                "category": "공원",
                "reason": "산책로와 잔디 공간이 있어 반려견과 걷기 좋습니다.",
                "recommended_duration": "약 40분",
                "caution": "자전거 이용자가 있을 수 있으므로 리드줄을 짧게 유지하세요.",
            },
            {
                "name": "운중천 산책로",
                "category": "하천 산책로",
                "reason": "평탄한 보행로가 이어져 가벼운 산책에 적합합니다.",
                "recommended_duration": "약 30분",
                "caution": "비가 온 뒤에는 일부 구간이 미끄러울 수 있습니다.",
            },
        ],
        "indoor_rest_places": [
            {
                "name": "판교 반려동물 동반 실내 휴식 공간",
                "category": "반려동물 동반 카페",
                "reason": "더위, 추위 또는 비를 피하면서 반려견과 쉴 수 있습니다.",
                "notice": "실제 방문 전 반려동물 동반 가능 여부와 운영시간을 확인하세요.",
            }
        ],
        "animal_hospitals": [
            {
                "name": "판교 인근 동물병원",
                "category": "동물병원",
                "reason": "산책 중 발생할 수 있는 부상이나 이상 증상에 대비하기 좋습니다.",
                "notice": "진료시간과 응급진료 가능 여부를 방문 전에 확인하세요.",
            }
        ],
    },
    "강남": {
        "walk_places": [
            {
                "name": "양재천 산책로",
                "category": "하천 산책로",
                "reason": "보행로가 길게 이어져 반려견과 충분히 산책하기 좋습니다.",
                "recommended_duration": "약 40분",
                "caution": "사람과 자전거 이용자가 많을 수 있으므로 리드줄을 유지하세요.",
            }
        ],
        "indoor_rest_places": [
            {
                "name": "강남 반려동물 동반 실내 휴식 공간",
                "category": "반려동물 동반 카페",
                "reason": "도심 산책 중 반려견과 잠시 쉬어가기 좋습니다.",
                "notice": "입장 조건과 반려동물 크기 제한을 미리 확인하세요.",
            }
        ],
        "animal_hospitals": [
            {
                "name": "강남 인근 동물병원",
                "category": "동물병원",
                "reason": "산책 중 응급상황이나 건강 이상에 대비할 수 있습니다.",
                "notice": "야간 및 응급진료 여부를 미리 확인하세요.",
            }
        ],
    },
    "개포": {
        "walk_places": [
            {
                "name": "개포 근린공원",
                "category": "공원",
                "reason": "주거지역과 가까우며 짧고 편안한 산책에 적합합니다.",
                "recommended_duration": "약 30분",
                "caution": "어린이와 주민이 많을 수 있으므로 반려견을 가까이 통제하세요.",
            }
        ],
        "indoor_rest_places": [
            {
                "name": "개포 반려동물 동반 실내 휴식 공간",
                "category": "반려동물 동반 카페",
                "reason": "산책 후 반려견과 함께 실내에서 휴식하기 좋습니다.",
                "notice": "방문 전 반려동물 동반 정책을 확인하세요.",
            }
        ],
        "animal_hospitals": [
            {
                "name": "개포 인근 동물병원",
                "category": "동물병원",
                "reason": "산책 중 발생할 수 있는 돌발상황에 대비할 수 있습니다.",
                "notice": "진료시간과 주차 가능 여부를 확인하세요.",
            }
        ],
    },
}


def normalize_location(location: str) -> str:
    """
    사용자가 입력한 지역명을 데모 데이터의 지역 키로 변환합니다.

    예:
        판교역 -> 판교
        강남구 -> 강남
        개포동 -> 개포
    """

    cleaned_location = location.strip()

    for supported_location in PLACE_DATA:
        if supported_location in cleaned_location:
            return supported_location

    return cleaned_location


def get_location_data(location: str) -> tuple[str, dict[str, Any] | None]:
    """정규화한 지역명과 해당 지역 데이터를 반환합니다."""

    normalized_location = normalize_location(location)
    location_data = PLACE_DATA.get(normalized_location)

    return normalized_location, location_data


@mcp.tool(
    name="check_server",
    description=(
        "Checks whether the Today's Pet Walk MCP server is running normally. "
        "Use this tool only to verify the MCP server connection."
    ),
    annotations=ToolAnnotations(
        title="Check Today's Pet Walk Server",
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    ),
)
def check_server() -> dict[str, str]:
    """MCP 서버의 정상 작동 여부를 확인합니다."""

    return {
        "status": "online",
        "service": "Today's Pet Walk",
        "message": "Today's Pet Walk MCP server is operating normally.",
    }


@mcp.tool(
    name="recommend_walk",
    description=(
        "Recommends a dog-walking place for a requested location. "
        "Use the dog's name and location to return a structured walking plan, "
        "including the recommended place, reason, duration, and safety caution."
    ),
    annotations=ToolAnnotations(
        title="Recommend a Dog Walk",
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    ),
)
def recommend_walk(
    dog_name: str,
    location: str,
) -> dict[str, Any]:
    """
    반려견 이름과 지역을 기반으로 산책 장소를 추천합니다.

    Args:
        dog_name: 반려견 이름
        location: 산책을 원하는 지역
    """

    normalized_location, location_data = get_location_data(location)

    if location_data is None:
        return {
            "status": "location_not_supported",
            "dog_name": dog_name,
            "requested_location": location,
            "message": (
                f"현재 데모 버전에서는 {location}의 장소 데이터가 준비되지 않았습니다."
            ),
            "supported_locations": list(PLACE_DATA.keys()),
        }

    recommended_place = location_data["walk_places"][0]

    return {
        "status": "success",
        "dog_name": dog_name,
        "location": normalized_location,
        "recommendation": recommended_place,
        "summary": (
            f"{dog_name}와 함께 {recommended_place['name']}에서 "
            f"{recommended_place['recommended_duration']} 정도 산책하는 것을 추천합니다."
        ),
        "data_notice": (
            "현재 결과는 공모전 데모용 데이터입니다. "
            "추후 실시간 장소 검색 API로 교체할 예정입니다."
        ),
    }


@mcp.tool(
    name="find_pet_friendly_rest_place",
    description=(
        "Finds a pet-friendly indoor rest place near the requested location. "
        "Use this tool when the user needs an indoor place to rest with a dog "
        "because of rain, heat, cold, fatigue, or a break during a walk."
    ),
    annotations=ToolAnnotations(
        title="Find a Pet-Friendly Indoor Rest Place",
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    ),
)
def find_pet_friendly_rest_place(
    dog_name: str,
    location: str,
) -> dict[str, Any]:
    """
    산책 중 반려견과 쉴 수 있는 실내 장소를 안내합니다.

    Args:
        dog_name: 반려견 이름
        location: 실내 휴식 장소를 찾을 지역
    """

    normalized_location, location_data = get_location_data(location)

    if location_data is None:
        return {
            "status": "location_not_supported",
            "dog_name": dog_name,
            "requested_location": location,
            "message": (
                f"현재 데모 버전에서는 {location}의 실내 휴식 장소 데이터가 "
                "준비되지 않았습니다."
            ),
            "supported_locations": list(PLACE_DATA.keys()),
        }

    rest_place = location_data["indoor_rest_places"][0]

    return {
        "status": "success",
        "dog_name": dog_name,
        "location": normalized_location,
        "rest_place": rest_place,
        "summary": (
            f"{dog_name}와 산책 중 휴식이 필요하면 "
            f"{rest_place['name']}을 확인해보세요."
        ),
        "verification_required": True,
    }


@mcp.tool(
    name="find_nearby_animal_hospital",
    description=(
        "Finds an animal hospital near the requested walking location. "
        "Use this tool to help the user prepare for injuries, abnormal symptoms, "
        "or emergencies that may occur during a dog walk."
    ),
    annotations=ToolAnnotations(
        title="Find a Nearby Animal Hospital",
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    ),
)
def find_nearby_animal_hospital(
    dog_name: str,
    location: str,
) -> dict[str, Any]:
    """
    산책 지역 인근의 동물병원을 안내합니다.

    Args:
        dog_name: 반려견 이름
        location: 동물병원을 찾을 지역
    """

    normalized_location, location_data = get_location_data(location)

    if location_data is None:
        return {
            "status": "location_not_supported",
            "dog_name": dog_name,
            "requested_location": location,
            "message": (
                f"현재 데모 버전에서는 {location}의 동물병원 데이터가 "
                "준비되지 않았습니다."
            ),
            "supported_locations": list(PLACE_DATA.keys()),
        }

    animal_hospital = location_data["animal_hospitals"][0]

    return {
        "status": "success",
        "dog_name": dog_name,
        "location": normalized_location,
        "animal_hospital": animal_hospital,
        "summary": (
            f"{dog_name}의 산책 중 응급상황에 대비해 "
            f"{animal_hospital['name']}의 위치와 진료시간을 확인해두세요."
        ),
        "emergency_guidance": (
            "출혈, 호흡곤란, 의식 저하, 반복적인 구토 또는 보행 불가 증상이 있으면 "
            "산책을 중단하고 즉시 가까운 동물병원에 연락하세요."
        ),
        "verification_required": True,
    }


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
