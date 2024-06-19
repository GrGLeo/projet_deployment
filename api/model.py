import os
import logging
import pandas as pd
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from xgboost import XGBRegressor
import mlflow


mlflow.set_tracking_uri(os.environ['APP_URI'])

class Model:
    def __init__(self):
        self.model_name = 'pricing_model'
        if self._is_model_in_production():
            logging.warning('... Loading model from MLflow ...')
            self.model = self._load_model_from_mlflow()
        else:
            logging.warning('... Initializing and training a new model ...')
            self.model = self._initialize_model()
            self._train()
    
    def __call__(self, x):
        return self.model.predict(x)

    def _is_model_in_production(self):
        try:
            client = mlflow.tracking.MlflowClient()
            model_versions = client.get_latest_versions(self.model_name)
            self.model_version = model_versions[0].version
            return len(model_versions) > 0
        except Exception as e:
            logging.error(f"Error checking model in production: {e}")
            return False

    def _load_model_from_mlflow(self):
        try:
            model_uri = f"models:/{self.model_name}/{self.model_version}"
            model = mlflow.sklearn.load_model(model_uri)
            return model
        except Exception as e:
            logging.error(f"Error loading model from MLflow: {e}")
            raise

    def _train(self):
        data = pd.read_csv('get_around_pricing_project.csv', index_col=0)
        X = data.drop('rental_price_per_day', axis=1)
        y = data['rental_price_per_day']

        with mlflow.start_run() as run:

            self.model.fit(X,y)

            mlflow.log_params(self.model.named_steps['model'].get_params())
            mlflow.log_artifact
            mlflow.sklearn.log_model(
                sk_model=self.model,
                artifact_path='sklearn-model',
                registered_model_name=self.model_name,
            )


    def _initialize_model(self):
        ohe_columns = ['model_key', 'fuel', 'paint_color', 'car_type']
        scale_columns = ['mileage', 'engine_power']

        ohe_pipe = Pipeline(
            steps=[
                ('ohe', OneHotEncoder(handle_unknown='ignore'))
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
                ('model', XGBRegressor(learning_rate=0.1,
                                       max_depth=5,
                                       max_leaves=31,
                                       n_estimators=200,
                                       num_parallel_tree=10,
                                       subsample=0.8,
                                       objective='reg:squarederror'))
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
