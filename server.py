import math
import os
from typing import Any

import requests
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

SERVICE_NAME = "오늘의 산책"
SERVER_PORT = int(os.getenv("PORT", "8000"))
REQUEST_TIMEOUT_SECONDS = 10
KAKAO_LOCAL_KEYWORD_URL = "https://dapi.kakao.com/v2/local/search/keyword.json"
OPEN_METEO_FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

mcp = FastMCP(
    name="TodaysPetWalk",
    host="0.0.0.0",
    port=SERVER_PORT,
    stateless_http=True,
    json_response=True,
)

class ExternalAPIError(RuntimeError):
    pass

def kakao_headers() -> dict[str, str]:
    api_key = os.getenv("KAKAO_REST_API_KEY", "").strip()
    if not api_key:
        raise ExternalAPIError("KAKAO_REST_API_KEY 시크릿이 설정되지 않았습니다.")
    return {"Authorization": f"KakaoAK {api_key}"}

def request_json(url: str, *, headers=None, params=None) -> dict[str, Any]:
    try:
        response = requests.get(url, headers=headers, params=params, timeout=REQUEST_TIMEOUT_SECONDS)
        response.raise_for_status()
        data = response.json()
    except requests.Timeout as exc:
        raise ExternalAPIError("외부 데이터 제공처의 응답 시간이 초과되었습니다.") from exc
    except requests.RequestException as exc:
        raise ExternalAPIError(f"외부 데이터 조회에 실패했습니다: {exc}") from exc
    except ValueError as exc:
        raise ExternalAPIError("외부 데이터 제공처가 올바른 JSON을 반환하지 않았습니다.") from exc
    if not isinstance(data, dict):
        raise ExternalAPIError("외부 API 응답 형식이 예상과 다릅니다.")
    return data

def search_kakao_places(query: str, *, longitude=None, latitude=None, radius_m=None, size=5, sort="distance"):
    params: dict[str, Any] = {"query": query, "size": max(1, min(size, 15))}
    if longitude is not None and latitude is not None:
        params.update({"x": longitude, "y": latitude, "sort": sort})
    if radius_m is not None and longitude is not None and latitude is not None:
        params["radius"] = max(1, min(radius_m, 20000))
    data = request_json(KAKAO_LOCAL_KEYWORD_URL, headers=kakao_headers(), params=params)
    docs = data.get("documents", [])
    return docs if isinstance(docs, list) else []

def resolve_place(place: str) -> dict[str, Any]:
    place = place.strip()
    if not place:
        raise ExternalAPIError("장소명을 입력해 주세요.")
    docs = search_kakao_places(place, size=1, sort="accuracy")
    if not docs:
        raise ExternalAPIError(f"'{place}'의 위치를 찾지 못했습니다.")
    item = docs[0]
    try:
        lat = float(item["y"])
        lon = float(item["x"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ExternalAPIError("검색된 장소 좌표를 해석하지 못했습니다.") from exc
    return {
        "name": item.get("place_name") or place,
        "address": item.get("road_address_name") or item.get("address_name") or "",
        "latitude": lat,
        "longitude": lon,
        "place_url": item.get("place_url") or "",
        "data_source": "Kakao Local API",
    }

def normalize_place_result(item: dict[str, Any], facility_type: str) -> dict[str, Any]:
    try:
        distance_m = int(float(str(item.get("distance") or "").strip()))
    except ValueError:
        distance_m = None
    try:
        lat = float(item["y"]) if item.get("y") else None
        lon = float(item["x"]) if item.get("x") else None
    except (TypeError, ValueError):
        lat, lon = None, None
    return {
        "type": facility_type,
        "name": item.get("place_name") or "",
        "category": item.get("category_name") or "",
        "distance_m": distance_m,
        "address": item.get("road_address_name") or item.get("address_name") or "",
        "phone": item.get("phone") or "",
        "latitude": lat,
        "longitude": lon,
        "place_url": item.get("place_url") or "",
        "data_source": "Kakao Local API",
    }

def search_nearby(*, query, facility_type, latitude, longitude, radius_m, size):
    docs = search_kakao_places(
        query,
        longitude=longitude,
        latitude=latitude,
        radius_m=radius_m,
        size=size,
    )
    results, seen = [], set()
    for item in docs:
        normalized = normalize_place_result(item, facility_type)
        if normalized["name"] and normalized["name"] not in seen:
            seen.add(normalized["name"])
            results.append(normalized)
    return results

def get_weather(latitude: float, longitude: float) -> dict[str, Any]:
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,apparent_temperature,precipitation,rain,weather_code,wind_speed_10m",
        "hourly": "precipitation_probability",
        "forecast_hours": 6,
        "timezone": "Asia/Seoul",
    }
    data = request_json(OPEN_METEO_FORECAST_URL, params=params)
    current = data.get("current", {}) if isinstance(data.get("current", {}), dict) else {}
    hourly = data.get("hourly", {}) if isinstance(data.get("hourly", {}), dict) else {}
    probs = []
    for value in hourly.get("precipitation_probability", []) if isinstance(hourly.get("precipitation_probability", []), list) else []:
        try:
            if value is not None:
                probs.append(int(value))
        except (TypeError, ValueError):
            pass
    return {
        "temperature_c": current.get("temperature_2m"),
        "apparent_temperature_c": current.get("apparent_temperature"),
        "precipitation_mm": current.get("precipitation"),
        "rain_mm": current.get("rain"),
        "wind_speed_kmh": current.get("wind_speed_10m"),
        "weather_code": current.get("weather_code"),
        "next_6h_max_rain_probability_percent": max(probs, default=0),
        "observed_at": current.get("time"),
        "data_source": "Open-Meteo Forecast API",
    }

def build_safety_advice(weather: dict[str, Any], duration_minutes: int) -> list[str]:
    advice = []
    apparent = weather.get("apparent_temperature_c")
    temperature = weather.get("temperature_c")
    rain_probability = weather.get("next_6h_max_rain_probability_percent", 0)
    wind_speed = weather.get("wind_speed_kmh")
    reference = apparent if isinstance(apparent, (int, float)) else temperature
    if isinstance(reference, (int, float)):
        if reference >= 30:
            advice.append("체감온도가 높습니다. 한낮을 피하고 물과 휴대용 그릇을 준비하세요.")
        elif reference >= 27:
            advice.append("더운 날씨입니다. 반려견의 헐떡임과 보행 속도를 자주 확인하세요.")
        elif reference <= 0:
            advice.append("기온이 낮습니다. 산책 시간을 줄이고 체온 저하를 확인하세요.")
    if isinstance(rain_probability, (int, float)) and rain_probability >= 50:
        advice.append("비 가능성이 높습니다. 우비, 수건, 발 세정용품을 준비하세요.")
    if isinstance(wind_speed, (int, float)) and wind_speed >= 30:
        advice.append("바람이 강합니다. 나무와 간판 주변을 피하고 리드줄을 짧게 유지하세요.")
    if duration_minutes >= 60:
        advice.append("장시간 산책입니다. 중간 휴식 지점과 별도 식수를 확보하세요.")
    return advice or ["현재 조건에서는 일반적인 산책이 가능해 보입니다. 리드줄, 배변봉투, 물을 준비하세요."]

def build_supply_recommendations(weather: dict[str, Any], duration_minutes: int):
    result = [{"item": "리드줄과 배변봉투", "reason": "안전하고 위생적인 산책을 위한 기본 준비물입니다."}]
    apparent = weather.get("apparent_temperature_c")
    rain_probability = weather.get("next_6h_max_rain_probability_percent", 0)
    if isinstance(apparent, (int, float)) and apparent >= 27:
        result.append({"item": "휴대용 물병과 접이식 그릇", "reason": "더운 날 수분 공급이 필요합니다."})
    if isinstance(rain_probability, (int, float)) and rain_probability >= 50:
        result.append({"item": "반려견 우비와 수건", "reason": "강수 가능성에 대비할 수 있습니다."})
    if duration_minutes >= 60 and not any(x["item"] == "휴대용 물병과 접이식 그릇" for x in result):
        result.append({"item": "휴대용 물병과 접이식 그릇", "reason": "장시간 산책 중 별도 식수를 확보하기 좋습니다."})
    return result

@mcp.tool(
    name="plan_pet_walk",
    description=(
        "오늘의 산책 서비스가 입력한 장소의 실제 좌표와 현재 날씨를 조회하고, "
        "주변의 실제 공원·산책로를 검색해 반려견 산책 계획, 안전 주의사항, "
        "준비물을 제공합니다."
    ),
    annotations=ToolAnnotations(
        title="오늘의 산책 - 실시간 산책 계획",
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=True,
    ),
)
def plan_pet_walk(dog_name: str, place: str, duration_minutes: int = 40) -> dict[str, Any]:
    dog_name, place = dog_name.strip(), place.strip()
    if not dog_name:
        return {"status": "invalid_request", "service": SERVICE_NAME, "message": "반려견 이름을 입력해 주세요."}
    if not place:
        return {"status": "invalid_request", "service": SERVICE_NAME, "message": "산책할 장소를 입력해 주세요."}
    duration = max(10, min(duration_minutes, 240))
    try:
        center = resolve_place(place)
        weather = get_weather(center["latitude"], center["longitude"])
        parks = search_nearby(
            query="공원 산책로",
            facility_type="walk_place",
            latitude=center["latitude"],
            longitude=center["longitude"],
            radius_m=3000,
            size=5,
        )
        return {
            "status": "success",
            "service": SERVICE_NAME,
            "dog_name": dog_name,
            "requested_place": place,
            "center": center,
            "weather": weather,
            "recommended_walk_places": parks[:5],
            "walk_plan": {
                "duration_minutes": duration,
                "safety_advice": build_safety_advice(weather, duration),
                "recommended_supplies": build_supply_recommendations(weather, duration),
            },
            "data_sources": ["Kakao Local API", "Open-Meteo Forecast API"],
            "notice": "날씨와 장소 정보는 실제 현장 상황과 다를 수 있습니다.",
        }
    except ExternalAPIError as exc:
        return {"status": "external_api_error", "service": SERVICE_NAME, "message": str(exc)}

@mcp.tool(
    name="find_nearby_facilities",
    description=(
        "오늘의 산책 서비스가 입력한 장소를 기준으로 카카오 로컬 API를 호출해 "
        "실제 동물병원, 공중화장실, 음수대를 거리순으로 찾습니다."
    ),
    annotations=ToolAnnotations(
        title="오늘의 산책 - 주변 편의시설 검색",
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=True,
    ),
)
def find_nearby_facilities(place: str, radius_m: int = 2000, max_results_per_type: int = 3) -> dict[str, Any]:
    radius = max(100, min(radius_m, 20000))
    size = max(1, min(max_results_per_type, 5))
    try:
        center = resolve_place(place)
        facilities = {}
        for facility_type, query in [
            ("animal_hospital", "동물병원"),
            ("public_toilet", "공중화장실"),
            ("drinking_fountain", "음수대"),
        ]:
            facilities[facility_type] = search_nearby(
                query=query,
                facility_type=facility_type,
                latitude=center["latitude"],
                longitude=center["longitude"],
                radius_m=radius,
                size=size,
            )
        return {
            "status": "success",
            "service": SERVICE_NAME,
            "center": center,
            "search_radius_m": radius,
            "facilities": facilities,
            "data_sources": ["Kakao Local API"],
            "notice": "운영시간과 개방 여부는 방문 전에 확인해 주세요.",
        }
    except ExternalAPIError as exc:
        return {"status": "external_api_error", "service": SERVICE_NAME, "message": str(exc)}

@mcp.tool(
    name="find_pet_friendly_rest_place",
    description=(
        "오늘의 산책 서비스가 입력한 장소 주변에서 카카오 로컬 API를 사용해 "
        "실제 반려동물 동반 카페와 실내 휴식 장소를 검색합니다."
    ),
    annotations=ToolAnnotations(
        title="오늘의 산책 - 반려동물 동반 휴식 장소",
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=True,
    ),
)
def find_pet_friendly_rest_place(place: str, radius_m: int = 3000, max_results: int = 5) -> dict[str, Any]:
    radius = max(100, min(radius_m, 20000))
    size = max(1, min(max_results, 10))
    try:
        center = resolve_place(place)
        combined, seen = [], set()
        for term in ["반려동물 동반 카페", "애견 동반 카페"]:
            for result in search_nearby(
                query=term,
                facility_type="pet_friendly_rest_place",
                latitude=center["latitude"],
                longitude=center["longitude"],
                radius_m=radius,
                size=size,
            ):
                if result["name"] not in seen:
                    seen.add(result["name"])
                    combined.append(result)
        combined.sort(key=lambda x: (x["distance_m"] is None, x["distance_m"] if x["distance_m"] is not None else math.inf))
        return {
            "status": "success",
            "service": SERVICE_NAME,
            "center": center,
            "search_radius_m": radius,
            "rest_places": combined[:size],
            "data_sources": ["Kakao Local API"],
            "verification_required": True,
            "notice": "반려동물 동반 정책과 운영시간은 방문 전에 확인해 주세요.",
        }
    except ExternalAPIError as exc:
        return {"status": "external_api_error", "service": SERVICE_NAME, "message": str(exc)}

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
