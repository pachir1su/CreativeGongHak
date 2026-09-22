# CreativeGongHak - Weather Report Project
# GitHub Repository: https://github.com/pachir1su/CreativeGongHak
#
# 4주차 개인 프로젝트: Open-Meteo API를 활용한 날씨 리포트

from datetime import datetime, timedelta

import requests

GEOCODING_API = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_API = "https://api.open-meteo.com/v1/forecast"
TARGET_HOURS = (6, 15)


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


def fetch_weather(latitude: float, longitude: float) -> dict:
    """Open-Meteo에서 3일간 시간별/일별 예보를 가져옵니다."""
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": (
            "temperature_2m,relative_humidity_2m,"
            "precipitation_probability,weather_code,wind_speed_10m"
        ),
        "daily": "temperature_2m_max,temperature_2m_min",
        "timezone": "auto",
        "forecast_days": 3,
    }
    response = requests.get(FORECAST_API, params=params, timeout=10)
    response.raise_for_status()
    return response.json()


def extract_target_forecasts(weather: dict) -> list[dict]:
    """오늘부터 3일간 오전 6시와 오후 3시 데이터만 추출합니다."""
    hourly = weather["hourly"]
    by_time = {
        timestamp: index
        for index, timestamp in enumerate(hourly["time"])
    }

    start_date = datetime.fromisoformat(hourly["time"][0]).date()
    result = []

    for offset in range(3):
        current_date = start_date + timedelta(days=offset)
        samples = []

        for hour in TARGET_HOURS:
            timestamp = f"{current_date.isoformat()}T{hour:02d}:00"
            index = by_time.get(timestamp)
            if index is None:
                continue

            samples.append(
                {
                    "time": timestamp,
                    "temperature": hourly["temperature_2m"][index],
                    "humidity": hourly["relative_humidity_2m"][index],
                    "precipitation_probability": hourly["precipitation_probability"][index],
                    "weather_code": hourly["weather_code"][index],
                    "wind_speed": hourly["wind_speed_10m"][index],
                }
            )

        result.append({"date": current_date.isoformat(), "samples": samples})

    return result


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
    print("날씨 정보를 가져오는 중...")

    weather = fetch_weather(location["latitude"], location["longitude"])
    forecasts = extract_target_forecasts(weather)

    for day in forecasts:
        print(f"\n{day['date']}")
        for sample in day["samples"]:
            clock = sample["time"].split("T")[1]
            print(
                f"  {clock} | {sample['temperature']}°C | "
                f"습도 {sample['humidity']}% | "
                f"강수확률 {sample['precipitation_probability']}% | "
                f"풍속 {sample['wind_speed']} km/h"
            )


if __name__ == "__main__":
    try:
        main()
    except (requests.RequestException, ValueError, KeyError) as exc:
        print(f"오류: {exc}")
