<<<<<<< Updated upstream
from typing import Any, Dict, Optional, Tuple

=======
import math
import os
from typing import Any

import requests
>>>>>>> Stashed changes
from mcp.server.fastmcp import FastMCP


<<<<<<< Updated upstream
# PlayMCP 배포 환경에서는 외부 접근이 가능하도록
# 반드시 0.0.0.0에 바인딩합니다.
=======
KAKAO_LOCAL_URL = "https://dapi.kakao.com/v2/local/search/keyword.json"
OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
REQUEST_TIMEOUT_SECONDS = 10

>>>>>>> Stashed changes
mcp = FastMCP(
    name="TodaysPetWalk",
    host="0.0.0.0",
    port=int(os.getenv("PORT", "8000")),
)


<<<<<<< Updated upstream
# ---------------------------------------------------------
# 공모전 데모용 장소 데이터
# 추후 카카오맵 또는 장소 검색 API 연결 시 교체할 수 있습니다.
# ---------------------------------------------------------
PLACE_DATA: Dict[str, Dict[str, Any]] = {
    "판교": {
        "walk_places": [
            {
                "name": "판교 화랑공원",
                "category": "공원",
                "reason": "산책로와 잔디 공간이 있어 반려견과 걷기 좋습니다.",
                "recommended_duration": "약 40분",
                "caution": (
                    "자전거 이용자가 있을 수 있으므로 "
                    "리드줄을 짧게 유지하세요."
                ),
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
                "reason": (
                    "더위, 추위 또는 비를 피하면서 "
                    "반려견과 함께 쉴 수 있습니다."
                ),
                "notice": (
                    "실제 방문 전 반려동물 동반 가능 여부와 "
                    "운영시간을 확인하세요."
                ),
            }
        ],
        "animal_hospitals": [
            {
                "name": "판교 인근 동물병원",
                "category": "동물병원",
                "reason": (
                    "산책 중 발생할 수 있는 부상이나 "
                    "이상 증상에 대비할 수 있습니다."
                ),
                "notice": (
                    "진료시간과 응급진료 가능 여부를 "
                    "방문 전에 확인하세요."
                ),
            }
        ],
    },
    "강남": {
        "walk_places": [
            {
                "name": "양재천 산책로",
                "category": "하천 산책로",
                "reason": (
                    "보행로가 길게 이어져 "
                    "반려견과 충분히 산책하기 좋습니다."
                ),
                "recommended_duration": "약 40분",
                "caution": (
                    "보행자와 자전거 이용자가 많을 수 있으므로 "
                    "리드줄을 유지하세요."
                ),
            }
        ],
        "indoor_rest_places": [
            {
                "name": "강남 반려동물 동반 실내 휴식 공간",
                "category": "반려동물 동반 카페",
                "reason": "도심 산책 중 반려견과 잠시 쉬어가기 좋습니다.",
                "notice": (
                    "입장 조건과 반려동물 크기 제한을 "
                    "미리 확인하세요."
                ),
            }
        ],
        "animal_hospitals": [
            {
                "name": "강남 인근 동물병원",
                "category": "동물병원",
                "reason": (
                    "산책 중 응급상황이나 "
                    "건강 이상에 대비할 수 있습니다."
                ),
                "notice": "야간 및 응급진료 여부를 미리 확인하세요.",
            }
        ],
    },
    "개포": {
        "walk_places": [
            {
                "name": "개포 근린공원",
                "category": "공원",
                "reason": (
                    "주거지역과 가까우며 "
                    "짧고 편안한 산책에 적합합니다."
                ),
                "recommended_duration": "약 30분",
                "caution": (
                    "어린이와 주민이 많을 수 있으므로 "
                    "반려견을 가까이 통제하세요."
                ),
            }
        ],
        "indoor_rest_places": [
            {
                "name": "개포 반려동물 동반 실내 휴식 공간",
                "category": "반려동물 동반 카페",
                "reason": (
                    "산책 후 반려견과 함께 "
                    "실내에서 휴식하기 좋습니다."
                ),
                "notice": "방문 전 반려동물 동반 정책을 확인하세요.",
            }
        ],
        "animal_hospitals": [
            {
                "name": "개포 인근 동물병원",
                "category": "동물병원",
                "reason": (
                    "산책 중 발생할 수 있는 "
                    "돌발상황에 대비할 수 있습니다."
                ),
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


def get_location_data(
    location: str,
) -> Tuple[str, Optional[Dict[str, Any]]]:
    """정규화한 지역명과 해당 지역 데이터를 반환합니다."""

    normalized_location = normalize_location(location)
    location_data = PLACE_DATA.get(normalized_location)

    return normalized_location, location_data


def build_unsupported_location_response(
    dog_name: str,
    location: str,
    feature_name: str,
) -> Dict[str, Any]:
    """지원하지 않는 지역에 대한 공통 응답을 생성합니다."""

    return {
        "status": "location_not_supported",
        "dog_name": dog_name,
        "requested_location": location,
        "message": (
            "현재 데모 버전에서는 "
            + location
            + "의 "
            + feature_name
            + " 데이터가 준비되지 않았습니다."
        ),
        "supported_locations": list(PLACE_DATA.keys()),
    }


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
def check_server() -> Dict[str, str]:
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
) -> Dict[str, Any]:
    """
    반려견 이름과 지역을 기반으로 산책 장소를 추천합니다.

    Args:
        dog_name: 반려견 이름
        location: 산책을 원하는 지역
    """

    normalized_location, location_data = get_location_data(location)

    if location_data is None:
        return build_unsupported_location_response(
            dog_name=dog_name,
            location=location,
            feature_name="산책 장소",
        )

    recommended_place = location_data["walk_places"][0]

    return {
        "status": "success",
        "dog_name": dog_name,
        "location": normalized_location,
        "recommendation": recommended_place,
        "summary": (
            dog_name
            + "와 함께 "
            + recommended_place["name"]
            + "에서 "
            + recommended_place["recommended_duration"]
            + " 정도 산책하는 것을 추천합니다."
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
) -> Dict[str, Any]:
    """
    산책 중 반려견과 쉴 수 있는 실내 장소를 안내합니다.

    Args:
        dog_name: 반려견 이름
        location: 실내 휴식 장소를 찾을 지역
    """

    normalized_location, location_data = get_location_data(location)

    if location_data is None:
        return build_unsupported_location_response(
            dog_name=dog_name,
            location=location,
            feature_name="실내 휴식 장소",
        )

    rest_place = location_data["indoor_rest_places"][0]

    return {
        "status": "success",
        "dog_name": dog_name,
        "location": normalized_location,
        "rest_place": rest_place,
        "summary": (
            dog_name
            + "와 산책 중 휴식이 필요하면 "
            + rest_place["name"]
            + "을 확인해보세요."
        ),
        "verification_required": True,
        "data_notice": (
            "현재 결과는 공모전 데모용 데이터입니다. "
            "방문 전 실제 반려동물 동반 가능 여부를 확인해야 합니다."
        ),
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
) -> Dict[str, Any]:
    """
    산책 지역 인근의 동물병원을 안내합니다.

    Args:
        dog_name: 반려견 이름
        location: 동물병원을 찾을 지역
    """

    normalized_location, location_data = get_location_data(location)

    if location_data is None:
        return build_unsupported_location_response(
            dog_name=dog_name,
            location=location,
            feature_name="동물병원",
        )

    animal_hospital = location_data["animal_hospitals"][0]

    return {
        "status": "success",
        "dog_name": dog_name,
        "location": normalized_location,
        "animal_hospital": animal_hospital,
        "summary": (
            dog_name
            + "의 산책 중 응급상황에 대비해 "
            + animal_hospital["name"]
            + "의 위치와 진료시간을 확인해두세요."
        ),
        "emergency_guidance": (
            "출혈, 호흡곤란, 의식 저하, 반복적인 구토 또는 "
            "보행 불가 증상이 있으면 산책을 중단하고 "
            "즉시 가까운 동물병원에 연락하세요."
        ),
        "verification_required": True,
        "data_notice": (
            "현재 결과는 공모전 데모용 데이터입니다. "
            "실제 진료 가능 여부와 운영시간을 반드시 확인해야 합니다."
        ),
    }
=======
class ExternalAPIError(RuntimeError):
    """외부 API 호출 실패를 사용자에게 안전하게 전달하기 위한 예외."""


def _kakao_headers() -> dict[str, str]:
    api_key = os.getenv("KAKAO_REST_API_KEY", "").strip()
    if not api_key:
        raise ExternalAPIError(
            "KAKAO_REST_API_KEY 환경변수가 설정되지 않았습니다."
        )
    return {"Authorization": f"KakaoAK {api_key}"}


def _request_json(
    url: str,
    *,
    headers: dict[str, str] | None = None,
    params: dict[str, Any] | None = None,
) -> dict[str, Any]:
    try:
        response = requests.get(
            url,
            headers=headers,
            params=params,
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        data = response.json()
    except requests.Timeout as exc:
        raise ExternalAPIError("외부 API 응답 시간이 초과되었습니다.") from exc
    except requests.RequestException as exc:
        raise ExternalAPIError(f"외부 API 호출에 실패했습니다: {exc}") from exc
    except ValueError as exc:
        raise ExternalAPIError("외부 API가 올바른 JSON을 반환하지 않았습니다.") from exc

    if not isinstance(data, dict):
        raise ExternalAPIError("외부 API 응답 형식이 예상과 다릅니다.")
    return data


def _search_kakao_keyword(
    query: str,
    *,
    longitude: float | None = None,
    latitude: float | None = None,
    radius_m: int | None = None,
    size: int = 5,
    sort: str = "distance",
) -> list[dict[str, Any]]:
    params: dict[str, Any] = {
        "query": query,
        "size": max(1, min(size, 15)),
    }

    if longitude is not None and latitude is not None:
        params["x"] = longitude
        params["y"] = latitude
        params["sort"] = sort

    if radius_m is not None and longitude is not None and latitude is not None:
        params["radius"] = max(1, min(radius_m, 20000))

    data = _request_json(
        KAKAO_LOCAL_URL,
        headers=_kakao_headers(),
        params=params,
    )
    documents = data.get("documents", [])
    return documents if isinstance(documents, list) else []


def _resolve_place(place: str) -> dict[str, Any]:
    documents = _search_kakao_keyword(place, size=1, sort="accuracy")
    if not documents:
        raise ExternalAPIError(
            f"'{place}'의 위치를 찾지 못했습니다. 더 구체적인 장소명을 입력해 주세요."
        )

    item = documents[0]
    try:
        longitude = float(item["x"])
        latitude = float(item["y"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ExternalAPIError("장소 좌표를 해석하지 못했습니다.") from exc

    return {
        "name": item.get("place_name") or place,
        "address": item.get("road_address_name") or item.get("address_name") or "",
        "latitude": latitude,
        "longitude": longitude,
        "place_url": item.get("place_url") or "",
    }


def _get_weather(latitude: float, longitude: float) -> dict[str, Any]:
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": ",".join(
            [
                "temperature_2m",
                "apparent_temperature",
                "precipitation",
                "rain",
                "weather_code",
                "wind_speed_10m",
            ]
        ),
        "hourly": "precipitation_probability",
        "forecast_hours": 6,
        "timezone": "Asia/Seoul",
    }
    data = _request_json(OPEN_METEO_URL, params=params)
    current = data.get("current", {})
    hourly = data.get("hourly", {})

    probabilities = hourly.get("precipitation_probability", [])
    next_6h_rain_probability = max(
        [int(value) for value in probabilities if value is not None],
        default=0,
    )

    return {
        "temperature_c": current.get("temperature_2m"),
        "apparent_temperature_c": current.get("apparent_temperature"),
        "precipitation_mm": current.get("precipitation"),
        "rain_mm": current.get("rain"),
        "wind_speed_kmh": current.get("wind_speed_10m"),
        "weather_code": current.get("weather_code"),
        "next_6h_max_rain_probability_percent": next_6h_rain_probability,
        "observed_at": current.get("time"),
    }


def _normalize_facility(
    item: dict[str, Any],
    facility_type: str,
) -> dict[str, Any]:
    distance_text = str(item.get("distance") or "").strip()
    try:
        distance_m = int(float(distance_text))
    except ValueError:
        distance_m = None

    return {
        "type": facility_type,
        "name": item.get("place_name") or "",
        "distance_m": distance_m,
        "address": item.get("road_address_name") or item.get("address_name") or "",
        "phone": item.get("phone") or "",
        "latitude": float(item["y"]) if item.get("y") else None,
        "longitude": float(item["x"]) if item.get("x") else None,
        "place_url": item.get("place_url") or "",
    }


def _find_facilities_by_coordinates(
    latitude: float,
    longitude: float,
    radius_m: int,
    max_results_per_type: int,
) -> list[dict[str, Any]]:
    keywords = {
        "public_toilet": "공중화장실",
        "drinking_fountain": "음수대",
        "animal_hospital": "동물병원",
        "pet_friendly_place": "반려동물 동반",
    }

    results: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()

    for facility_type, keyword in keywords.items():
        documents = _search_kakao_keyword(
            keyword,
            longitude=longitude,
            latitude=latitude,
            radius_m=radius_m,
            size=max_results_per_type,
        )
        for item in documents:
            normalized = _normalize_facility(item, facility_type)
            dedupe_key = (facility_type, normalized["name"])
            if not normalized["name"] or dedupe_key in seen:
                continue
            seen.add(dedupe_key)
            results.append(normalized)

    return sorted(
        results,
        key=lambda item: (
            item["distance_m"] is None,
            item["distance_m"] if item["distance_m"] is not None else math.inf,
        ),
    )
>>>>>>> Stashed changes


def _build_safety_advice(
    weather: dict[str, Any],
    duration_minutes: int,
    dog_size: str,
) -> list[str]:
    advice: list[str] = []

    temperature = weather.get("temperature_c")
    apparent = weather.get("apparent_temperature_c")
    rain_probability = weather.get("next_6h_max_rain_probability_percent", 0)
    wind_speed = weather.get("wind_speed_kmh")

    reference_temperature = apparent if isinstance(apparent, (int, float)) else temperature

    if isinstance(reference_temperature, (int, float)):
        if reference_temperature >= 30:
            advice.append(
                "체감온도가 높습니다. 그늘 위주로 짧게 걷고 물과 휴대용 그릇을 준비하세요."
            )
        elif reference_temperature <= 0:
            advice.append(
                "기온이 낮습니다. 짧은 산책을 권장하며 발바닥과 체온 저하를 확인하세요."
            )

    if isinstance(rain_probability, (int, float)) and rain_probability >= 50:
        advice.append(
            "향후 6시간 내 비 가능성이 있습니다. 우비와 발 세정용품을 준비하세요."
        )

    if isinstance(wind_speed, (int, float)) and wind_speed >= 30:
        advice.append(
            "바람이 강합니다. 나무·간판 주변을 피하고 리드줄을 짧게 유지하세요."
        )

    if duration_minutes >= 60:
        advice.append(
            "장시간 산책입니다. 중간 휴식 지점과 음수대 또는 별도 식수를 확보하세요."
        )

    if dog_size == "small" and duration_minutes >= 45:
        advice.append(
            "소형견에게 긴 산책일 수 있습니다. 피로 신호가 보이면 즉시 쉬어 주세요."
        )

    if not advice:
        advice.append(
            "현재 조건은 일반적인 산책이 가능해 보입니다. 리드줄과 배변봉투를 준비하세요."
        )

    advice.append(
        "음수대는 사람용 시설일 수 있으므로 반려견이 수도꼭지에 직접 접촉하지 않게 해 주세요."
    )
    return advice


def _build_supply_recommendations(
    weather: dict[str, Any],
    duration_minutes: int,
) -> list[dict[str, str]]:
    supplies: list[dict[str, str]] = [
        {
            "item": "배변봉투",
            "reason": "기본 산책 위생용품입니다.",
            "musinsa_search_keyword": "반려견 배변봉투",
        }
    ]

    apparent = weather.get("apparent_temperature_c")
    rain_probability = weather.get("next_6h_max_rain_probability_percent", 0)

    if isinstance(apparent, (int, float)) and apparent >= 27:
        supplies.extend(
            [
                {
                    "item": "휴대용 반려견 물병",
                    "reason": "더운 날 산책 중 수분 공급이 필요합니다.",
                    "musinsa_search_keyword": "반려견 휴대용 물병",
                },
                {
                    "item": "쿨링 용품",
                    "reason": "체감온도가 높은 환경에서 열 부담을 줄이는 데 도움이 됩니다.",
                    "musinsa_search_keyword": "반려견 쿨링",
                },
            ]
        )

    if isinstance(rain_probability, (int, float)) and rain_probability >= 50:
        supplies.append(
            {
                "item": "반려견 우비",
                "reason": "비 예보에 대비해 털과 체온을 보호할 수 있습니다.",
                "musinsa_search_keyword": "반려견 우비",
            }
        )

    if duration_minutes >= 60 and not any(
        item["item"] == "휴대용 반려견 물병" for item in supplies
    ):
        supplies.append(
            {
                "item": "휴대용 반려견 물병",
                "reason": "장시간 산책 중 별도 식수를 확보하는 편이 안전합니다.",
                "musinsa_search_keyword": "반려견 휴대용 물병",
            }
        )

    return supplies


@mcp.tool()
def find_nearby_facilities(
    place: str,
    radius_m: int = 1500,
    max_results_per_type: int = 3,
) -> dict[str, Any]:
    """
    입력한 장소 주변의 공중화장실, 음수대, 동물병원,
    반려동물 동반 장소를 거리순으로 검색합니다.

    Args:
        place: 기준 장소명. 예: 서울숲, 양재시민의숲
        radius_m: 검색 반경(미터). 1~20,000
        max_results_per_type: 시설 유형별 최대 결과 수. 1~15
    """
    try:
        resolved = _resolve_place(place)
        facilities = _find_facilities_by_coordinates(
            latitude=resolved["latitude"],
            longitude=resolved["longitude"],
            radius_m=max(1, min(radius_m, 20000)),
            max_results_per_type=max(1, min(max_results_per_type, 15)),
        )
        return {
            "success": True,
            "center": resolved,
            "radius_m": radius_m,
            "facilities": facilities,
            "notice": (
                "검색 결과는 카카오 로컬 장소 데이터 기준이며, "
                "운영시간·반려동물 동반 가능 여부는 방문 전에 확인해야 합니다."
            ),
        }
    except ExternalAPIError as exc:
        return {"success": False, "error": str(exc)}


@mcp.tool()
def plan_pet_walk(
    place: str,
    duration_minutes: int = 60,
    dog_size: str = "medium",
    radius_m: int = 1500,
) -> dict[str, Any]:
    """
    장소의 현재 날씨와 주변 편의시설을 조회해 반려견 산책 계획을 만듭니다.

    Args:
        place: 산책 장소명. 예: 서울숲, 반포한강공원
        duration_minutes: 예상 산책 시간(분). 10~240
        dog_size: 반려견 크기. small, medium, large
        radius_m: 주변 시설 검색 반경(미터). 1~20,000
    """
    normalized_size = dog_size.strip().lower()
    if normalized_size not in {"small", "medium", "large"}:
        return {
            "success": False,
            "error": "dog_size는 small, medium, large 중 하나여야 합니다.",
        }

    duration = max(10, min(duration_minutes, 240))
    radius = max(1, min(radius_m, 20000))

    try:
        resolved = _resolve_place(place)
        weather = _get_weather(
            latitude=resolved["latitude"],
            longitude=resolved["longitude"],
        )
        facilities = _find_facilities_by_coordinates(
            latitude=resolved["latitude"],
            longitude=resolved["longitude"],
            radius_m=radius,
            max_results_per_type=3,
        )
        safety_advice = _build_safety_advice(
            weather=weather,
            duration_minutes=duration,
            dog_size=normalized_size,
        )
        supplies = _build_supply_recommendations(
            weather=weather,
            duration_minutes=duration,
        )

        return {
            "success": True,
            "place": resolved,
            "walk_plan": {
                "duration_minutes": duration,
                "dog_size": normalized_size,
                "search_radius_m": radius,
            },
            "weather": weather,
            "safety_advice": safety_advice,
            "nearby_facilities": facilities,
            "recommended_supplies": supplies,
            "data_notice": (
                "날씨는 Open-Meteo, 장소는 카카오 로컬 검색 결과를 사용합니다. "
                "실제 영업·개방 상태와 반려동물 동반 정책은 현장에서 달라질 수 있습니다."
            ),
        }
    except ExternalAPIError as exc:
        return {"success": False, "error": str(exc)}


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
