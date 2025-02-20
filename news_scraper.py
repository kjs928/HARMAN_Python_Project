import urllib.request
import urllib.parse
import json
import pandas as pd
import os
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ✅ GitHub Actions에서 환경 변수 가져오기
client_id = os.getenv("NAVER_CLIENT_ID")
client_secret = os.getenv("NAVER_CLIENT_SECRET")

# ✅ 네이버 SMTP 서버 정보
SMTP_SERVER = "smtp.naver.com"
SMTP_PORT = 587  # TLS 포트

# ✅ 네이버 이메일 계정 정보 (보안을 위해 환경 변수 사용 추천)
NAVER_EMAIL = os.getenv("NAVER_EMAIL")
NAVER_PASSWORD = os.getenv("NAVER_PASSWORD")
TO_EMAIL = os.getenv("TO_EMAIL")


# ✅ 검색할 키워드 목록
keywords = ["반도체", "삼성전자", "sk하이닉스"]

# ✅ 가져올 검색 결과 개수 설정 (최대 100개)
result_count = 5

# ✅ 전체 검색 결과 저장 리스트
all_results = []

# ✅ 네이버 뉴스 검색 API 요청 및 결과 DataFrame 변환
for keyword in keywords:
    encText = urllib.parse.quote(keyword)
    url = f"https://openapi.naver.com/v1/search/news.json?query={encText}&display={result_count}"

    # 요청 객체 생성 및 헤더 추가
    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id", client_id)
    request.add_header("X-Naver-Client-Secret", client_secret)

    # API 요청 및 응답 처리
    try:
        response = urllib.request.urlopen(request)
        rescode = response.getcode()

        if rescode == 200:
            response_body = response.read()
            response_json = json.loads(response_body.decode('utf-8'))  # JSON 파싱

            # 검색 결과를 DataFrame에 저장
            news_list = []
            for item in response_json['items']:
                # ✅ pubDate 날짜 변환 (YYYY-MM-DD, 시간 제거)
                try:
                    pub_date = datetime.strptime(item['pubDate'], "%a, %d %b %Y %H:%M:%S %z")
                    pub_date = pub_date.strftime("%Y-%m-%d")  # 시간(HH:MM:SS) 제거
                except ValueError:
                    pub_date = item['pubDate']  # 변환 실패 시 원본 값 유지

                news_list.append([
                    keyword,               # 검색 키워드
                    pub_date,              # 변환된 뉴스 게시 날짜 (YYYY-MM-DD)
                    item['title'],         # 뉴스 제목
                    item['description'],   # 뉴스 요약
                    item['link']           # 네이버 뉴스 링크
                ])

            # 리스트를 전체 결과 리스트에 추가
            all_results.extend(news_list)

        else:
            print(f"Error Code: {rescode}")

    except Exception as e:
        print(f"Error: {e}")

# ✅ DataFrame 생성 (컬럼명 수정)
columns = ['keyword', 'date', 'title', 'summary', 'url']
df = pd.DataFrame(all_results, columns=columns)

# ✅ CSV 파일 경로 설정
csv_filename = "news_results.csv"

# ✅ 기존 CSV 파일 불러오기 (중복 방지)
if os.path.exists(csv_filename):
    existing_df = pd.read_csv(csv_filename, encoding='utf-8-sig')

    # 기존 데이터와 새로운 데이터 결합 후 중복 제거
    combined_df = pd.concat([existing_df, df]).drop_duplicates(subset=['title', 'date'], keep='last')

    # ✅ CSV 파일 덮어쓰기 (중복 제거 후 저장)
    combined_df.to_csv(csv_filename, mode='w', index=False, encoding='utf-8-sig')

else:
    # ✅ 새 파일 생성
    df.to_csv(csv_filename, mode='w', index=False, encoding='utf-8-sig')

print(f"\n📂 검색 결과가 '{csv_filename}' 파일로 저장되었습니다.")

# ✅ 이메일 전송 함수
def send_email():
    try:
        # ✅ 이메일 제목 & 본문 내용 설정
        subject = "[자동화 알림] 뉴스 저장 완료"
        body = f"""
        키워드로 설정하신 [{', '.join(keywords)}]에 대한 기사가 자동화로 저장되었습니다.

        자세한 내용은 사용자님의 웹페이지에서 확인해주세요.
        """

        # ✅ 이메일 메시지 생성
        msg = MIMEMultipart()
        msg["From"] = NAVER_EMAIL
        msg["To"] = TO_EMAIL
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        # ✅ 네이버 SMTP 서버에 연결하여 이메일 전송
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()  # TLS 보안 연결 활성화
        server.login(NAVER_EMAIL, NAVER_PASSWORD)  # 네이버 이메일 계정 로그인
        server.sendmail(NAVER_EMAIL, TO_EMAIL, msg.as_string())  # 이메일 전송
        server.quit()

        print("✅ 이메일이 성공적으로 전송되었습니다!")

    except Exception as e:
        print(f"❌ 이메일 전송 실패: {e}")

# ✅ CSV 저장 후 이메일 전송 실행
send_email()
