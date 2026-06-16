#txt로 되어있는거에서 DOM그래프 구해서 pkl로 저장
import os
import pickle
from tqdm import tqdm
from bs4 import BeautifulSoup
import networkx as nx

def get_node_label(tag):

    name = tag.name

    # input type
    if name == "input":
        t = tag.get("type")
        if t:
            return f"input_{t}"
        return "input"

    # form login
    if name == "form":
        action = tag.get("action")
        if action and "login" in action.lower():
            return "form_login"
        return "form"

    # iframe external
    if name == "iframe":
        src = tag.get("src")
        if src and "http" in src:
            return "iframe_external"
        return "iframe"

    # script external
    if name == "script":
        src = tag.get("src")
        if src:
            return "script_external"
        return "script"

    # link external
    if name == "a":
        href = tag.get("href")
        if href and "http" in href:
            return "a_external"
        return "a"

    return name


# HTML → DOM Graph 변환
def html_to_graph(html):

    soup = BeautifulSoup(html, "lxml")

    G = nx.DiGraph()

    node_id = 0

    def dfs(tag, parent=None):
        nonlocal node_id

        current = node_id
        label = get_node_label(tag)
        G.add_node(current, label=label)

        node_id += 1

        if parent is not None:
            G.add_edge(parent, current)

        for child in tag.children:
            if child.name:
                dfs(child, current)

    # ⭐ root를 html tag로 잡기
    root = soup.find("html")

    if root is None:
        root = soup

    dfs(root)

    return G


# 전체 dataset 처리
def process_dataset(txt_root, pkl_root):

    for split in os.listdir(txt_root):

        split_path = os.path.join(txt_root, split)

        if not os.path.isdir(split_path):
            continue

        print(f"\nProcessing split: {split}")

        for label in os.listdir(split_path):

            label_path = os.path.join(split_path, label)

            if not os.path.isdir(label_path):
                continue

            print(f"  Label: {label}")

            # pkl 저장 폴더
            save_path = os.path.join(pkl_root, split, label)
            os.makedirs(save_path, exist_ok=True)

            files = os.listdir(label_path)

            for file in tqdm(files):

                if not file.endswith(".txt"):
                    continue

                txt_path = os.path.join(label_path, file)

                # txt 이름 그대로 사용
                pkl_name = os.path.splitext(file)[0] + ".pkl"
                pkl_path = os.path.join(save_path, pkl_name)

                # 이미 존재하면 skip
                if os.path.exists(pkl_path):
                    continue

                try:
                    with open(txt_path, "r", encoding="utf-8", errors="ignore") as f:
                        html = f.read()

                    G = html_to_graph(html)

                    with open(pkl_path, "wb") as f:
                        pickle.dump(G, f)

                except Exception as e:
                    print("Error:", txt_path, e)


# 실행
if __name__ == "__main__":

    txt_root = "D:/paper/website/txt"
    pkl_root = "D:/paper/website/pkl"

    process_dataset(txt_root, pkl_root)

    print("\nDOM Graph Extraction 완료")