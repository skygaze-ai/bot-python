# Example ingesting the sampled_profiles into SQL

import csv


def parse_follows() -> list:
    follows = []
    with open("data/sampled_follows.csv", "r") as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            follows.append({"did": row[0], "subject_did": row[1]})
    return follows


def ingest_follows(follows: list) -> None:
    # ingest into SQL
    pass


def main() -> None:
    follows = parse_follows()
    ingest_follows(follows)


if __name__ == "__main__":
    main()
