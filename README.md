# Getaround Analysis
This project was developed as part of a school assignment focused on the deployment aspect of data science. It involves two main components, an analysis on the late checkout and their impact, and an machine learning model to infer a price on a vehicule given information

## Table of Contents

- [Description](#description)
- [Repo architecture](#repo-architecture)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [Contact Information](#contact-information)

## Description
### Analysis of Late Checkouts on Getaround:

- Getaround is a rental car service where late checkouts can pose significant operational challenges.
- The analysis aims to identify the impacts of late checkouts on consecutive rentals.
- This component is implemented using a Streamlit app, providing an interactive and visual interface for data exploration and insights.

### Vehicle Price Prediction Model:

- This part involves building a predictive model to estimate car rental prices based on vehicle details.
- The model is built using XGBoost, a powerful and efficient implementation of the gradient boosting framework.
- The model is served via an API using FastAPI, a modern, fast (high-performance), web framework for building APIs with Python.
- Model versioning and storage are managed with MLflow, ensuring reproducibility and easy deployment.

## Repo architecture
```
.
├── api
│   ├── api.py
│   ├── Dockerfile
│   ├── get_around_pricing_project.csv
│   ├── model.py
│   ├── param.py
│   └── requirements.txt
├── data
│   ├── get_around_delay_analysis.xlsx
│   └── get_around_pricing_project.csv
├── front
│   ├── app.py
│   ├── Dockerfile
│   ├── get_around_delay_analysis.xlsx
│   ├── get_around_pricing_project.csv
│   ├── requirements.txt
│   └── utils.py
├── mlflow
│   ├── Dockerfile
│   └── requirements.txt
├── notebook
│   ├── 01-Getaround_analysis.ipynb
│   ├── exploration.ipynb
│   └── ml.ipynb
├── push_heroku.sh
└── README.md
```

## Installation
Step-by-step instructions on how to get a development environment running.
- Requirements
    - python 3.10+
    - Heroku cli: https://devcenter.heroku.com/articles/heroku-cli

- Clone the repository
```bash
git clone https://github.com/GrGLeo/projet_deploymeny.git
```

- Navigate to the project directory
```bash
cd project_deploymeny
```
- Copy the template.env
```bash
cp template.env .env
```
- Three varialbe need to be filled:
    - AWS_ACCESS_ID
    - AWS_ACCESSS_KEY
    - S3 BUCKET

- To push all to heroku:
```bash
chmod +x push_heroku.sh
./push_heroku.sh
# follow the given link to get to the front app
```

## Usage
On the frontend 3 page can be visited.  
The first one give insight into the Getaround
data and the late chekout, and their effect on the following rental.  
The second page, let the user run simulation and a system to give a windows
between each rental, a car would need be shown to the users, thus to mitigate
the impact on short delayed checkout.  
The third page, is for the price prediction, a form can be filled for each car that
need to be estimate, and the model will predict the price per day for the rental.

## Contributing

Guidelines for contributing to the project.
- Fork the repository.
- Create a new branch (git checkout -b feature/your-feature).
- Make your changes.
- Commit your changes (git commit -m 'Add some feature').
- Push to the branch (git push origin feature/your-feature).
- Open a pull request.

## Contact Information
**GitHub** : GrGLeo
