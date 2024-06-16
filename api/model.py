import os
import logging
import pickle
import pandas as pd
from sklearn.preprocessing import StandardScaler, OneHotEncoder
# from sklearn.impute import SimpleImputer, KNNImputer
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LinearRegression


class Model:
    def __init__(self):
        self.file = 'model.pkl'
        if os.path.exists(self.file):
            logging.warning('... Loading model ...')
            self.model = self._load_model()
        else:
            logging.warning('... Initializing model ...')
            self.model = self._initialize_model()
            self._train()
            self._save_model()

    def _load_model(self):
        with open(self.file, 'rb') as f:
            model = pickle.load(f)
        return model

    def _save_model(self):
        with open(self.file, 'wb') as f:
            pickle.dump(self.model, f)

    def _train(self):
        data = pd.read_csv('get_around_pricing_project.csv', index_col=0)
        X = data.drop('rental_price_per_day', axis=1)
        y = data['rental_price_per_day']

        self.model.fit(X, y)

    def __call__(self, x):
        return self.model.predict(x)

    def _initialize_model(self):
        ohe_columns = ['model_key', 'fuel', 'paint_color', 'car_type']
        scale_columns = ['mileage', 'engine_power']

        ohe_pipe = Pipeline(
                steps=[
                    ('ohe', OneHotEncoder())
                    ]
                )
        scaler_pipe = Pipeline(
                steps=[
                    ('scaler', StandardScaler())
                    ]
                )
        preprocessing = ColumnTransformer(
                transformers=[
                    ('ohe', ohe_pipe, ohe_columns),
                    ('standard', scaler_pipe, scale_columns)
                    ],
                remainder='passthrough'
                )
        ml_pipe = Pipeline(
                steps=[
                    ('preprocessing', preprocessing),
                    ('model', LinearRegression())
                    ]
                )
        return ml_pipe


if __name__ == '__main__':
    model = Model()
    x = {
            'model_key': ['Renault'],
            'mileage': [109839],
            'engine_power': [135],
            'fuel': ['diesel'],
            'paint_color': ['black'],
            'car_type': ['sedan'],
            'private_parking_available': [True],
            'has_gps': [True],
            'has_air_conditioning': [False],
            'automatic_car': [False],
            'has_getaround_connect': [True],
            'has_speed_regulator': [False],
            'winter_tires': [True],
            }
    x = pd.DataFrame(x)
    print(model(x))
