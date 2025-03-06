import requests, os, time

def jp_crawler(jp_headers):
    API_URL = "https://www.jobplanet.co.kr/api/v3/search/postings"
    JP_HEADERS = jp_headers
    PARAMS = {
        "occupation_level2": "11913,11916",  # 데이터 엔지니어 관련 직군 코드
        "years_of_experience": "0,3",  # 0~2년 경력
        "order_by": "ranking",
        "query": "",
        "page": 1,  # 시작 페이지
        "page_size": 8  # 한 번에 가져올 개수
    }
    all_jobs = []  # 모든 채용 공고 저장 리스트
    page = 1  # 초기 페이지 값

    markdown_all = ""  # 전체 공고
    markdown_newbie = ""  # 신입 공고
    markdown_experienced = ""  # 경력 공고

    while True:
        PARAMS["page"] = page  # 현재 페이지 설정
        response = requests.get(API_URL, params=PARAMS, headers=JP_HEADERS)

        if response.status_code != 200:
            print(f"❌ 요청 실패: {response.status_code}")
            break

        data = response.json()
        
        job_list = data.get("data", {}).get("items", [])  # 실제 채용 공고 리스트 추출
        if not job_list:
            print("✅ 더 이상 데이터 없음 → 크롤링 종료")
            break  # 더 이상 데이터 없으면 종료

        all_jobs.extend(job_list)  # 가져온 데이터 추가

        print(f"✅ Page {page} - {len(job_list)}개 수집 완료")

        for job in job_list:
            # 공고 제목
            title = job.get("title", "제목 없음")

            # 원티드 URL (id 기반 생성)
            job_id = job.get("id")
            job_url = f"https://www.jobplanet.co.kr/job/{job_id}" if job_id else "URL 없음"

            # 회사명
            company_name = job.get("company", {}).get("name", "회사명 없음")

            # 근무 지역
            location = job.get("company", {}).get("city_name", "지역 정보 없음")

            # 경력 정보
            # 2 = 경력
            # 4 = 무관
            # 1 = 신입
            is_newbie = job.get("annual", {}).get("type")[0]
            annual_from = job.get("annual", {}).get("years", 0)  # 최소 경력
            annual_to = job.get("annual", {}).get("maximum_years", 100)  # 최대 경력

            if is_newbie == 1:
                career_info = "신입"
            elif is_newbie == 4:
                career_info = "경력무관"
            elif annual_from is not None and annual_to is not None:
                career_info = f"{annual_from}~{annual_to}년 경력"
            else:
                career_info = "경력 정보 없음"

            deadline = job.get("deadline_message")

            # 마크다운 포맷으로 저장
            markdown_entry = f"\n🔹 Job: {title} ({company_name})\n"
            markdown_entry += f"🔗 URL: {job_url}\n\n"
            markdown_entry += f"📌 **상세 정보**: ['{career_info}', '학력무관', '정규직', '{location}', '{deadline}']\n\n"
            markdown_entry += "---\n"

            # 전체 마크다운
            markdown_all += markdown_entry

            # 신입 & 경력 구분 저장
            if is_newbie == 1:
                markdown_newbie += markdown_entry  # 신입, 경력 무관 채용 공고 저장
            else:
                markdown_experienced += markdown_entry  # 경력 채용 공고 저장

        # 다음 페이지로 이동
        page += 1

        # 요청 사이 딜레이 추가 (서버 차단 방지)
        time.sleep(1.5)


    # ✅ 마크다운 파일 저장
    job_list_folder = "job_list"
    os.makedirs(job_list_folder, exist_ok=True)  # 폴더 없으면 자동 생성

    with open(job_list_folder + "/all_job_list.md", "a", encoding="utf-8") as f:
        f.write(markdown_all)

    with open(job_list_folder + "/newbie_job_list.md", "a", encoding="utf-8") as f:
        f.write(markdown_newbie)

    with open(job_list_folder + "/1_to_3_experience_required_job_list.md", "a", encoding="utf-8") as f:
        f.write(markdown_experienced)

    print(f"✅ 총 {len(all_jobs)}개의 채용 공고 저장 완료! (all_job_list.md, newbie_job_list.md, experienced_job_list.md)")
