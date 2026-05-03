import pandas as pd

# track_id,career_track,degree_fit,keywords
df = pd.read_csv("./data/career_track.csv")

# tracks score
def get_track_scores(sop):
    scores = dict()
    for _, row in df.iterrows():
        count = sum([1 if kw in row["keywords"] else 0 for kw in sop])
        scores[row["track_id"]] = count
    return scores