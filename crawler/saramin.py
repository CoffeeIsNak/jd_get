import requests, bs4, os, time


def saramin_crawler(c_type, saram_headers):
    """
    c_type:
        0 = 경력무관
        1 = 신입
        2 = 1~3년 경력
    """
    if c_type == 0:
        print("🚀사람인 경력 무관 채용 공고 크롤링 시작")
    elif c_type == 1:
        print("🚀사람인 신입 채용 공고 크롤링 시작")
    else:
        print("🚀사람인 1 ~ 3년 경력 채용 공고 크롤링 시작")
    
    SARAM_HEADERS = saram_headers
    page_no = 1
    markdown_content = "\n"  # 마크다운 저장용 문자열

    job_list_folder = "job_list"
    os.makedirs(job_list_folder, exist_ok=True)  # 폴더 생성 (없으면 자동 생성)

    while True:
        if c_type == 2:
            BASE_URL = rf"https://www.saramin.co.kr/zf_user/search?searchType=search&searchword=%EB%8D%B0%EC%9D%B4%ED%84%B0+%EC%97%94%EC%A7%80%EB%8B%88%EC%96%B4&cat_kewd=83&exp_none=y&company_cd=0%2C1%2C2%2C3%2C4%2C5%2C6%2C7%2C9%2C10&exp_cd=2&exp_max=3&panel_type=&search_optional_item=y&search_done=y&panel_count=y&preview=y&recruitPage={page_no}"
        else:
            BASE_URL = rf"https://www.saramin.co.kr/zf_user/search?searchType=search&searchword=%EB%8D%B0%EC%9D%B4%ED%84%B0+%EC%97%94%EC%A7%80%EB%8B%88%EC%96%B4&cat_kewd=83&exp_none=y&company_cd=0%2C1%2C2%2C3%2C4%2C5%2C6%2C7%2C9%2C10&panel_type=&search_optional_item=y&search_done=y&panel_count=y&preview=y&recruitPage={page_no}&exp_cd={c_type}"
        
        session = requests.Session()
        response = session.get(BASE_URL, headers=SARAM_HEADERS)

        # 응답 상태 확인
        if response.status_code != 200:
            print(f"❌ 요청 실패: {response.status_code}")
            break

        response.encoding = "utf-8"
        html_content = response.text
        soup = bs4.BeautifulSoup(html_content, "html.parser")

        # ✅ 채용 공고 섹션 찾기
        job_section = soup.select("div.content > div.item_recruit")  # 각 공고를 담고 있는 div 태그

        if not job_section:
            print(f"❌ 채용 정보 섹션을 찾을 수 없음 (페이지 {page_no})")
            break

        for job in job_section:
            # 공고 제목 & 링크
            title_tag = job.select_one("h2.job_tit > a")
            title = title_tag.text.strip() if title_tag else "제목 없음"
            url = "https://www.saramin.co.kr" + title_tag["href"] if title_tag else "URL 없음"

            # 회사명/html/body/div[4]/div/div[1]/section/div[3]/div[1]/div[1]/div[3]/strong/a
            # #recruit_info_list > div.content > div:nth-child(1) > div.area_corp > strong > a
            # #recruit_info_list > div.content > div:nth-child(1) > div.area_corp > strong > a
            company_tag = job.select_one("div.area_corp strong.corp_name a")
            company = company_tag.text.strip() if company_tag else "회사명 없음"

            # 신입/경력 정보 /html/body/div[4]/div/div[1]/section/div[3]/div[1]/div[1]/div[2]/div[3]/span[2]
            # #recruit_info_list > div.content > div:nth-child(1) > div.area_job > div.job_condition > span:nth-child(2)
            experience_tag = job.select_one("div.area_job div.job_condition span:nth-child(2)")
            experience_text = experience_tag.text.strip() if experience_tag else "경력 정보 없음"

            # 지역 정보
            location_tag = job.select_one("div.area_job div.job_condition span:nth-child(1)")
            location = location_tag.text.strip() if location_tag else "지역 정보 없음"

            # 마감일 정보 #recruit_info_list > div.content > div:nth-child(1) > div.area_job > div.job_date > span
            deadline_tag = job.select_one("div.area_job div.job_date span")
            deadline = deadline_tag.text.strip() if deadline_tag else "상시채용"

            # 마크다운 포맷으로 저장
            markdown_content += f"🔹 Job: {title} ({company})\n"
            markdown_content += f"🔗 URL: {url}\n\n"
            markdown_content += f"📌 **상세 정보**: ['{experience_text}', '학력무관', '정규직', '{location}', '{deadline}']\n\n"
            markdown_content += "---\n\n"

        print(f"✅ 페이지 {page_no} - {len(job_section)}개 크롤링 완료")
        page_no += 1
        time.sleep(1.5)  # 서버 부하 방지

    # ✅ 마크다운 파일 저장
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
