import ssl
import os
import pandas as pd
from mlxtend.frequent_patterns import apriori
from mlxtend.frequent_patterns import association_rules
import pickle


def main():
    ssl._create_default_https_context = ssl._create_unverified_context
    url = os.environ["DS_URL"]
    playlists = pd.read_csv(url)

    # One-hot encoding of playlists dataframe
    playlists["value"] = 1
    playlists = playlists.pivot_table(index="pid", columns="track_uri", values="value", fill_value=0)
    playlists = playlists.astype(bool)

    # Generates a dataframe to store association rules
    frequent_itemsets = apriori(playlists, min_support=0.07, use_colnames=True)
    rules = association_rules(frequent_itemsets, metric="lift", min_threshold=1)

    with open("/ml-data/rules.pickle", "wb") as f:
        pickle.dump(rules, f)


if __name__ == "__main__":
    main()