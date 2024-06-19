import streamlit as st
import pandas as pd
import requests

# Load the CSV file for unique dropdown values
data = pd.read_csv('get_around_pricing_project.csv')
unique_model_keys = data['model_key'].unique().tolist()
unique_fuels = data['fuel'].unique().tolist()
unique_paint_colors = data['paint_color'].unique().tolist()
unique_car_types = data['car_type'].unique().tolist()

st.title("Car Price Prediction")

# Initialize session state
if 'car_list' not in st.session_state:
    st.session_state['car_list'] = []
if 'predicted' not in st.session_state:
    st.session_state['predicted'] = False
if 'cars_df' not in st.session_state:
    st.session_state['cars_df'] = pd.DataFrame()

def add_car():
    # Get user input for one car
    model_key = st.selectbox('Model Key', unique_model_keys, key=f'model_key_{len(st.session_state.car_list)}')
    mileage = st.number_input('Mileage', min_value=0, max_value=1000000, value=0, step=1, key=f'mileage_{len(st.session_state.car_list)}')
    engine_power = st.number_input('Engine Power', min_value=0, max_value=1000, value=0, step=1, key=f'engine_power_{len(st.session_state.car_list)}')
    fuel = st.selectbox('Fuel Type', unique_fuels, key=f'fuel_{len(st.session_state.car_list)}')
    paint_color = st.selectbox('Paint Color', unique_paint_colors, key=f'paint_color_{len(st.session_state.car_list)}')
    car_type = st.selectbox('Car Type', unique_car_types, key=f'car_type_{len(st.session_state.car_list)}')
    private_parking_available = st.checkbox('Private Parking Available', key=f'private_parking_available_{len(st.session_state.car_list)}')
    has_gps = st.checkbox('Has GPS', key=f'has_gps_{len(st.session_state.car_list)}')
    has_air_conditioning = st.checkbox('Has Air Conditioning', key=f'has_air_conditioning_{len(st.session_state.car_list)}')
    automatic_car = st.checkbox('Automatic Car', key=f'automatic_car_{len(st.session_state.car_list)}')
    has_getaround_connect = st.checkbox('Has Getaround Connect', key=f'has_getaround_connect_{len(st.session_state.car_list)}')
    has_speed_regulator = st.checkbox('Has Speed Regulator', key=f'has_speed_regulator_{len(st.session_state.car_list)}')
    winter_tires = st.checkbox('Winter Tires', key=f'winter_tires_{len(st.session_state.car_list)}')

    car_data = {
        'model_key': model_key,
        'mileage': mileage,
        'engine_power': engine_power,
        'fuel': fuel,
        'paint_color': paint_color,
        'car_type': car_type,
        'private_parking_available': private_parking_available,
        'has_gps': has_gps,
        'has_air_conditioning': has_air_conditioning,
        'automatic_car': automatic_car,
        'has_getaround_connect': has_getaround_connect,
        'has_speed_regulator': has_speed_regulator,
        'winter_tires': winter_tires
    }
    return car_data

# Form to add multiple cars
st.header("Add Car Details")
with st.form(key='car_form'):
    car_data = add_car()
    submitted = st.form_submit_button(label='Add Car')

# Add the car to the list if the form was submitted
if submitted:
    st.session_state.car_list.append(car_data)
    st.success("Car added successfully!")

# Display the list of cars and predict button if there are cars in the list
if st.session_state.car_list and not st.session_state.predicted:
    st.subheader("Cars to Predict")
    cars_df = pd.DataFrame(st.session_state.car_list)
    st.write(cars_df)

    if st.button('Predict Prices'):
        # Convert the list of cars to a dictionary with list values
        cars_dict = {key: [car[key] for car in st.session_state.car_list] for key in st.session_state.car_list[0]}
        
        api_url = "https://getaround-api-lg-b04147e374d7.herokuapp.com/predict"
        response = requests.post(api_url, json=cars_dict)
        if response.status_code == 200:
            prediction = response.json()
            predictions = prediction['prediction']

            # Add the predictions to the DataFrame
            cars_df['predicted_price'] = predictions
            st.session_state['cars_df'] = cars_df
            st.session_state['predicted'] = True
        else:
            st.write("Error: Unable to get prediction")

# Display the DataFrame with predictions if predictions have been made
if st.session_state.predicted:
    st.subheader('Prediction Results')
    st.write(st.session_state.cars_df)
