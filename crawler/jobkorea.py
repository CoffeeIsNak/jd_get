import requests, bs4, time
from datetime import datetime, timedelta


def job_korea_crawler(c_type, jk_headers):
    """
    c_type:
        1 = 신입
        2 = 경력
        4 = 경력무관
    """
    if c_type == 1:
        print("🚀 잡코리아 신입 채용 공고 크롤링 시작")
    elif c_type == 2:
        print("🚀 잡코리아 경력 채용 공고 크롤링 시작")
    else:
        print("🚀 잡코리아 경력 무관 채용 공고 크롤링 시작")
    headers = jk_headers
    page_no = 1
    markdown_content = "\n"  # 마크다운 저장용 문자열

    while True:
        if c_type == 2:
            BASE_URL = rf"https://www.jobkorea.co.kr/Search/?FeatureCode=WRK&duty=1000236&careerType={c_type}&careerMin=1&careerMax=3&tabType=recruit&Page_No={page_no}"
        else:
            BASE_URL = rf"https://www.jobkorea.co.kr/Search/?FeatureCode=WRK&duty=1000236&careerType={c_type}&tabType=recruit&Page_No={page_no}"
        
        session = requests.Session()
        response = session.get(BASE_URL, headers=headers)

        # 응답 상태 확인
        if response.status_code != 200:
            print(f"❌ 요청 실패: {response.status_code}")
            exit()

        response.encoding = "utf-8"
        html_content = response.text

        # BeautifulSoup으로 HTML 파싱
        soup = bs4.BeautifulSoup(html_content, "html.parser")

        # 채용공고 리스트 가져오기
        target_section = soup.select("article.list")

        # 페이지 넘기기 종료
        if target_section:
            target_section = target_section[0]
            job_articles = target_section.find_all("article")
            
            # 결과 출력
            for job in job_articles:
                # 공고 제목 & 링크 찾기
                title_tag = job.select_one("div:nth-of-type(2) div a.information-title-link")
                title = title_tag.text.strip() if title_tag else "제목 없음"
                url = "https://www.jobkorea.co.kr" + title_tag["href"] if title_tag else "URL 없음"

                # 회사명 
                # /html/body/main/div/article/article/section[1]/article[2]/article[17]/div[1]/a
                company_name_tag = job.select_one("div:nth-of-type(1) a")
                company_name = company_name_tag.text.strip() if company_name_tag else "회사명 없음"

                # /html/body/main/div/article/article/section[1]/article[2]/article[1]/div[2]/ul
                # 추가 정보 크롤링 (신입/경력, 학력, 근무 형태, 지역, 마감일)
                detail_list = job.select("ul.chip-information-group li.chip-information-item")
                details_text = [detail.text.strip() for detail in detail_list]

                deadline = details_text[-1]

                if deadline == '상시채용':
                    pass
                elif deadline == '오늘마감':
                    d_days = 0
                    deadline_date = datetime.now() + timedelta(d_days)
                    details_text[-1] = deadline_date.strftime('%Y-%m-%d')
                else:
                    d_days = int(deadline[2:])
                    deadline_date = datetime.now() + timedelta(d_days)
                    details_text[-1] = deadline_date.strftime('%Y-%m-%d')

                # 데이터 출력
                markdown_content += f"\n🔹 Job: {title} ({company_name})\n"
                markdown_content += f"🔗 URL: {url}\n\n"
                markdown_content += f"📌 **상세 정보**: {details_text}\n\n"
                markdown_content += "---\n"
        else:
            print("✅ 검색 결과 없음 → 크롤링 종료")
            break
        
        print(f"✅ {page_no} - {len(job_articles)} 개 채용공고 크롤링 완료")
        page_no += 1
        time.sleep(1)
        

    # 마크다운 파일 저장
    job_list_folder = "job_list"
    if c_type == 1 or c_type == 4:
        file_name = job_list_folder + "/newbie_job_list.md"
    else:
        file_name = job_list_folder + "/1_to_3_experience_required_job_list.md"

    with open(file_name, "a", encoding="utf-8") as f:
        f.write(markdown_content)
    
    all_file_name = job_list_folder + "/all_job_list.md"
    with open(all_file_name, "a", encoding="utf-8") as f:
        f.write(markdown_content)
    
    print("✅ 크롤링 완료 → 마크다운 저장 완료")
