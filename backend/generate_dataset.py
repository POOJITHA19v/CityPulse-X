import os
import numpy as np
import pandas as pd

np.random.seed(42)
num_samples = 5000

rainfall = np.random.uniform(0, 200, num_samples)
wind_speed = np.random.uniform(0, 150, num_samples)
lightning_probability = np.random.uniform(0, 1, num_samples)
thunderstorm_intensity = np.random.uniform(0, 1, num_samples)

risk_score = (
    (rainfall >= 80) * 20
    + (wind_speed >= 60) * 15
    + (lightning_probability >= 0.6) * 15
    + (thunderstorm_intensity >= 0.7) * 20
    + (
        (rainfall >= 80)
        | (wind_speed >= 60)
        | (lightning_probability >= 0.6)
    ) * 10
)

risk_level = np.where(
    risk_score >= 50,
    "HIGH",
    np.where(risk_score >= 25, "MODERATE", "LOW")
)

data = pd.DataFrame({
    "rainfall_mm": rainfall.round(2),
    "wind_speed_kmh": wind_speed.round(2),
    "lightning_probability": lightning_probability.round(3),
    "thunderstorm_intensity": thunderstorm_intensity.round(3),
    "risk_score": risk_score,
    "risk_level": risk_level
})

output_path = os.path.join(
    os.path.dirname(__file__),
    "data",
    "urban_weather_dataset.csv"
)

os.makedirs(os.path.dirname(output_path), exist_ok=True)
data.to_csv(output_path, index=False)

print("Dataset generated successfully!")
print(f"Total records: {len(data)}")
print(f"Saved to: {output_path}")
print("\nRisk category counts:")
print(data["risk_level"].value_counts())
print("\nFirst five rows:")
print(data.head())
