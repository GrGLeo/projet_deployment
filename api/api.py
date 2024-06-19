from pydantic import BaseModel
from typing import List
from fastapi import FastAPI
from model import Model
import pandas as pd
from param import description


class CarModel(BaseModel):
    model_key: List[str]
    mileage: List[int]
    engine_power: List[int]
    fuel: List[str]
    paint_color: List[str]
    car_type: List[str]
    private_parking_available: List[bool]
    has_gps: List[bool]
    has_air_conditioning: List[bool]
    automatic_car: List[bool]
    has_getaround_connect: List[bool]
    has_speed_regulator: List[bool]
    winter_tires: List[bool]


app = FastAPI(
        description=description
        )


@app.get('/')
async def index():
    return 'Hello world'


@app.post('/predict')
async def predict(car_model: CarModel):
    x = {
            'model_key': car_model.model_key,
            'mileage': car_model.mileage,
            'engine_power': car_model.engine_power,
            'fuel': car_model.fuel,
            'paint_color': car_model.paint_color,
            'car_type': car_model.car_type,
            'private_parking_available': car_model.private_parking_available,
            'has_gps': car_model.has_gps,
            'has_air_conditioning': car_model.has_air_conditioning,
            'automatic_car': car_model.automatic_car,
            'has_getaround_connect': car_model.has_getaround_connect,
            'has_speed_regulator': car_model.has_speed_regulator,
            'winter_tires': car_model.winter_tires
            }
    print(x)
    y = pd.DataFrame(x)
    model = Model()
    print(model(y))
    return {'prediction': model(y).tolist()}
