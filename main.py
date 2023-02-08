from fastapi import FastAPI
from pydantic import BaseModel
from pygrowup import Observation
from datetime import datetime
import math


class BabyData(BaseModel):
    date_of_birth: str
    measurement_date: str
    sex: str
    weight: float
    height: float
    bmi: float = 0.0


app = FastAPI()


def zptile(z_score):
    return f'{round((.5 * (math.erf(float(z_score) / 2 ** .5) + 1))*100)}%'


@app.post("/api/v1/bmi")
def get_bmi_data(baby: BabyData):

    age_in_days = (datetime.fromisoformat(baby.measurement_date)-datetime.fromisoformat(baby.date_of_birth)).days

    obs = Observation(sex=baby.sex, age_in_days=age_in_days)

    baby.bmi = baby.weight / ((baby.height / 100) ** 2)

    measurements = {
        "length_or_height_for_age": obs.length_or_height_for_age(baby.height),
        "weight_for_age": obs.weight_for_age(baby.weight),
        "weight_for_length": obs.weight_for_length(baby.weight, baby.height),

        # TODO: Introduce child height handling for toddlers
        # "weight_for_height": obs.weight_for_height(Decimal(baby.weight), Decimal(baby.height)),

        "bmi_for_age": obs.bmi_for_age(baby.weight / ((baby.height / 100) ** 2))
    }

    percentiles = {}

    for key in measurements.keys():
        percentiles[key] = zptile(measurements[key])

    return {
        "baby": baby,
        "measurements": measurements,
        "percentiles": percentiles
    }
