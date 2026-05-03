import pandas as pd

from track_preprocessing import df as track_df

from cluster_preprocessing import clusterToDegree, subjectToCluster
from track_preprocessing import get_track_scores

# id,degree,university,gpa,year,subjects,experience_years,experience_role,additional_info,strengths,sop
df = pd.read_csv("./data/test.csv")

# Preprocessing
df["subjects"] = df["subjects"].apply(lambda x : [i.strip().lower() for i in x.split(';')])
df["strengths"] = df["strengths"].apply(lambda x : [i.strip().lower() for i in x.split(';')])
df["sop"] = df["sop"].apply(lambda x : [i.strip().lower() for i in x.split(';')])

# Adding clusters, degree_scores
def get_clusters(subjects):
    clusters = []
    for subject in subjects:
        if subject in subjectToCluster:
            clusters.append(subjectToCluster[subject])
    return clusters

def get_degree_scores(clusters):
    scores = {"MHA" : 0, "MPH" : 0, "MSHI" : 0, "MBA-HC" : 0}
    for cluster in clusters:
        for degree in clusterToDegree[cluster]:
            scores[degree] += 1
    return scores

def get_strength_scores(strengths):
    scores = {}
    for _, row in track_df.iterrows():
        count = sum(1 if strength in row["keywords"] else 0 for strength in strengths)
        scores[row["track_id"]] = count
    return scores

    
df["clusters"] = df["subjects"].apply(get_clusters)
df["degree_scores"] = df["clusters"].apply(get_degree_scores)
df["track_scores"] = df["sop"].apply(get_track_scores)
df["strength_scores"] = df["sop"].apply(get_strength_scores)

df.head()