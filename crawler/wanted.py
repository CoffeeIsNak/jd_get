import requests
import time

def wanted_crawler(wanted_headers):
    API_URL = "https://www.wanted.co.kr/api/chaos/navigation/v1/results"
    WANTED_HEADERS = wanted_headers

    PARAMS = {
        "job_group_id": 518,  # 데이터 엔지니어 직군 코드 (예시)
        "job_ids": 655,  # 특정 직무 ID (예시)
        "country": "kr",
        "job_sort": "job.latest_order",
        "years": [0, 3],  # 0~3년 경력
        "locations": "all",
        "limit": 20,  # 한 번에 가져올 개수
        "offset": 0  # 페이지네이션 (처음부터 시작)
    }

    all_jobs = []  # 모든 채용 공고 저장 리스트
    offset = 0  # 초기 offset 값
    limit = 20  # 한 번에 가져올 개수

    markdown_all = ""  # 전체 공고
    markdown_newbie = ""  # 신입 공고
    markdown_experienced = ""  # 경력 공고

    while True:
        PARAMS["offset"] = offset  # offset 업데이트
        response = requests.get(API_URL, params=PARAMS, headers=WANTED_HEADERS)

        if response.status_code != 200:
            print(f"❌ 요청 실패: {response.status_code}")
            break

        data = response.json()
        
        job_list = data.get("data", {})  # 실제 채용 공고 리스트 추출
        if not job_list:
            print("✅ 더 이상 데이터 없음 → 크롤링 종료")
            break  # 더 이상 데이터 없으면 종료

        all_jobs.extend(job_list)  # 가져온 데이터 추가

        print(f"✅ {offset} ~ {offset + limit}번째 데이터 수집 완료 ({len(job_list)}개)")
        
        for job in job_list:
            # 공고 제목
            title = job.get("position", "제목 없음")

            # 원티드 URL (id 기반 생성)
            job_id = job.get("id")
            job_url = f"https://www.wanted.co.kr/wd/{job_id}" if job_id else "URL 없음"

            # 회사명
            company_name = job.get("company", {}).get("name", "회사명 없음")

            # 근무 지역
            location = job.get("address", {}).get("district", "지역 정보 없음")

            # 경력 정보
            is_newbie = job.get("is_newbie", False)  # 신입 여부
            annual_from = job.get("annual_from")  # 최소 경력
            annual_to = job.get("annual_to")  # 최대 경력

            if is_newbie:
                career_info = "신입"
            elif annual_from is not None and annual_to is not None:
                career_info = f"{annual_from}~{annual_to}년 경력"
            else:
                career_info = "경력 정보 없음"

            # 마감일 정보 (D-값 없음)
            deadline = "상시채용"

            # 마크다운 포맷으로 저장
            markdown_entry = f"\n🔹 Job: {title} ({company_name})\n"
            markdown_entry += f"🔗 URL: {job_url}\n\n"
            markdown_entry += f"📌 **상세 정보**: ['{career_info}', '학력무관', '정규직', '{location}', '{deadline}']\n\n"
            markdown_entry += "---\n"

            # 전체 마크다운
            markdown_all += markdown_entry

            # 신입 & 경력 구분 저장
            if is_newbie:
                markdown_newbie += markdown_entry  # 신입 채용 공고 저장
            else:
                markdown_experienced += markdown_entry  # 경력 채용 공고 저장

        # 다음 페이지로 이동
        offset += limit

        # 요청 사이 딜레이 추가 (서버 차단 방지)
        time.sleep(1.5)


    # 마크다운 파일 저장
    job_list_folder = "job_list"
    with open(job_list_folder + "/all_job_list.md", "w", encoding="utf-8") as f:
        f.write(markdown_all)

    with open(job_list_folder + "/newbie_job_list.md", "a", encoding="utf-8") as f:
        f.write(markdown_newbie)

    with open(job_list_folder + "/1_to_3_experience_required_job_list.md", "w", encoding="utf-8") as f:
        f.write(markdown_experienced)

    print(f"✅ 총 {len(all_jobs)}개의 채용 공고 저장 완료! (wanted_all.md, wanted_newbie.md, wanted_experienced.md)")
