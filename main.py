import time
from dependencies import *
from helper import delete_old_list
from crawler.job_planet import jp_crawler
from crawler.jobkorea import job_korea_crawler
from crawler.saramin import saramin_crawler
from crawler.wanted import wanted_crawler
from crawler.zig_hang import zig_hang_crawler


def main():
    print("\n🔹오래된 채용 공고 삭제 중")
    delete_old_list.delete_folder_contents("job_list")
    print("✅ 오래된 채용 공고 삭제 완료\n")

    print("🚀 채용 공고 크롤링 시작!\n")

    # JobPlanet 크롤러 실행
    print("\n🔹 [1/5] JobPlanet 크롤링 중...")
    jp_crawler(JP_HEADERS)
    print("✅ JobPlanet 크롤링 완료!\n")

    # 잠시 대기 (서버 차단 방지)
    time.sleep(1)

    # Wanted 크롤러 실행
    print("\n🔹 [2/5] Wanted 크롤링 중...")
    wanted_crawler(WANTED_HEADERS)
    print("✅ Wanted 크롤링 완료!\n")

    time.sleep(1)

    # zighang 크롤러 실행
    print("\n🔹 [3/5] Zighang 크롤링 중...")
    zig_hang_crawler(ZH_HEADERS)
    print("✅ Zighang 크롤링 완료!\n")

    time.sleep(1)

    # Saramin 크롤러 실행
    print("\n🔹 [4/5] Saramin 크롤링 중...")
    # 0 = 경력무관, 1 = 신입, 2 = 1~3년 경력
    for c_type in [0, 1, 2]:
        saramin_crawler(c_type, SARAM_HEADERS)
    print("✅ Saramin 크롤링 완료!\n")

    time.sleep(1)

    # JobKorea 크롤러 실행
    # 1 = 신입, 2 = 경력, 4 = 경력무관
    print("\n🔹 [5/5] JobKorea 크롤링 중...")
    for c_type in [1, 2, 4]:
        job_korea_crawler(c_type, JP_HEADERS)
    print("\n✅ JobKorea 크롤링 완료!\n")

    print("\n🎉 모든 크롤링 작업 완료!\n")

if __name__ == "__main__":
    main()
