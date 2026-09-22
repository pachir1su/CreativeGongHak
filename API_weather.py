# CreativeGongHak - Weather Report Project
# GitHub Repository: https://github.com/pachir1su/CreativeGongHak
#
# 4주차 개인 프로젝트: Open-Meteo API를 활용한 날씨 리포트

from datetime import datetime, timedelta
import json
from pathlib import Path

import requests

GEOCODING_API = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_API = "https://api.open-meteo.com/v1/forecast"
TARGET_HOURS = (6, 15)

WMO_WEATHER = {
    0: "맑음",
    1: "대체로 맑음",
    2: "부분적으로 흐림",
    3: "흐림",
    45: "안개",
    48: "서리 안개",
    51: "약한 이슬비",
    53: "이슬비",
    55: "강한 이슬비",
    56: "약한 어는 이슬비",
    57: "강한 어는 이슬비",
    61: "약한 비",
    63: "비",
    65: "강한 비",
    66: "약한 어는 비",
    67: "강한 어는 비",
    71: "약한 눈",
    73: "눈",
    75: "강한 눈",
    77: "싸락눈",
    80: "약한 소나기",
    81: "소나기",
    82: "강한 소나기",
    85: "약한 눈 소나기",
    86: "강한 눈 소나기",
    95: "천둥번개",
    96: "우박 동반 천둥번개",
    99: "강한 우박 동반 천둥번개",
}


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
    daily = weather["daily"]

    hourly_index = {
        timestamp: index
        for index, timestamp in enumerate(hourly["time"])
    }
    daily_index = {
        date_text: index
        for index, date_text in enumerate(daily["time"])
    }

    start_date = datetime.fromisoformat(hourly["time"][0]).date()
    result = []

    for offset in range(3):
        current_date = start_date + timedelta(days=offset)
        date_text = current_date.isoformat()
        samples = []

        for hour in TARGET_HOURS:
            timestamp = f"{date_text}T{hour:02d}:00"
            index = hourly_index.get(timestamp)
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

        d_index = daily_index.get(date_text)
        result.append(
            {
                "date": date_text,
                "samples": samples,
                "temperature_min": daily["temperature_2m_min"][d_index] if d_index is not None else None,
                "temperature_max": daily["temperature_2m_max"][d_index] if d_index is not None else None,
            }
        )

    return result


def weather_description(code: int) -> str:
    return WMO_WEATHER.get(code, f"알 수 없음({code})")


def day_label(offset: int) -> str:
    return ("오늘", "내일", "모레")[offset]


def print_report(location: dict, forecasts: list[dict]) -> None:
    print()
    print("=" * 58)
    print(f"☀️ {location['name']} 날씨 예보 (오전 6시 / 오후 3시 기준)")
    print("=" * 58)

    for offset, day in enumerate(forecasts):
        date_obj = datetime.fromisoformat(day["date"])
        print()
        print(f"📅 {day_label(offset)} ({date_obj:%m.%d.})")
        print("-" * 50)

        for sample in day["samples"]:
            hour = datetime.fromisoformat(sample["time"]).hour
            time_label = "오전 06:00" if hour == 6 else "오후 15:00"
            icon = "🌅" if hour == 6 else "🌇"
            print(f"  {icon} {time_label}")
            print(f"     날씨: {weather_description(sample['weather_code'])}")
            print(f"     기온: {sample['temperature']} °C")
            print(f"     강수확률: {sample['precipitation_probability']}%")
            print(f"     습도: {sample['humidity']}%")
            print(f"     풍속: {sample['wind_speed']} km/h")
            print()

        if day["temperature_min"] is not None:
            print(
                f"  🌡 일일 기온: 최저 {day['temperature_min']} °C / "
                f"최고 {day['temperature_max']} °C"
            )

    print()
    print("=" * 58)


def save_json(location: dict, forecasts: list[dict]) -> Path:
    """현재 날씨 리포트를 UTF-8 JSON 파일로 저장합니다."""
    safe_name = "".join(
        char if char.isalnum() or char in ("-", "_") else "_"
        for char in location["name"]
    )
    filename = f"weather_{safe_name}_{datetime.now():%Y%m%d_%H%M%S}.json"
    path = Path(filename)

    payload = {
        "repository": "https://github.com/pachir1su/CreativeGongHak",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "location": location,
        "forecasts": forecasts,
    }
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return path


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
    print_report(location, forecasts)

    answer = input("\n날씨 정보를 JSON 파일로 저장하시겠습니까? (y/n): ").strip().lower()
    if answer in {"y", "yes"}:
        path = save_json(location, forecasts)
        print(f"저장 완료: {path.resolve()}")


if __name__ == "__main__":
    try:
        main()
    except requests.Timeout:
        print("오류: API 응답 시간이 초과되었습니다. 잠시 후 다시 시도해 주세요.")
    except requests.RequestException as exc:
        print(f"오류: 날씨 API 요청에 실패했습니다. ({exc})")
    except (ValueError, KeyError, IndexError) as exc:
        print(f"오류: {exc}")
    except KeyboardInterrupt:
        print("\n프로그램을 종료합니다.")
