import os

src_root = "D:/paper/website/LLM/generated_html"
dst_root = "D:/paper/website/txt/llm"

for root, dirs, files in os.walk(src_root):
    for file in files:
        if not file.endswith(".html"):
            continue

        # 원본 전체 경로
        src_path = os.path.join(root, file)

        # 상대 경로 (gpt/xxx.html 이런거 유지용)
        rel_path = os.path.relpath(root, src_root)

        # 목적지 폴더 생성
        dst_dir = os.path.join(dst_root, rel_path)
        os.makedirs(dst_dir, exist_ok=True)

        # 파일 이름 변경 (.html → .txt)
        new_name = file[:-5] + ".txt"
        dst_path = os.path.join(dst_dir, new_name)

        # 이동 + 이름 변경
        os.rename(src_path, dst_path)

        print(f"{src_path} → {dst_path}")

print("✅ Done.")