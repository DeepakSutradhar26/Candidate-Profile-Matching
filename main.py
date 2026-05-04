import json
import pandas as pd

from cluster_preprocessing import clusterToDegree, subjectToCluster
from track_preprocessing import df as track_df, trackToDegree

# Load candidates
candidate_df = pd.read_csv("./data/test.csv")

# Preprocessing
candidate_df["subjects"] = candidate_df["subjects"].apply(
    lambda x: [i.strip().lower() for i in x.split(";")]
)
candidate_df["strengths"] = candidate_df["strengths"].apply(lambda x: x.lower())
candidate_df["experience_role"] = candidate_df["experience_role"].astype(str).str.lower()
candidate_df["sop"] = candidate_df["sop"].apply(lambda x: x.strip().lower())


# Scoring helpers

def get_clusters(subjects):
    clusters = []
    for subject in subjects:
        if subject in subjectToCluster:
            clusters.append(subjectToCluster[subject])
    return list(set(clusters))


def _keyword_scores(text):
    """Count keyword hits per track in a free-text string."""
    scores = {row["track_id"]: 0 for _, row in track_df.iterrows()}
    if not text or text == "nan":
        return scores
    for _, row in track_df.iterrows():
        scores[row["track_id"]] = sum(1 for kw in row["keywords"] if kw in text)
    return scores


def get_exp_scores(experience):
    return _keyword_scores(experience)


def get_sop_scores(sop):
    return _keyword_scores(sop)


def get_strength_scores(strengths):
    return _keyword_scores(strengths)


def get_final_scores(candidate_row):
    scores = {row["track_id"]: 0 for _, row in track_df.iterrows()}
    for track in scores:
        exp_score      = candidate_row["exp_scores"][track]
        sop_score      = candidate_row["sop_scores"][track]
        strength_score = candidate_row["strength_scores"][track]
        scores[track]  = 0.6 * sop_score + 0.2 * strength_score + 0.2 * exp_score
    return scores


def best_degree_from_profile(row):
    """Fallback degree picker used for T02 (no fixed primary degree)."""
    scores = {"MHA": 0, "MPH": 0, "MSHI": 0, "MBA-HC": 0}
    for cluster in row["clusters"]:
        for degree in clusterToDegree[cluster]:
            scores[degree] += 1.0
    subjects = row["subjects"]
    if any(x in subjects for x in ["finance", "accounting", "economics"]):
        scores["MBA-HC"] += 2.0
    if any(x in subjects for x in ["computer", "data", "python", "sql"]):
        scores["MSHI"] += 2.0
    if any(x in subjects for x in ["public", "community", "policy"]):
        scores["MPH"] += 2.0
    if any(x in subjects for x in ["nursing", "clinical", "medicine"]):
        scores["MHA"] += 2.0
    return max(scores, key=scores.get)


def get_degree_scores(row):
    scores = {"MHA": 0, "MPH": 0, "MSHI": 0, "MBA-HC": 0}
    # Score from subject clusters
    for cluster in row["clusters"]:
        for degree in clusterToDegree[cluster]:
            scores[degree] += 0.5
    # Score from top-3 tracks (weighted: 1st=2.0, 2nd/3rd=0.75)
    for i, track in enumerate(row["top3_tracks"]):
        wt = 2.0 if i == 0 else 0.75
        if track == "T02":
            best_degree = best_degree_from_profile(row)
            scores[best_degree] += wt
        else:
            if trackToDegree[track] is not None:
                scores[trackToDegree[track]] += wt
    return scores


# Apply pipeline 

candidate_df["clusters"]         = candidate_df["subjects"].apply(get_clusters)
candidate_df["exp_scores"]       = candidate_df["experience_role"].apply(get_exp_scores)
candidate_df["sop_scores"]       = candidate_df["sop"].apply(get_sop_scores)
candidate_df["strength_scores"]  = candidate_df["strengths"].apply(get_strength_scores)
candidate_df["final_scores"]     = candidate_df.apply(get_final_scores, axis=1)


def get_top3_tracks(final_scores):
    sorted_tracks = sorted(final_scores.items(), key=lambda x: x[1], reverse=True)
    return [track for track, _ in sorted_tracks[:3]]


candidate_df["top3_tracks"]      = candidate_df["final_scores"].apply(get_top3_tracks)
candidate_df["degree_scores"]    = candidate_df.apply(get_degree_scores, axis=1)
candidate_df["recommended_degree"] = candidate_df["degree_scores"].apply(
    lambda s: max(s, key=s.get)
)


# Track metadata lookup
track_meta = {row["track_id"]: row["career_track"] for _, row in track_df.iterrows()}


# Build JSON from candidate_df

def get_matched_keywords(track_id, candidate_row):
    """Return keywords that actually matched for this track from sop/exp/strengths."""
    kws = set(track_df.loc[track_df["track_id"] == track_id, "keywords"].values[0])
    sop       = candidate_row["sop"]
    exp       = candidate_row["experience_role"]
    strengths = candidate_row["strengths"]
    matched = [kw for kw in kws if kw in sop or kw in exp or kw in strengths]
    return matched


results = []
for _, row in candidate_df.iterrows():
    top3       = row["top3_tracks"]
    rec_degree = row["recommended_degree"]

    entry = {
        "id": row["id"],
        "top_3_career_tracks": [
            {
                "rank": i + 1,
                "track_id": t,
                "career_track": track_meta[t],
                "score": round(row["final_scores"][t], 3),
                "matched_keywords": get_matched_keywords(t, row),
            }
            for i, t in enumerate(top3)
        ],
        "recommended_degree": {
            "degree": rec_degree,
            "degree_scores": {k: round(v, 3) for k, v in row["degree_scores"].items()},
            "academic_clusters": row["clusters"],
        },
    }
    results.append(entry)

output = {"candidates": results}

# Print to console
print(json.dumps(output, indent=2))

# Save to file
import os
os.makedirs("./output", exist_ok=True)
with open("./output/results.json", "w") as f:
    json.dump(output, f, indent=2)

print("\nSaved to ./output/results.json")