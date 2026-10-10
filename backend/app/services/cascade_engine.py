import json
import math
import os
from typing import Dict, List


BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)


MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "urban_risk_model.json"
)


# ==========================================================
# LOAD TRAINED ML MODEL
# ==========================================================

def load_model():

    try:

        with open(
            MODEL_PATH,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except (
        FileNotFoundError,
        json.JSONDecodeError,
        OSError
    ):

        return None


ML_MODEL = load_model()


# ==========================================================
# MACHINE LEARNING PREDICTION
# ==========================================================

def predict_ml_risk(weather: Dict) -> Dict:

    if ML_MODEL is None:

        return {
            "available": False,
            "risk_level": "UNAVAILABLE",
            "message": "Trained ML model could not be loaded."
        }


    features = ML_MODEL["features"]

    class_models = ML_MODEL["classes"]

    scores = {}


    for label, class_model in class_models.items():

        score = math.log(
            max(
                class_model["prior"],
                1e-12
            )
        )


        for feature in features:

            value = float(
                weather.get(
                    feature,
                    0
                )
            )


            mean = class_model["means"][feature]

            variance = max(
                class_model["variances"][feature],
                1e-9
            )


            score -= 0.5 * math.log(
                2 * math.pi * variance
            )


            score -= (
                (value - mean) ** 2
            ) / (
                2 * variance
            )


        scores[label] = score


    predicted_class = max(
        scores,
        key=scores.get
    )


    max_score = max(
        scores.values()
    )


    exp_scores = {

        label:
        math.exp(
            score - max_score
        )

        for label, score in scores.items()

    }


    total = sum(
        exp_scores.values()
    )


    probabilities = {

        label:
        round(
            value / total,
            4
        )

        for label, value in exp_scores.items()

    }


    return {

        "available": True,

        "risk_level":
        predicted_class,

        "class_probabilities":
        probabilities,

        "model":
        "Gaussian Naive Bayes",

        "training_data":
        "Synthetic weather dataset"

    }


# ==========================================================
# INFRASTRUCTURE ASSESSMENT
# ==========================================================

def assess_infrastructure(
    weather: Dict
) -> List[Dict]:

    rain = weather.get(
        "rainfall_mm",
        0
    )

    wind = weather.get(
        "wind_speed_kmh",
        0
    )

    lightning = weather.get(
        "lightning_probability",
        0
    )

    thunder = weather.get(
        "thunderstorm_intensity",
        0
    )


    assessments = []


    def add_assessment(
        name,
        score,
        reasons
    ):

        if score >= 70:

            level = "HIGH"

        elif score >= 35:

            level = "MODERATE"

        else:

            level = "LOW"


        assessments.append({

            "name":
            name,

            "risk_level":
            level,

            "risk_score":
            min(
                100,
                round(score)
            ),

            "reasons":
            reasons

        })


    # ------------------------------------------------------
    # POWER GRID
    # ------------------------------------------------------

    power_score = (

        min(
            wind / 100,
            1
        ) * 40

        + lightning * 35

        + thunder * 25

    )


    power_reasons = []


    if wind >= 60:

        power_reasons.append(
            "High wind exposure"
        )


    if lightning >= 0.6:

        power_reasons.append(
            "Elevated lightning exposure"
        )


    if thunder >= 0.7:

        power_reasons.append(
            "Severe thunderstorm estimate"
        )


    if not power_reasons:

        power_reasons.append(
            "No major power-grid hazard threshold reached"
        )


    add_assessment(
        "Power Grid",
        power_score,
        power_reasons
    )


    # ------------------------------------------------------
    # ROAD NETWORK
    # ------------------------------------------------------

    road_score = (

        min(
            rain / 150,
            1
        ) * 70

        + min(
            wind / 120,
            1
        ) * 30

    )


    road_reasons = []


    if rain >= 80:

        road_reasons.append(
            "Heavy rainfall may affect roads"
        )


    if wind >= 60:

        road_reasons.append(
            "High winds may obstruct roads"
        )


    if not road_reasons:

        road_reasons.append(
            "No major road hazard threshold reached"
        )


    add_assessment(
        "Road Network",
        road_score,
        road_reasons
    )


    # ------------------------------------------------------
    # TRAFFIC NETWORK
    # ------------------------------------------------------

    traffic_score = (

        min(
            rain / 150,
            1
        ) * 40

        + min(
            wind / 120,
            1
        ) * 25

        + lightning * 15

        + thunder * 20

    )


    traffic_reasons = []


    if rain >= 50:

        traffic_reasons.append(
            "Rain may reduce road visibility or mobility"
        )


    if wind >= 60:

        traffic_reasons.append(
            "Wind-related road disruption is possible"
        )


    if (
        lightning >= 0.6
        or thunder >= 0.7
    ):

        traffic_reasons.append(
            "Storm conditions may disrupt traffic"
        )


    if not traffic_reasons:

        traffic_reasons.append(
            "No major traffic hazard threshold reached"
        )


    add_assessment(
        "Traffic Network",
        traffic_score,
        traffic_reasons
    )


    # ------------------------------------------------------
    # HOSPITALS
    # ------------------------------------------------------

    hospital_score = (

        min(
            rain / 150,
            1
        ) * 25

        + min(
            wind / 120,
            1
        ) * 20

        + lightning * 20

        + thunder * 20

        + (
            15
            if rain >= 80
            or wind >= 60
            else 0
        )

    )


    hospital_reasons = []


    if rain >= 80:

        hospital_reasons.append(
            "Potential emergency access disruption"
        )


    if (
        wind >= 60
        or thunder >= 0.7
    ):

        hospital_reasons.append(
            "Severe weather may increase response demands"
        )


    if lightning >= 0.6:

        hospital_reasons.append(
            "Elevated storm-related emergency exposure"
        )


    if not hospital_reasons:

        hospital_reasons.append(
            "No major indirect hazard threshold reached"
        )


    add_assessment(
        "Hospitals",
        hospital_score,
        hospital_reasons
    )


    return assessments


# ==========================================================
# DECISION RECOMMENDATIONS
# ==========================================================

def generate_recommendations(
    assessments: List[Dict]
) -> List[Dict]:

    recommendations = []


    for item in assessments:

        name = item["name"]

        level = item["risk_level"]

        score = item["risk_score"]


        # --------------------------------------------------
        # POWER GRID
        # --------------------------------------------------

        if name == "Power Grid":

            if level == "HIGH":

                action = (
                    "Inspect vulnerable power lines, "
                    "prepare backup power systems, "
                    "and monitor electrical infrastructure."
                )

                priority = "IMMEDIATE"

            elif level == "MODERATE":

                action = (
                    "Increase monitoring of power infrastructure "
                    "and prepare maintenance teams."
                )

                priority = "PREPARE"

            else:

                action = (
                    "Continue normal monitoring of the power grid."
                )

                priority = "MONITOR"


        # --------------------------------------------------
        # ROAD NETWORK
        # --------------------------------------------------

        elif name == "Road Network":

            if level == "HIGH":

                action = (
                    "Monitor flood-prone roads, "
                    "prepare traffic diversions, "
                    "and inspect major road corridors."
                )

                priority = "IMMEDIATE"

            elif level == "MODERATE":

                action = (
                    "Monitor drainage conditions and "
                    "prepare possible traffic diversions."
                )

                priority = "PREPARE"

            else:

                action = (
                    "Continue normal road monitoring."
                )

                priority = "MONITOR"


        # --------------------------------------------------
        # TRAFFIC NETWORK
        # --------------------------------------------------

        elif name == "Traffic Network":

            if level == "HIGH":

                action = (
                    "Activate traffic monitoring, "
                    "prepare alternative routes, "
                    "and watch for signal or road disruptions."
                )

                priority = "IMMEDIATE"

            elif level == "MODERATE":

                action = (
                    "Increase traffic monitoring and "
                    "prepare alternative routes."
                )

                priority = "PREPARE"

            else:

                action = (
                    "Continue normal traffic monitoring."
                )

                priority = "MONITOR"


        # --------------------------------------------------
        # HOSPITALS
        # --------------------------------------------------

        elif name == "Hospitals":

            if level == "HIGH":

                action = (
                    "Prepare emergency capacity, "
                    "maintain emergency access routes, "
                    "and coordinate response teams."
                )

                priority = "IMMEDIATE"

            elif level == "MODERATE":

                action = (
                    "Review emergency readiness and "
                    "maintain access for emergency vehicles."
                )

                priority = "PREPARE"

            else:

                action = (
                    "Continue normal emergency preparedness."
                )

                priority = "MONITOR"


        recommendations.append({

            "infrastructure":
            name,

            "risk_level":
            level,

            "risk_score":
            score,

            "priority":
            priority,

            "recommended_action":
            action

        })


    return recommendations


# ==========================================================
# CASCADE ENGINE
# ==========================================================

def calculate_cascade(
    weather: Dict,
    infrastructure: List[Dict]
) -> Dict:

    rainfall = weather.get(
        "rainfall_mm",
        0
    )

    wind = weather.get(
        "wind_speed_kmh",
        0
    )

    lightning = weather.get(
        "lightning_probability",
        0
    )

    thunderstorm = weather.get(
        "thunderstorm_intensity",
        0
    )


    events = []

    cascade_score = 0.0


    # ------------------------------------------------------
    # STAGE 1
    # ------------------------------------------------------

    if thunderstorm >= 0.7:

        events.append({

            "stage": 1,

            "event":
            "Severe Thunderstorm",

            "impact":
            "High atmospheric hazard estimate detected"

        })

        cascade_score += 20


    # ------------------------------------------------------
    # STAGE 2
    # ------------------------------------------------------

    if lightning >= 0.6:

        events.append({

            "stage": 2,

            "event":
            "Lightning Strike Risk",

            "impact":
            "Electrical infrastructure may be exposed"

        })

        cascade_score += 15


    # ------------------------------------------------------
    # STAGE 3
    # ------------------------------------------------------

    if rainfall >= 80:

        events.append({

            "stage": 3,

            "event":
            "Urban Flooding",

            "impact":
            "Drainage capacity may be exceeded"

        })

        cascade_score += 20


    # ------------------------------------------------------
    # STAGE 4
    # ------------------------------------------------------

    if wind >= 60:

        events.append({

            "stage": 4,

            "event":
            "High Wind Damage",

            "impact":
            "Trees, power lines and roads may be exposed"

        })

        cascade_score += 15


    # ------------------------------------------------------
    # STAGE 5
    # ------------------------------------------------------

    if rainfall >= 80 and wind >= 60:

        events.append({

            "stage": 5,

            "event":
            "Power Grid Disruption Risk",

            "impact":
            "Combined storm conditions may affect power infrastructure"

        })

        cascade_score += 10


    # ------------------------------------------------------
    # STAGE 6
    # ------------------------------------------------------

    if rainfall >= 50 or wind >= 50:

        events.append({

            "stage": 6,

            "event":
            "Road and Traffic Disruption",

            "impact":
            "Road mobility and traffic flow may be affected"

        })

        cascade_score += 10


    # ------------------------------------------------------
    # STAGE 7
    # ------------------------------------------------------

    if (
        rainfall >= 80
        or wind >= 60
        or thunderstorm >= 0.7
    ):

        events.append({

            "stage": 7,

            "event":
            "Emergency Response Pressure",

            "impact":
            "Emergency services may experience increased operational demand"

        })

        cascade_score += 10


    cascade_score = min(
        cascade_score,
        100
    )


    if cascade_score >= 80:

        risk_level = "CRITICAL"

    elif cascade_score >= 60:

        risk_level = "HIGH"

    elif cascade_score >= 30:

        risk_level = "MODERATE"

    else:

        risk_level = "LOW"


    infrastructure_assessment = assess_infrastructure(
        weather
    )


    recommendations = generate_recommendations(
        infrastructure_assessment
    )


    ml_prediction = predict_ml_risk(
        weather
    )


    return {

        "cascade_score":
        round(
            cascade_score,
            2
        ),

        "risk_level":
        risk_level,

        "cascade_depth":
        len(events),

        "events":
        events,

        "infrastructure_nodes_analyzed":
        len(infrastructure),

        "infrastructure_assessment":
        infrastructure_assessment,

        "recommendations":
        recommendations,

        "ml_prediction":
        ml_prediction

    }