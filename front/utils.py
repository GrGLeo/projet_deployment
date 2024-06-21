import numpy as np
import streamlit as st
import pandas as pd
import plotly.express as px


def change_state(state, delay):
    if state == 'ended':
        if delay > 0:
            return 'delayed'
        elif delay <= 0:
            return 'on time'
        else:
            return 'NR'
    elif state == 'canceled':
        return 'canceled'

def get_past_delay(row, df):
    delay = np.nan
    if not np.isnan(row['previous_ended_rental_id']):
        delay = df[df['rental_id'] == row['previous_ended_rental_id']]['delay_at_checkout_in_minutes'].values[0]
    return delay

def get_impact_of_previous_rental_delay(delay, state):
    impact = '-'
    if not np.isnan(delay):
        if delay > 0:
            if state == 'canceled':
                impact = 'cancelation'
            else:
                impact = 'late checkin'
        else:
            impact = 'no impact'
    return impact

def preprocessed_df():
    df = pd.read_excel('get_around_delay_analysis.xlsx')
    df['past_delay'] = df.apply(get_past_delay, args=[df], axis=1)
    df['checkin_delay_in_minutes'] = df['past_delay'] - df['time_delta_with_previous_rental_in_minutes']
    df['state'] = df.apply(lambda row: change_state(row['state'], row['delay_at_checkout_in_minutes']), axis=1)
    df['impact'] = df.apply(lambda row: get_impact_of_previous_rental_delay(row['checkin_delay_in_minutes'], row['state']), axis=1)
    
    return df

def get_outlier(df, col):
    Q1 = df[col].quantile(0.25)
    Q3 = df[col].quantile(0.75)

    IQR = Q3 - Q1

    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    return lower_bound, upper_bound

def run_simulation(df, threshold, scope):
    if scope == 'All':
        applied_threshold = df[df['time_delta_with_previous_rental_in_minutes'] <= threshold]
    else:
        applied_threshold = df[(df['time_delta_with_previous_rental_in_minutes'] <= threshold) & (df['checkin_type'] == scope)]
    cancel_avoided = len(applied_threshold[applied_threshold['impact'] == 'cancelation'])
    lost_rental = len(applied_threshold) - cancel_avoided
    return (
        df.drop(applied_threshold.index),
        lost_rental,
        cancel_avoided
        )

def create_pie(df, col, title):
    counts = df[col].value_counts()
    counts_df = counts.reset_index()
    counts_df.columns = [col, 'count']
    fig = px.pie(counts_df, names=col, values='count', title=title)
    return fig

def add_car(unique_model_keys, unique_fuels, unique_paint_colors, unique_car_types):
    # Get user input for one car
    model_key = st.selectbox('Model Key', unique_model_keys, key=f'model_key_{len(st.session_state.car_list)}')
    mileage = st.slider('Mileage', min_value=0, max_value=1_000_000, value=150_000, step=5, key=f'mileage_{len(st.session_state.car_list)}')
    engine_power = st.slider('Engine Power', min_value=0, max_value=500, value=120, step=5, key=f'engine_power_{len(st.session_state.car_list)}')
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
