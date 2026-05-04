# CARA — Candidate Profile Matching

A rule-based classifier that reads a candidate's academic background, work experience, behavioral strengths, and statement of purpose, then recommends the best-fit healthcare graduate degree and top 3 career tracks.

Built as part of the **Curavolv AI & Software Development Internship — Phase 1 Assessment**.

## Origin

This project was originally developed as a **Kaggle notebook**.
👉 [View the original Kaggle notebook here](https://www.kaggle.com/code/deep262003/no-ml-profile-matching-pipeline)

The notebook was then converted into this structured Python repository. I used AI assistance only for:
- Converting the Kaggle notebook into a modular repo structure
- Understanding Python syntax in specific places

**All classification logic, scoring weights, keyword augmentation strategy, and degree/track mapping decisions were designed by me independently. This README was also written with AI assistance.**

## What It Classifies

**4 Degree Types**

| Degree | Full Name | Focus |
|--------|-----------|-------|
| MHA | Master of Health Administration | Provider ops, hospital leadership |
| MPH | Master of Public Health | Population health, epidemiology, policy |
| MSHI | Master of Science in Health Informatics | Health IT, data systems, EHR |
| MBA-HC | MBA with Healthcare Concentration | Finance, strategy, entrepreneurship |

**11 Career Tracks** — T01 through T11, covering areas from Healthcare Administration and Consulting to Digital Health Informatics, Health Policy, and Entrepreneurship.

## How It Works

### Pipeline Overview

```
test.csv  ──►  Preprocessing  ──►  Scoring  ──►  Top 3 Tracks  ──►  Recommended Degree  ──►  results.json
```

### Scoring Logic

Each candidate is scored against all 11 career tracks using three signals:

| Signal | Weight | Source |
|--------|--------|--------|
| SOP (Statement of Purpose) | 60% | `sop` column |
| Experience Role | 20% | `experience_role` column |
| Strengths | 20% | `strengths` column |

Scoring is keyword-based — each track has a list of cleaned keywords, and hits are counted across the three fields.

### Degree Recommendation

Degree scores are computed from two sources:
1. **Subject clusters** — each subject maps to a cluster (C1–C10), and each cluster maps to best-fit degrees
2. **Top 3 tracks** — the primary degree of the top track gets weight `2.0`; 2nd and 3rd get `0.75` each

Special case: Track T02 (Consulting) has no fixed primary degree — the best degree is inferred from the candidate's subject profile.

## Project Structure

```
├── data/
│   ├── subject_cluster.csv     # Cluster → subjects → degrees mapping
│   ├── career_track.csv        # Track → keywords → degree fit
│   └── test.csv                # Candidate profiles
├── output/
│   └── results.json            # Generated classification output
├── cluster_preprocessing.py    # Builds subjectToCluster and clusterToDegree dicts
├── track_preprocessing.py      # Cleans track keywords, builds trackToDegree map
├── main.py                     # Full pipeline — scoring, ranking, JSON output
└── README.md
```

## Running It

```bash
pip install pandas
python main.py
```

Output is printed to console and saved to `./output/results.json`.

## Output Format

```json
{
  "candidates": [
    {
      "id": "Sample_MBA_Finance_01",
      "top_3_career_tracks": [
        {
          "rank": 1,
          "track_id": "T03",
          "career_track": "Healthcare Finance, Payer Strategy & Value-Based Care",
          "score": 1.2,
          "matched_keywords": ["revenue cycle", "payer", "audit", "economics"]
        },
        ...
      ],
      "recommended_degree": {
        "degree": "MBA-HC",
        "degree_scores": { "MHA": 0.5, "MPH": 0.75, "MSHI": 0.0, "MBA-HC": 2.5 },
        "academic_clusters": ["C5"]
      }
    }
  ]
}
```

## Test Candidates

| ID | Background | Expected Degree |
|----|-----------|-----------------|
| Sample_FreshGrad_01 | BDS, Maharashtra | MHA |
| Sample_MPH_Community_01 | BA Sociology, Mumbai | MPH |
| Sample_MBA_Finance_01 | BCom Finance, Symbiosis | MBA-HC |
| Sample_MSHI_Tech_01 | BTech CS, VIT Vellore | MSHI |
| Sample_MHA_LTC_01 | BSc Nursing, AIIMS Delhi | MHA |
| Sample_MPH_Policy_01 | BA Political Science, St. Xavier's | MPH |

## AI Usage Disclosure

As required by the assessment guidelines, here is a full disclosure of where AI was used:

- ✅ Converting Kaggle notebook to a modular Python repo structure
- ✅ Python syntax help (e.g. lambda expressions, dict comprehensions)
- ✅ Writing this README

- ❌ Classification logic and scoring weights — designed independently
- ❌ Keyword augmentation strategy — designed independently  
- ❌ Degree/track mapping decisions — designed independently
- ❌ The core matching pipeline — designed independently