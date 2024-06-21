import os
import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from utils import get_outlier, add_car, preprocessed_df, run_simulation, create_pie


st.set_page_config(
        page_title="GetAround Analysis",
        layout="wide"
    )

st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ("Analysis", "Simulation", "Price prediction"))

@st.cache_data
def load_data():
    df = preprocessed_df()
    df_timedelay = df[df['state'] == 'delayed']  
    df_consecutive = df[df['impact'] != '-']
    return df, df_timedelay, df_consecutive

df, df_timedelay, df_consecutive = load_data()

if page == 'Analysis':
    st.title('Getaround Analysis 🚗')

    st.write("""
When using Getaround, drivers book cars for a specific time period, from an hour to a few days long.
They are supposed to bring back the car on time, but it happens from time to time that drivers are late for the checkout.

Late returns at checkout can generate high friction for the next driver if the car was supposed to be rented again on the same day :
Customer service often reports users unsatisfied because they had to wait for the car to come back from the previous rental or users that
even had to cancel their rental because the car wasn’t returned on time.
""")

    st.header('Main indicators')
    total_rentals = df.shape[0]
    unique_cars = df['car_id'].nunique()
    delayed_rentals = df_timedelay.shape[0]
    col1, col2, col3 = st.columns(3)

    with col1:
        st.write('Total Rentals')
        st.subheader(total_rentals)

    with col2:
        st.write('Unique Cars')
        st.subheader(unique_cars)

    with col3:
        st.write('Delayed Rentals')
        st.subheader(delayed_rentals)
    st.write(f'On the total of {total_rentals} rentals, {round((delayed_rentals / total_rentals)*100, 2)}% had a delay at checkout.')

    col1, col2 = st.columns(2)

    with col1:
        fig = create_pie(df, 'state', 'State Distribution')
        fig.update_layout(height=400, width=440, margin=dict(l=35, r=10, t=45, b=0))
        st.plotly_chart(fig) 

        bin_size = 15
        num_bins = int((df_timedelay['delay_at_checkout_in_minutes'].max() + bin_size) / bin_size)
        fig = px.histogram(df_timedelay, x='delay_at_checkout_in_minutes', nbins=num_bins,
                            title='Distribution of Delay at Checkout in Minutes',
                            histnorm='percent')
        fig.update_xaxes(range=[0, 400])
        st.plotly_chart(fig)
    
    with col2:
        lower_bound, upper_bound = get_outlier(df_timedelay, 'delay_at_checkout_in_minutes')

        df_filtered = df_timedelay[(df_timedelay['delay_at_checkout_in_minutes'] >= lower_bound) & 
                               (df_timedelay['delay_at_checkout_in_minutes'] <= upper_bound)]

        fig = px.box(df_filtered, y='delay_at_checkout_in_minutes', title='Delay at Checkout in Minutes')
        fig.update_yaxes(title='Minutes of delay')
        fig.update_layout(height=400, width=440, margin=dict(l=35, r=10, t=45, b=0))
        st.plotly_chart(fig) 
        st.write('')
        st.write('')
        st.write('')
        st.write('')
        st.write('')

        st.write('''
                 26% of the delayed are between 1 and 19 minute, and 52% are between 1 and 60 minutes. Delay with no consecutive rental
                 doesn't impact the customers, has there is no immediate following customers. But it can impact the car owner if the checkin 
                 type is mobile or paper.
                 ''')
    st.subheader('Checkin type')
    col1, col2 = st.columns(2)
    checkin_type = df['checkin_type'].value_counts()
    checkin_typ_ontime = df[df['state'] != 'delayed']['checkin_type'].value_counts()
    checkin_type_delayed = df_timedelay['checkin_type'].value_counts()
    
    with col1:
        st.metric('Rentals made by mobile', checkin_type.get('mobile', 0))
    with col2:
        st.metric('Rentals made by connected app', checkin_type.get('connect', 0))

    data = {
    'checkin_type': list(checkin_type.index) + list(checkin_type_delayed.index) + list(checkin_typ_ontime.index),
    'count': list(checkin_type.values) + list(checkin_type_delayed.values) + list(checkin_typ_ontime.values),
    'category': ['All rentals'] * len(checkin_type) + ['Delayed rentals'] * len(checkin_type_delayed) + ['On time rentals'] * len(checkin_typ_ontime)
        }

    df_combined = pd.DataFrame(data)
    df_combined['proportion'] = df_combined.groupby('category')['count'].transform(lambda x: x / x.sum())
    col1, col2 = st.columns([0.6, 0.4])
    with col1:  
        fig = px.bar(
            df_combined,
            x='checkin_type',
            y='proportion',
            color='category',
            barmode='group',
            title='Proportion of Check-in Types (All rentals vs. Delayed rentals)',
            labels={'proportion': 'Proportion', 'checkin_type': 'Check-in Type'}
        )
        st.plotly_chart(fig)
    with col2:
        st.write('')
        st.write('')
        st.write('')
        st.write('')
        st.write('')
        st.write('''
                 The proportion of checkin types, stay the almost the same for the delayed checkout out or the on time checkout.  
                 The on time connected rentals are slighty higher (3.7%) than the delayed connected rentals.
                 ''')
    st.header('Impact of delay on next rental')
 
    consecutive_rental = df_consecutive.shape[0]
    was_late = df_consecutive[df_consecutive['impact'] == 'late checkin'].shape[0]
    got_cancel = df_consecutive[df_consecutive['impact'] == 'cancelation'].shape[0]
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric('Consecutive Rentals', consecutive_rental)
        st.metric('% of Total Rentals', f'{round((consecutive_rental / total_rentals)*100, 2)}%')
    with col2:
        st.metric('Previous Rental was Late', was_late)
        st.metric('% of Consecutive Rentals', f'{round((was_late / consecutive_rental)*100, 2)}%')
    with col3:
        st.metric('Cancellation due to Delay', got_cancel)
        st.metric('% of Consecutive Rentals', f'{round((got_cancel / consecutive_rental)*100, 2)}%')

    impact_df = df_consecutive['impact'].value_counts(normalize=True).reset_index()
    fig = px.bar(impact_df, x='impact', y='proportion', title='Impact proportions')
    fig.update_layout(yaxis_title='')

    st.plotly_chart(fig)

elif page == 'Simulation':
    st.title('Simulation')
    st.write("""
In order to mitigate those issues we’ve decided to implement a minimum delay between two rentals.
A car won’t be displayed in the search results if the requested checkin or checkout times are too close from an already booked rental.

It solves the late checkout issue but also potentially hurts Getaround/owners revenues. To find the right trade off we can run simulation and
directly see the potential impact. 
""")

    with st.form(key='simulation_form'):
        cols = st.columns([15,85])
        with cols[0]:   
            threshold = st.number_input('threshold', min_value=0, max_value=1000, value=15, step=15)
        scope = st.radio('scope', ['All', 'connect', 'mobile'])
        run = st.form_submit_button(label='Run the simulation')
    
    if run:
        df_run, lost_rental, cancel_avoided = run_simulation(df_consecutive, threshold, scope)
        col1, col2, col3 = st.columns([0.4, 0.2, 0.4])        
        with col1:
            st.metric('Lost Rentals', lost_rental)
            st.subheader('Distribution of state pre simulation')
            fig = create_pie(df_consecutive, 'impact', '')
            fig.update_layout(height=400, width=440, margin=dict(l=35, r=10, t=45, b=0))
            st.plotly_chart(fig)
            
        with col3:
            st.metric('Cancellations Avoided', cancel_avoided) 
            st.subheader('Distribution of state post simulation')
            fig = create_pie(df_run, 'impact', '')
            fig.update_layout(height=400, width=440, margin=dict(l=35, r=10, t=45, b=0))
            st.plotly_chart(fig)
    
    
elif page == 'Price prediction':
    data = pd.read_csv('get_around_pricing_project.csv')
    unique_model_keys = data['model_key'].unique().tolist()
    unique_fuels = data['fuel'].unique().tolist()
    unique_paint_colors = data['paint_color'].unique().tolist()
    unique_car_types = data['car_type'].unique().tolist()

    if 'car_list' not in st.session_state:
        st.session_state['car_list'] = []
    st.header('Price prediction')
    st.write('''
        Fill in the formule with detail of the car, then add car. The form can be fill multiple time to get more than one prediction at the time.  
        A summary of all added car with details information will be shown once a car is added.
        The price prediction return is made by order of car added.
             ''')
    st.subheader("Add Car Details")
    with st.form(key='car_form'):
        car_data = add_car(unique_model_keys, unique_fuels, unique_paint_colors, unique_car_types)
        submitted = st.form_submit_button(label='Add Car')

    if submitted:
        st.session_state.car_list.append(car_data)
        st.success("Car added successfully!")

    if st.session_state.car_list:
        st.subheader("Cars to estimate")
        cars_df = pd.DataFrame(st.session_state.car_list)
        st.write(cars_df)
        
        col1, col2, _ = st.columns([0.1, 0.2, 0.7])
        with col1:
            make_prediction = st.button('Predict prices')

        with col2:
            empty_car = st.button('Empty the car list')

        if empty_car:
            st.session_state.car_list = []
            st.experimental_rerun()
            
        if make_prediction:
            cars_dict = {key: [car[key] for car in st.session_state.car_list] for key in st.session_state.car_list[0]}
        
            api_url = os.environ['API_URL']
            api_url += "predict"
            response = requests.post(api_url, json=cars_dict)
            if response.status_code == 200:
                prediction = response.json()
                predictions = prediction['prediction']

                for i, pred in zip(cars_df.index,predictions):
                    st.write(f'**Price per day prediction for car {i+1}**: {round(pred,2)}€') 
            else:
                st.write("Error: Unable to get prediction")
