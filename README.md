# Crypto-Arbitrage-Trading-Project

## 필수 라이브러리 및 설치 방법

이 프로젝트를 실행하기 위해 아래의 라이브러리들이 필요합니다.

- **Python 3.6 이상**  
  프로젝트 실행에 필요한 최소 Python 버전입니다.

- **ccxt**  
  다양한 암호화폐 거래소 API 연동을 위한 라이브러리  
  설치: `pip install ccxt`

- **requests**  
  HTTP 요청을 보내기 위한 라이브러리  
  설치: `pip install requests`

- **schedule**  
  주기적인 작업(예: 가격 체크 및 거래 실행)을 위한 스케줄링 라이브러리  
  설치: `pip install schedule`

- **pandas**  
  데이터 처리 및 분석에 유용한 라이브러리  
  설치: `pip install pandas`

- **numpy**  
  수치 계산 및 배열 연산을 위한 라이브러리  
  설치: `pip install numpy`

- **python-dotenv**  
  API 키와 같은 민감 정보 관리를 위해 `.env` 파일 사용 시 필요한 라이브러리  
  설치: `pip install python-dotenv`

## requirements.txt 파일 생성

아래와 같이 `requirements.txt` 파일을 작성하면, 다음 명령어로 한 번에 모든 라이브러리를 설치할 수 있습니다.

```bash
pip install -r requirements.txt
