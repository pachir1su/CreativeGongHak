# CreativeGongHak - Weather Report Project
# GitHub Repository: https://github.com/pachir1su/CreativeGongHak
#
# 4주차 개인 프로젝트: Open-Meteo API를 활용한 날씨 리포트

import requests

GEOCODING_API = "https://geocoding-api.open-meteo.com/v1/search"


def geocode_city(city: str) -> dict:
    """도시 이름을 위도/경도로 변환합니다."""
    params = {
        "name": city,
        "count": 1,
        "language": "ko",
        "format": "json",
    }
    response = requests.get(GEOCODING_API, params=params, timeout=10)
    response.raise_for_status()

    results = response.json().get("results", [])
    if not results:
        raise ValueError(f"'{city}' 지역을 찾을 수 없습니다.")

    place = results[0]
    return {
        "name": place.get("name", city),
        "admin1": place.get("admin1", ""),
        "country": place.get("country", ""),
        "latitude": place["latitude"],
        "longitude": place["longitude"],
        "timezone": place.get("timezone", "auto"),
    }


def main():
    print("☀️ 날씨 리포트 (Open-Meteo API)")
    print("오전 6시, 오후 3시 기준으로 3일간 날씨를 제공합니다.")
    print("-" * 48)

    city = input("날씨를 확인할 지역을 입력하세요 (기본값: 서울): ").strip() or "서울"
    location = geocode_city(city)

    print(
        f"📍 {location['name']} "
        f"(위도: {location['latitude']:.4f}, 경도: {location['longitude']:.4f})"
    )


if __name__ == "__main__":
    try:
        main()
    except (requests.RequestException, ValueError) as exc:
        print(f"오류: {exc}")
