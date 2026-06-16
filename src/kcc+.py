"""
prediction_comparison.py

각 방법(Tag, Semantic, WL h=1/2/3)의 val 예측 결과를 모아
어떤 샘플이 어느 방법에서 맞고/틀리는지 비교하는 CSV를 생성.

[출력]
  prediction_comparison.csv  : 샘플별 각 방법 예측 + 정답 + 분석 컬럼
  detection_overlap.csv      : 방법 간 탐지/미탐지 교차 집계
"""

import os
import sys
import pickle
import hashlib
from collections import Counter

import networkx as nx
import pandas as pd
from tqdm import tqdm

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

os.makedirs("results", exist_ok=True)


# ─────────────────────────────────────────────
# 기본 설정 (베이스 코드와 동일)
# ─────────────────────────────────────────────
HTML_TAGS = {
    "html", "head", "body",
    "div", "span", "section", "article", "nav",
    "header", "footer", "main",
    "p", "a",
    "form", "input", "button", "label",
    "textarea", "select", "option",
    "img", "iframe", "script", "link",
    "table", "tr", "td", "th",
    "ul", "li"
}


# ─────────────────────────────────────────────
# 그래프 로드 (베이스 코드와 동일 - sorted 없음)
# ─────────────────────────────────────────────
def load_graphs(path):
    graphs, labels, filenames = [], [], []
    for label in ["Phish", "NotPhish"]:
        label_path = os.path.join(path, label)
        for file in os.listdir(label_path):      # sorted 없음 - 베이스 코드와 동일
            if not file.endswith(".pkl"):
                continue
            with open(os.path.join(label_path, file), "rb") as f:
                G = pickle.load(f)
            if G.number_of_nodes() > 10000:
                continue
            graphs.append(G)
            labels.append(1 if label == "Phish" else 0)
            filenames.append(f"{label}/{file}")   # ← 파일명 저장
    return graphs, labels, filenames


def get_node_label(G, n):
    data = G.nodes[n]
    if "label" in data:  return str(data["label"]).strip().lower()
    if "tag"   in data:  return str(data["tag"]).strip().lower()
    if "name"  in data:  return str(data["name"]).strip().lower()
    return "unk"


# ─────────────────────────────────────────────
# Feature 추출 함수 (베이스 코드와 동일)
# ─────────────────────────────────────────────
def extract_semantic_label_set(graphs, min_freq=5):
    counter = Counter()
    for G in tqdm(graphs, desc="Semantic label extraction"):
        for n in G.nodes():
            lbl = get_node_label(G, n)
            if lbl not in HTML_TAGS:
                counter[lbl] += 1
    return {lbl for lbl, freq in counter.items() if freq >= min_freq}


def tag_count_features(G):
    features = Counter()
    total = G.number_of_nodes()
    if total == 0:
        return features
    for n in G.nodes():
        lbl = get_node_label(G, n)
        if lbl in HTML_TAGS:
            features[lbl] += 1
    for k in features:
        features[k] /= total
    return features


def semantic_count_features(G, semantic_label_set):
    features = Counter()
    total = G.number_of_nodes()
    if total == 0:
        return features
    for n in G.nodes():
        lbl = get_node_label(G, n)
        if lbl in semantic_label_set:
            features[lbl] += 1
    for k in features:
        features[k] /= total
    return features


def wl_features(G, h=3, max_neigh=5):
    labels = {n: get_node_label(G, n) for n in G.nodes()}
    features = Counter(labels.values())
    for _ in range(h):
        new_labels = {}
        for node in G.nodes():
            neigh = []
            if isinstance(G, nx.DiGraph):
                neigh += [labels[n] for n in G.successors(node)]
            else:
                neigh += [labels[n] for n in G.neighbors(node)]
            neigh.sort()
            neigh = neigh[:max_neigh]
            combined = labels[node] + "_" + "_".join(neigh)
            new_labels[node] = hashlib.md5(combined.encode()).hexdigest()
        labels = new_labels
        features.update(labels.values())
    return features


def build_feature_matrix(graphs, mode, vocab=None, top_k=3000,
                          h=3, max_neigh=5, semantic_label_set=None):
    all_features = []
    for G in tqdm(graphs, desc=f"Features [{mode}]"):
        if mode == "tag":
            f = tag_count_features(G)
        elif mode == "semantic":
            f = semantic_count_features(G, semantic_label_set)
        elif mode == "wl":
            f = wl_features(G, h=h, max_neigh=max_neigh)
        all_features.append(f)

    if vocab is None:
        cnt = Counter()
        for f in all_features:
            cnt.update(f)
        vocab = [feat for feat, _ in cnt.most_common(top_k)]

    rows = [[f.get(v, 0) for v in vocab] for f in all_features]
    return pd.DataFrame(rows, columns=vocab), vocab


def train_and_predict(X_train, y_train, X_val):
    clf = RandomForestClassifier(n_estimators=200, n_jobs=1, random_state=42)
    clf.fit(X_train, y_train)
    return clf.predict(X_val)


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
train_path = "D:/paper/website/pkl/training"
val_path   = "D:/paper/website/pkl/validation"

print("Loading graphs...")
train_graphs, train_labels, _              = load_graphs(train_path)
val_graphs,   val_labels,   val_filenames  = load_graphs(val_path)

print(f"Train: {len(train_graphs)}  Val: {len(val_graphs)}")

# semantic label set
semantic_label_set = extract_semantic_label_set(train_graphs, min_freq=5)

# ── 결과를 담을 DataFrame 뼈대 ───────────────
result_df = pd.DataFrame({
    "filename":   val_filenames,
    "true_label": val_labels,          # 1=Phish, 0=NotPhish
})

# ── 각 방법별 예측 ───────────────────────────
methods = [
    ("tag",      dict(mode="tag")),
    ("semantic", dict(mode="semantic", semantic_label_set=semantic_label_set)),
    ("wl_h1",    dict(mode="wl", h=1)),
    ("wl_h2",    dict(mode="wl", h=2)),
    ("wl_h3",    dict(mode="wl", h=3)),
]

for name, kwargs in methods:
    print(f"\n[{name}] feature extraction & prediction")
    X_tr, vocab = build_feature_matrix(train_graphs, **kwargs)
    X_vl, _     = build_feature_matrix(val_graphs, vocab=vocab, **kwargs)

    preds = train_and_predict(X_tr, train_labels, X_vl)
    result_df[f"pred_{name}"] = preds

    acc = accuracy_score(val_labels, preds)
    print(f"  Accuracy: {acc:.4f}")

# ─────────────────────────────────────────────
# 분석 컬럼 추가
# ─────────────────────────────────────────────
pred_cols = [f"pred_{n}" for n, _ in methods]

# 각 샘플이 몇 개 방법에서 Phish로 탐지됐는지
result_df["phish_detect_count"] = result_df[pred_cols].sum(axis=1)

# 정오표 컬럼 (1=정답, 0=오답)
for name, _ in methods:
    result_df[f"correct_{name}"] = (
        result_df[f"pred_{name}"] == result_df["true_label"]
    ).astype(int)

# 모든 방법이 맞춘 경우
correct_cols = [f"correct_{n}" for n, _ in methods]
result_df["all_correct"] = (result_df[correct_cols].sum(axis=1) == len(methods)).astype(int)



# 분류 유형
def classify_case(row):
    true = row["true_label"]
    preds = {n: row[f"pred_{n}"] for n, _ in methods}

    all_correct = all(p == true for p in preds.values())
    all_wrong   = all(p != true for p in preds.values())

    if all_correct:
        return "all_correct"
    elif all_wrong:
        return "all_wrong"
    else:
        # 어떤 방법이 탐지하고 어떤 방법이 못하는지
        detected     = [n for n, p in preds.items() if p == true]
        not_detected = [n for n, p in preds.items() if p != true]
        return f"detected_by({'|'.join(detected)})__missed_by({'|'.join(not_detected)})"

result_df["case_type"] = result_df.apply(classify_case, axis=1)

# ─────────────────────────────────────────────
# 저장
# ─────────────────────────────────────────────
out_path = "results/prediction_comparison.csv"
result_df.to_csv(out_path, index=False)
print(f"\nSaved: {out_path}  ({len(result_df)} rows)")

# ── 요약 출력 ─────────────────────────────────
print("\n" + "="*55)
print("케이스 유형별 집계:")
print(result_df["case_type"].value_counts().to_string())

# ── 방법 간 교차 탐지 비교표 ─────────────────
print("\n" + "="*55)
print("Phish 샘플만 - 각 방법 탐지 여부 조합 집계:")
phish_df = result_df[result_df["true_label"] == 1].copy()
detect_cols = [f"pred_{n}" for n, _ in methods]
combo = phish_df[detect_cols].apply(tuple, axis=1).value_counts()
combo.index = [str(dict(zip([n for n,_ in methods], c))) for c in combo.index]
print(combo.to_string())

# ── overlap CSV ───────────────────────────────
overlap_rows = []
for i, (n1, _) in enumerate(methods):
    for n2, _ in methods[i+1:]:
        both    = ((result_df[f"pred_{n1}"] == 1) & (result_df[f"pred_{n2}"] == 1)).sum()
        only_n1 = ((result_df[f"pred_{n1}"] == 1) & (result_df[f"pred_{n2}"] != 1)).sum()
        only_n2 = ((result_df[f"pred_{n1}"] != 1) & (result_df[f"pred_{n2}"] == 1)).sum()
        neither = ((result_df[f"pred_{n1}"] != 1) & (result_df[f"pred_{n2}"] != 1)).sum()
        overlap_rows.append({
            "method_A": n1, "method_B": n2,
            "both_phish": both,
            f"only_{n1}": only_n1,
            f"only_{n2}": only_n2,
            "neither_phish": neither,
        })

overlap_df = pd.DataFrame(overlap_rows)
overlap_df.to_csv("results/detection_overlap.csv", index=False)
print(f"\nSaved: results/detection_overlap.csv")

print("\n" + "="*55)
print("전체 샘플 기준 1:1 Correct 비교:")

for i, (n1, _) in enumerate(methods):
    for n2, _ in methods[i+1:]:
        better_n1 = ((result_df[f"correct_{n1}"] == 1) & (result_df[f"correct_{n2}"] == 0)).sum()
        better_n2 = ((result_df[f"correct_{n1}"] == 0) & (result_df[f"correct_{n2}"] == 1)).sum()

        print(f"{n1} vs {n2}  →  {n1}: {better_n1}, {n2}: {better_n2}")

print("\nDone.")
sys.exit()