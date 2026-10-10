import csv
import json
import math
import os
import random

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "urban_weather_dataset.csv")
MODEL_DIR = os.path.join(BASE_DIR, "models")
MODEL_PATH = os.path.join(MODEL_DIR, "urban_risk_model.json")

FEATURES = [
    "rainfall_mm",
    "wind_speed_kmh",
    "lightning_probability",
    "thunderstorm_intensity"
]

# Load the dataset
with open(DATA_PATH, "r", newline="", encoding="utf-8-sig") as file:
    rows = list(csv.DictReader(file))

random.Random(42).shuffle(rows)

split_index = int(len(rows) * 0.8)
train_rows = rows[:split_index]
test_rows = rows[split_index:]

classes = sorted(set(row["risk_level"] for row in rows))
model = {"features": FEATURES, "classes": {}}

# Train Gaussian Naive Bayes
for label in classes:
    class_rows = [
        row for row in train_rows
        if row["risk_level"] == label
    ]

    class_model = {
        "prior": len(class_rows) / len(train_rows),
        "means": {},
        "variances": {}
    }

    for feature in FEATURES:
        values = [float(row[feature]) for row in class_rows]
        mean = sum(values) / len(values)
        variance = sum((value - mean) ** 2 for value in values) / len(values)

        class_model["means"][feature] = mean
        class_model["variances"][feature] = max(variance, 1e-9)

    model["classes"][label] = class_model


def predict(row):
    scores = {}

    for label, class_model in model["classes"].items():
        score = math.log(class_model["prior"])

        for feature in FEATURES:
            value = float(row[feature])
            mean = class_model["means"][feature]
            variance = class_model["variances"][feature]

            score -= 0.5 * math.log(2 * math.pi * variance)
            score -= ((value - mean) ** 2) / (2 * variance)

        scores[label] = score

    return max(scores, key=scores.get)


# Evaluate on records not used for training
correct = sum(
    predict(row) == row["risk_level"]
    for row in test_rows
)

accuracy = correct / len(test_rows)

print("CITYPULSE X - GAUSSIAN NAIVE BAYES")
print("=" * 40)
print(f"Training records: {len(train_rows)}")
print(f"Testing records: {len(test_rows)}")
print(f"Test accuracy: {accuracy:.2%}")

print("\nClass-wise results:")
for label in classes:
    actual = sum(row["risk_level"] == label for row in test_rows)
    predicted = sum(predict(row) == label for row in test_rows)
    print(f"{label}: {predicted} predictions, {actual} actual records")

os.makedirs(MODEL_DIR, exist_ok=True)

with open(MODEL_PATH, "w", encoding="utf-8") as file:
    json.dump(model, file, indent=2)

print(f"\nModel saved successfully: {MODEL_PATH}")
