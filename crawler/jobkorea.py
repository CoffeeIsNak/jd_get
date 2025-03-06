import requests, bs4


def job_korea_crawler(c_type, jk_headers):
    """
    c_type:
        1 = 신입
        2 = 경력
        4 = 경력무관
    """
    if c_type == 1:
        print("🚀잡코리아 신입 채용 공고 크롤링 시작")
    elif c_type == 1:
        print("🚀잡코리아 경력 채용 공고 크롤링 시작")
    else:
        print("🚀잡코리아 경력 무관 채용 공고 크롤링 시작")
    JK_HEADERS = jk_headers
    page_no = 1
    markdown_content = "\n"  # 마크다운 저장용 문자열

    while True:
        if c_type == 2:
            BASE_URL = rf"https://www.jobkorea.co.kr/Search/?stext=%EB%8D%B0%EC%9D%B4%ED%84%B0%EC%97%94%EC%A7%80%EB%8B%88%EC%96%B4&FeatureCode=WRK&duty=1000236&careerType={c_type}&careerMin=1&careerMax=3&tabType=recruit&Page_No={page_no}"
        else:
            BASE_URL = rf"https://www.jobkorea.co.kr/Search/?stext=%EB%8D%B0%EC%9D%B4%ED%84%B0%EC%97%94%EC%A7%80%EB%8B%88%EC%96%B4&FeatureCode=WRK&duty=1000236&careerType={c_type}&tabType=recruit&Page_No={page_no}"
        
        session = requests.Session()
        response = session.get(BASE_URL, headers=JK_HEADERS)

        # 응답 상태 확인
        if response.status_code != 200:
            print(f"❌ 요청 실패: {response.status_code}")
            exit()

        response.encoding = "utf-8"
        html_content = response.text

        # BeautifulSoup으로 HTML 파싱
        soup = bs4.BeautifulSoup(html_content, "html.parser")

        # 페이지 넘기기 종료
        no_result = soup.select_one("p.list-empty-result")
        if no_result:
            print("✅ 검색 결과 없음 → 크롤링 종료")
            break

        # XPath에 해당하는 위치 찾기 (CSS Selector 사용)
        target_section = soup.select_one("main div article article section:nth-of-type(1) article:nth-of-type(2)")

        if target_section:
            # 1번째부터 15번째 article만 가져오기
            job_articles = target_section.find_all("article")

            # 결과 출력
            for idx, job in enumerate(job_articles, start=1):
                # 공고 제목 & 링크 찾기
                title_tag = job.select_one("div:nth-of-type(2) div a.information-title-link")
                title = title_tag.text.strip() if title_tag else "제목 없음"
                url = "https://www.jobkorea.co.kr" + title_tag["href"] if title_tag else "URL 없음"

                # /html/body/main/div/article/article/section[1]/article[2]/article[1]/div[2]/ul
                # 추가 정보 크롤링 (신입/경력, 학력, 근무 형태, 지역, 마감일)
                detail_list = job.select("ul.chip-information-group li.chip-information-item")
                details_text = [detail.text.strip() for detail in detail_list]

                # 데이터 출력
                markdown_content += f"🔹 Job: {title}\n"
                markdown_content += f"🔗 URL: {url}\n\n"
                markdown_content += f"📌 **상세 정보**: {details_text}\n\n"
                markdown_content += "---\n\n"

        else:
            print("❌ 해당 섹션을 찾을 수 없음")
        
        page_no += 1

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
