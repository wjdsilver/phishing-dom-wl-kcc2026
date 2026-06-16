## Dataset

This repository does not include the original dataset due to GitHub file size limitations.

The experiments were conducted using the **Phishing Website HTML Classification** dataset available on Kaggle:

https://www.kaggle.com/datasets/huntingdata11/phishing-website-html-classification

The dataset contains HTML files collected from both phishing and benign websites.

---

## Data Preparation

### 1. Download the Dataset

Download and extract the dataset from Kaggle.

### 2. Organize the Dataset

Place the extracted files under the following directory structure:

'''text
data/
├── phishing/
└── benign/'''

### 3. Convert HTML Files to Text

Run the following script to convert HTML files into text format:

'''python src/html2txt.py'''

### 4. Generate Graph Representations

Run the following script to extract graph representations and generate pickle files:

'''python src/graphExtractPerFile.py'''

### 5. Train and Evaluate

After preprocessing, run the training and evaluation scripts provided in this repository.