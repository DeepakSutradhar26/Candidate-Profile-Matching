import pandas as pd

# track_id,career_track,degree_fit,keywords
df = pd.read_csv("./data/career_track.csv")

# Unnecessary words removal
last_words = [
    " keywords", " strength", " background", " focus",
    " career goal", " interest", " goal", " evidence", " such",
    " as", " language", "global ", "mental ",
    " trials", " affairs"
]

def get_clean_data(keywords):
    results = []
    for sentence in keywords.split(";"):
        for last in last_words:
            if last in sentence:
                sentence = sentence.replace(last, "")
        if " or " in sentence or "/" in sentence:
            separator = " or " if "or" in sentence else "/"
            splited = sentence.split(separator)
            first = splited[0]
            second = splited[1].split(" ")[0]
            rest = splited[1][splited[1].index(" ") + 1:] if " " in splited[1] else ""
            results.append(str(first + " " + rest).strip())
            results.append(str(second + " " + rest).strip())
        else:
            results.append(sentence.strip())
        for i in range(len(results)):
            if not results[i].isupper():
                results[i] = results[i].lower()
    return results

# Manual keyword augmentations (from reference)
df.loc[df["track_id"] == "T02", "keywords"] += (
    ";consulting;advisory;audit;client;implementation;economics;"
    "revenue cycle;honesty;software developer;fhir"
)
df.loc[df["track_id"] == "T03", "keywords"] += ";payer"
df.loc[df["track_id"] == "T04", "keywords"] += ";care program"
df.loc[df["track_id"] == "T05", "keywords"] += ";large healthcare;government health;care facilities"
df.loc[df["track_id"] == "T07", "keywords"] += ";state health"
df.loc[df["track_id"] == "T11", "keywords"] += ";cfo;audit;technology;health-tech"
df.loc[df["track_id"] == "T05", "keywords"] = df.loc[
    df["track_id"] == "T05", "keywords"
].apply(lambda x: x.replace(";health", ""))

df["degree_fit"] = df["degree_fit"].apply(lambda x: [i.strip() for i in x.split(";")])
df["keywords"] = df["keywords"].apply(lambda x: x.lower())
df["keywords"] = df["keywords"].apply(get_clean_data)

# Mapping track_id to primary degree
trackToDegree = dict()
for _, row in df.iterrows():
    trackToDegree[row["track_id"]] = None
    for degree in row["degree_fit"]:
        if "primary" in degree:
            trackToDegree[row["track_id"]] = degree.split(" ")[0]

# Score helpers used by main.py
def get_track_scores(text_tokens, field="keywords"):
    """Generic scorer: counts keyword hits in a list of tokens against each track."""
    scores = dict()
    for _, row in df.iterrows():
        count = sum(1 for kw in row[field] if kw in text_tokens)
        scores[row["track_id"]] = count
    return scores