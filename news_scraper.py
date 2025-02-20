import urllib.request
import urllib.parse
import json
import pandas as pd
import os
from datetime import datetime

# ✅ GitHub Actions에서 환경 변수 가져오기
client_id = os.getenv("NAVER_CLIENT_ID")
client_secret = os.getenv("NAVER_CLIENT_SECRET")

# ✅ 검색할 키워드 목록 (자동 실행이므로 고정된 키워드 사용 가능)
keywords = ["반도체", "스마트폰"]

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
                news_list.append([
                    keyword,  # 검색 키워드
                    item['title'],  # 뉴스 제목
                    item['originallink'],  # 뉴스 원본 링크
                    item['link'],  # 네이버 뉴스 링크
                    item['description'],  # 뉴스 요약
                    item['pubDate']  # 뉴스 게시 날짜
                ])

            # 리스트를 전체 결과 리스트에 추가
            all_results.extend(news_list)

        else:
            print(f"Error Code: {rescode}")

    except Exception as e:
        print(f"Error: {e}")

# ✅ DataFrame 생성
columns = ['검색 키워드', '제목', '원본 링크', '네이버 뉴스 링크', '요약', '게시 날짜']
df = pd.DataFrame(all_results, columns=columns)

# ✅ CSV 파일로 저장
# ✅ CSV 파일이 이미 존재하는지 확인 후 저장 방식 결정
if os.path.exists(csv_filename):
    df.to_csv(csv_filename, mode='a', index=False, header=False, encoding='utf-8-sig')  # 기존 파일에 추가 (header 제외)
else:
    df.to_csv(csv_filename, mode='w', index=False, encoding='utf-8-sig')  # 새 파일 생성 (header 포함)


print(f"\n📂 검색 결과가 '{csv_filename}' 파일로 저장되었습니다.")
