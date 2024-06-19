import os
import logging
import pandas as pd
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from xgboost import XGBRegressor
from sklearn.model_selection import GridSearchCV
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

        param_grid = {
            'model__n_estimators': [100, 200],
            'model__learning_rate': [0.01, 0.1],
            'model__max_depth': [3, 5, 7],
            'model__subsample': [0.8, 1.0],
            'model__max_leaves': [0, 31, 50], 
            'model__num_parallel_tree': [1, 5, 10]
        }

        grid_search = GridSearchCV(self.model, param_grid, cv=5, scoring='neg_mean_squared_error', verbose=1, n_jobs=-1)

        with mlflow.start_run() as run:
            grid_search.fit(X, y)

            logging.info(f"Best parameters found: {grid_search.best_params_}")
            logging.info(f"Best cross-validation score: {-grid_search.best_score_}")

            mlflow.log_params(grid_search.best_params_)
            mlflow.log_metric("best_neg_mse", -grid_search.best_score_)
            mlflow.sklearn.log_model(
                sk_model=grid_search.best_estimator_,
                artifact_path="sklearn-model",
                registered_model_name=self.model_name,
            )

        self.model = grid_search.best_estimator_

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
                ('model', XGBRegressor(objective='reg:squarederror'))
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
