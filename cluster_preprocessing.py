import pandas as pd

# cluster_id,cluster_name,subjects,best_fit_degrees
df = pd.read_csv("./data/subject_cluster.csv")

# Preprocessing
df["subjects"] = df["subjects"].apply(lambda x: [i.strip().lower() for i in x.split(";")])
df["best_fit_degrees"] = df["best_fit_degrees"].apply(lambda x: [i.strip() for i in x.split(";")])

# Mapping subject to cluster_id
subjectToCluster = dict()
for _, row in df.iterrows():
    for subject in row["subjects"]:
        subjectToCluster[subject] = row["cluster_id"]

# Mapping cluster_id to degree
clusterToDegree = dict()
for _, row in df.iterrows():
    clusterToDegree[row["cluster_id"]] = row["best_fit_degrees"]