# CreativeGongHak

창의적공학설계(AD) 01분반 실습 저장소입니다.

## 4주차 - 날씨 리포트 개인 프로젝트

Python과 **Open-Meteo API**를 이용하여 사용자가 입력한 지역의 **오늘/내일/모레 3일간 날씨**를 출력합니다.

### 주요 기능

- 사용자가 지역명 입력 (미입력 시 서울)
- Open-Meteo Geocoding API로 위도/경도 검색
- 오전 6시 / 오후 3시 예보 출력
- 날씨, 기온, 강수확률, 습도, 풍속 표시
- 일일 최저/최고 기온 표시
- 선택적으로 결과를 JSON 파일로 저장
- API 오류 및 잘못된 지역 입력 처리

### 실행 방법

Python 3.10 이상을 권장합니다.

```bash
pip install -r requirements.txt
python API_weather.py
```

### Git / GitHub 실습 이력

이 프로젝트는 기능을 각각 별도 브랜치에서 개발하고 Pull Request로 `main`에 병합했습니다.

1. `feature/project-setup`
2. `feature/city-geocoding`
3. `feature/weather-api`
4. `feature/report-output`
5. `feature/json-export`

Git Graph에서 각 브랜치의 분기와 Merge 이력을 확인할 수 있습니다.

### 저장소 주소

https://github.com/pachir1su/CreativeGongHak
