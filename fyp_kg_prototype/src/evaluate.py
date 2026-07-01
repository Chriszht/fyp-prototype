from collections import Counter


def precision_recall_f1(predicted: set[tuple], gold: set[tuple]) -> dict:
    true_positive = len(predicted & gold)
    false_positive = len(predicted - gold)
    false_negative = len(gold - predicted)

    precision = true_positive / (true_positive + false_positive) if predicted else 0.0
    recall = true_positive / (true_positive + false_negative) if gold else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0

    return {
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "true_positive": true_positive,
        "false_positive": false_positive,
        "false_negative": false_negative,
    }


def relation_distribution(relations: list[dict]) -> dict:
    counter = Counter(item["type"] for item in relations)
    return dict(counter)


if __name__ == "__main__":
    predicted_entities = {
        ("bert", "method"),
        ("question answering", "task"),
        ("language inference", "task"),
    }
    gold_entities = {
        ("bert", "method"),
        ("question answering", "task"),
        ("natural language inference", "task"),
    }
    print(precision_recall_f1(predicted_entities, gold_entities))
