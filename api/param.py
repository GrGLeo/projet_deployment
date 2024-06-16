description = """
# Prediction API
This API allows users to input various features of cars and obtain predictions based on those features.
    It includes two main endpoints:
    - **Root Endpoint (`/`)**: A simple endpoint to check if the API is running.
    - **Predict Endpoint (`/predict`)**: This endpoint accepts a POST request with car features and returns a prediction.
### Car Features
The prediction endpoint accepts the following car features:
- **model_key**: List of model keys as strings.
- **mileage**: List of mileages as integers.
- **engine_power**: List of engine power values as integers.
- **fuel**: List of fuel types as strings.
- **paint_color**: List of paint colors as strings.
- **car_type**: List of car types as strings.
- **private_parking_available**: List of booleans indicating if private parking is available.
- **has_gps**: List of booleans indicating if GPS is available.
- **has_air_conditioning**: List of booleans indicating if air conditioning is available.
- **automatic_car**: List of booleans indicating if the car is automatic.
- **has_getaround_connect**: List of booleans indicating if Getaround Connect is available.
- **has_speed_regulator**: List of booleans indicating if a speed regulator is available.
- **winter_tires**: List of booleans indicating if the car has winter tires.

### Example
To make a prediction, send a POST request to `/predict` with a JSON payload containing the car features.

**Example Request:**
```json
{
    "model_key": ["Renault", "Mercedes"],
    "mileage": [109369, 180032],
    "engine_power": [135, 105],
    "fuel": ["diesel", "diesel"],
    "paint_color": ["black", "grey"],
    "car_type": ["sedan", "hatchback"],
    "private_parking_available": [true, false],
    "has_gps": [true, true],
    "has_air_conditioning": [true, false],
    "automatic_car": [true, true],
    "has_getaround_connect": [false, true],
    "has_speed_regulator": [true, true],
    "winter_tires": [false, true]
}
```

**Example Response:**
```json
{
    "prediction": [151.57, 159.92]
}
```
"""
