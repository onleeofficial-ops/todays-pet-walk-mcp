# 오늘의 산책 MCP

실제 Kakao Local API와 Open-Meteo Forecast API를 연결한 예선용 MCP입니다.

## Tools
- plan_pet_walk
- find_nearby_facilities
- find_pet_friendly_rest_place

## PlayMCP 시크릿
KAKAO_REST_API_KEY

## 컨테이너 포트
8000

## 검사
python -m py_compile server.py

## Git 반영
git add server.py requirements.txt Dockerfile .dockerignore .gitignore .env.example README.md
git commit -m "feat: connect real location and weather APIs"
git push origin main
