import requests, os, time


def zig_hang_crawler(zh_headers):
    headers = zh_headers
    all_jobs = []  # 모든 채용 공고 저장 리스트
    page = 0  # 초기 페이지 값

    markdown_all = ""  # 전체 공고
    markdown_newbie = ""  # 신입 공고
    markdown_experienced = ""  # 경력 공고

    while True:
        api_url = rf"https://api.zighang.com/api/recruitment/filter/v4?page={page}&size=11&isOpen=true&sortCondition=DEADLINE&orderBy=ASC&companyTypes=&industries=&recruitmentTypeNames=&recruitmentDeadlineType=&educations=&careers=ZERO,ONE,TWO,THREE,IRRELEVANCE&recruitmentAddress=&recJobMajorCategory=AI_%EB%8D%B0%EC%9D%B4%ED%84%B0&recJobSubCategory=%EB%8D%B0%EC%9D%B4%ED%84%B0%EC%97%94%EC%A7%80%EB%8B%88%EC%96%B4&affiliate=&companyName=&keywords=&uploadStartDate=&uploadEndDate=&workStartDate=&workEndDate="
        response = requests.get(api_url, headers=headers)

        if response.status_code != 200:
            print(f"❌ 요청 실패: {response.status_code}")
            print(response.text)
            break

        data = response.json()
        
        job_list = data.get("recruitments", {}).get("recruitmentSimpleList", [])  # 실제 채용 공고 리스트 추출
        if not job_list:
            print("✅ 더 이상 데이터 없음 → 크롤링 종료")
            break  # 더 이상 데이터 없으면 종료

        all_jobs.extend(job_list)  # 가져온 데이터 추가

        print(f"✅ Page {page} - {len(job_list)}개 수집 완료")

        for job in job_list:
            # 공고 제목
            title = job.get("title", "제목 없음")

            # URL
            job_url = job.get("shortenedUrl", "URL 없음")

            # 회사명
            company_name = job.get("companyName", "회사명 없음")

            # 근무 지역
            locations = job.get("recruitmentAddress", [])
            location = ', '.join(locations)

            # 경력 정보
            careers = job.get('careers', [])
            if 'ZERO' in careers:
                is_newbie = True
            else:
                is_newbie = False
                if 'ONE' in careers:
                    annual_from = 1
                elif 'TWO' in careers:
                    annual_from = 2
                else:
                    annual_from = 3

            if is_newbie:
                career_info = "신입"
            else:
                career_info = f'{annual_from}년 이상'

            deadline_type = job.get('deadlineType') 
            deadline_msg = job.get("recruitmentDeadline")

            if deadline_type == 'DUE_DATE':
                deadline = deadline_msg[:10]
            else:
                deadline = '상시채용'
            

            # 마크다운 포맷으로 저장
            markdown_entry = f"\n🔹 Job: {title} ({company_name})\n"
            markdown_entry += f"🔗 URL: {job_url}\n\n"
            markdown_entry += f"📌 **상세 정보**: ['{career_info}', '학력무관', '정규직', '{location}', '{deadline}']\n\n"
            markdown_entry += "---\n"

            # 전체 마크다운
            markdown_all += markdown_entry

            # 신입 & 경력 구분 저장
            if is_newbie:
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
