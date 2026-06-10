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

## Citation

(To be added after publication)
