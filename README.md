# 오늘의 산책 (TodaysPetWalk)

반려견 산책 장소의 날씨와 주변 편의시설을 조회하고, 산책 안전수칙과 준비물을 추천하는 MCP 서버입니다.

## 예선 제출 범위

- 장소명으로 좌표 확인
- 현재 날씨 및 향후 6시간 강수 가능성 확인
- 주변 공중화장실·음수대·동물병원·반려동물 동반 장소 검색
- 기온·비·바람·산책 시간에 따른 안전 안내
- 상황별 반려용품 추천 키워드 제공
- 외부 API 오류와 키 누락 예외 처리

## MCP 툴

### `plan_pet_walk`

날씨·편의시설·안전수칙·준비물을 한 번에 반환합니다.

예시 입력:

```json
{
  "place": "서울숲",
  "duration_minutes": 60,
  "dog_size": "medium",
  "radius_m": 1500
}
```

### `find_nearby_facilities`

입력한 장소 주변의 편의시설만 거리순으로 검색합니다.

예시 입력:

```json
{
  "place": "양재시민의숲",
  "radius_m": 2000,
  "max_results_per_type": 3
}
```

## 환경변수

카카오 REST API 키를 코드에 직접 입력하지 않습니다.

```bash
cp .env.example .env
```

`.env` 파일 또는 PlayMCP 환경변수에 아래 값을 설정합니다.

```env
KAKAO_REST_API_KEY=발급받은_REST_API_키
PORT=8000
```

> `.env`는 `.gitignore`에 포함되어 있으므로 깃에 커밋하지 않습니다.

## 설치 및 실행

```bash
pip install -r requirements.txt
python server.py
```

서버는 PlayMCP 배포를 위해 `0.0.0.0`에 바인딩되며 기본 포트는 `8000`입니다.

## 제출 전 테스트 질의

```text
서울숲에서 중형견과 1시간 산책하려고 해.
현재 날씨와 주변 음수대, 공중화장실, 동물병원을 포함해 준비물을 추천해줘.
```

```text
반포한강공원 주변 2km 안의 공중화장실과 동물병원을 찾아줘.
```

## 데이터 및 제한사항

- 장소 검색: 카카오 로컬 REST API
- 날씨: Open-Meteo Forecast API
- 검색 결과의 운영시간, 개방 여부, 반려동물 동반 정책은 실제 현장과 다를 수 있습니다.
- 음수대는 사람용 시설일 수 있으므로 반려견이 수도꼭지에 직접 접촉하지 않도록 안내합니다.
- 무신사 상품의 가격·재고를 직접 수집하지 않고 필요한 상품군의 검색 키워드만 제공합니다.

## Git 업데이트

```bash
git add server.py requirements.txt .env.example .gitignore README.md
git commit -m "feat: connect weather and nearby facility APIs"
git push
```
