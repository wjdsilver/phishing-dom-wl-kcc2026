# DOM Graph-Based Phishing Detection using WL Subtree Features

This repository contains the implementation of our KCC 2026 paper.

## Overview

Traditional phishing detection methods often rely on URL or content features.
This work investigates whether structural information contained in the DOM tree can be used to distinguish phishing webpages from benign webpages.

We represent each webpage as a DOM graph and extract Weisfeiler-Lehman (WL) subtree features.
The resulting feature vectors are used for phishing classification.

## Pipeline

HTML Page
→ DOM Tree Construction
→ Graph Conversion
→ WL Subtree Feature Extraction
→ Classification
→ Evaluation

## Features

- DOM statistics
- HTML tag counts
- Semantic label counts
- WL subtree patterns

## Publication
### 논문, KCC 2026 한국컴퓨터종합학술대회 논문집 (1,509 - 1,510)
> **[KCC 2026 한국컴퓨터종합학술대회 논문집 (1,509 - 1,510) : DOM 구조 기반 Graph Feature를 이용한 Phishing 웹페이지
탐지](https://github.com/user-attachments/files/29327766/KCC2026_15_505_DOM.Graph.Feature.Phishing.pdf)**
>
## Poster Presentation
### KCC 2026 Poster Session
This work was presented at the KCC 2026 poster session.
<img width="800" alt="KCC포스터" src="https://github.com/user-attachments/assets/c38c7e2a-c5ac-4980-b180-bf82d1205fe7" />

