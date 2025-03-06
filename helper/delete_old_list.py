import shutil
import os

def delete_folder_contents(folder_path):
    """ 특정 폴더 내 모든 파일과 하위 폴더 삭제 """
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)  # 폴더 전체 삭제
        print(f"🗑️ {folder_path} 폴더 내 모든 파일 삭제 완료!")
    
    os.makedirs(folder_path, exist_ok=True)  # 폴더 다시 생성
    print(f"📂 {folder_path} 폴더 다시 생성 완료!")
