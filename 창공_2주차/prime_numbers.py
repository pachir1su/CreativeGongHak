"""1부터 100까지의 소수를 찾는 개인 실습 프로그램.

교수님 예제의 에라토스테네스의 체 대신, 후보 수를 직접 판별하는
6k ± 1 최적화 방식을 사용한다.
"""


def isPrimeNumber(number: int) -> bool:
    """number가 소수인지 확인한다."""
    # 2와 3은 작은 소수이며, 그보다 작은 수와 짝수는 먼저 제외한다.
    if number in (2, 3):
        return True
    if number < 2 or number % 2 == 0 or number % 3 == 0:
        return False

    # 6의 배수 주변 후보만 검사하면 불필요한 나눗셈을 줄일 수 있다.
    divisor = 5
    while divisor * divisor <= number:
        if number % divisor == 0 or number % (divisor + 2) == 0:
            return False
        divisor += 6
    return True


def collectPrimeNumbers(limit: int = 100) -> list[int]:
    """1부터 limit까지의 소수를 순서대로 반환한다."""
    # 실행 범위를 명확히 검증해 잘못된 입력을 조기에 안내한다.
    if not isinstance(limit, int) or isinstance(limit, bool):
        raise TypeError("limit은 정수여야 합니다.")
    if limit < 1:
        raise ValueError("limit은 1 이상이어야 합니다.")

    # 각 후보를 함수로 판별해 결과 목록을 만든다.
    return [number for number in range(2, limit + 1) if isPrimeNumber(number)]


def printPrimeReport(limit: int = 100) -> None:
    """소수 목록과 개수를 보기 쉽게 출력한다."""
    # 계산 결과를 줄 단위 보고서로 구성해 기존 한 줄 출력과 구분한다.
    primeNumbers = collectPrimeNumbers(limit)
    print(f"1부터 {limit} 사이의 소수:")
    print(", ".join(map(str, primeNumbers)))
    print(f"총 {len(primeNumbers)}개")


def main() -> None:
    """개인 실습 프로그램의 기본 실행 지점."""
    # 과제 기본 범위인 1부터 100까지를 실행하고 예상 오류를 안내한다.
    try:
        printPrimeReport()
    except (TypeError, ValueError) as error:
        print(f"입력 오류: {error}")
    except Exception as error:
        print(f"실행 중 오류가 발생했습니다: {error}")


if __name__ == "__main__":
    # 이 파일을 직접 실행했을 때만 결과를 출력한다.
    main()
