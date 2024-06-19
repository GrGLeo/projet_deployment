import streamlit as st
import pandas as pd
import requests
import plotly.express as px


st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ("Analysis", "Simulation", "Price prediction"))

    

if page == 'Analysis':
    df = pd.read_excel('get_around_delay_analysis.xlsx')

    def change_state(state, delay):
        if delay > 1440:
            return 'error'
        elif delay > 0:
            return 'delayed'
        elif delay < 0:
            return 'On time'
        else:
            return state
    
    df['state'] = df.apply(lambda row: change_state(row['state'], row['delay_at_checkout_in_minutes']), axis=1)
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
    delayed_rentals = df[df['state'] == 'delayed'].shape[0]
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

    st.write(f'On the total of {total_rentals} rentals {round((delayed_rentals / total_rentals)*100,2)}% had a delay at checkout.')
    st.write(f'Due to some record having really high delay (>24h) those outlier have been marked as an error.')

    col1, col2 = st.columns(2)
    df_timedelay = df[df['state'] == 'delayed']

    with col1:
        state_counts = df['state'].value_counts()
        state_counts_df = state_counts.reset_index()
        state_counts_df.columns = ['state', 'count']
        fig = px.pie(state_counts_df, names='state', values='count', title='State Distribution')
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
        Q1 = df_timedelay['delay_at_checkout_in_minutes'].quantile(0.25)
        Q3 = df_timedelay['delay_at_checkout_in_minutes'].quantile(0.75)

        IQR = Q3 - Q1

        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR

        df_filtered = df_timedelay[(df_timedelay['delay_at_checkout_in_minutes'] >= lower_bound) & 
                               (df_timedelay['delay_at_checkout_in_minutes'] <= upper_bound)]

        fig = px.box(df_filtered, y='delay_at_checkout_in_minutes', title='Delay at Checkout in Minutes')
        fig.update_yaxes(title='Minutes of delay')
        fig.update_layout(height=400, width=440, margin=dict(l=35, r=10, t=45, b=0))
        st.plotly_chart(fig) 
        st.write('')
        st.write('')
        st.write('')

        st.write('26% of the delayed are between 1 and 19 minute, and 52% are between 1 and 60 minutes')

    st.header('Impact of delay on next rental')
    df_merged = df.merge(df, left_on='previous_ended_rental_id', right_on='rental_id', suffixes=('', '_previous'))
    df_merged = df_merged[['rental_id', 'car_id', 'checkin_type', 'state', 'delay_at_checkout_in_minutes', 
                           'previous_ended_rental_id', 'delay_at_checkout_in_minutes_previous']]
    df_merged.rename(columns={'delay_at_checkout_in_minutes': 'current_delay', 
                              'delay_at_checkout_in_minutes_previous': 'previous_delay'}, inplace=True)

    rental_with_previous = df_merged.shape[0]

    df_merged_late =  df_merged[df_merged['previous_delay'] > 0]
    previous_was_late = df_merged_late.shape[0]
    rental_cancel = df_merged_late[df_merged_late['state'] == 'canceled'].shape[0]
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
       st.write('Rentals follow a past rental')
       st.subheader(rental_with_previous)
       st.write('% on total rentals')
       st.subheader(f'{round((rental_with_previous / total_rentals)*100, 2)}%')
    with col2:
        st.write('Previous rental was late')
        st.subheader(previous_was_late)
        st.write('% on followed past rental')
        st.subheader(f'{round((previous_was_late / rental_with_previous)*100, 2)}%')
    with col3:
        st.write('Cancellation due to delay')
        st.subheader(rental_cancel)
        st.write('% on followed past rental')
        st.subheader(f'{round((rental_cancel / rental_with_previous)*100, 2)}%')

elif page == 'Simulation':
    st.title('Simulation')
    st.write("""
In order to mitigate those issues we’ve decided to implement a minimum delay between two rentals. A car won’t be displayed in the search results if the requested checkin or checkout times are too close from an already booked rental.

It solves the late checkout issue but also potentially hurts Getaround/owners revenues: we need to find the right trade off.
""")

    cols = st.columns(5)
    with cols[0]:
        threshold = st.number_input('threshold', min_value=0, max_value=1000, value=15, step=5)
    with cols[1]:
        scope = st.radio('scope', ['All', 'connect', 'mobile'])

    df = pd.read_excel('get_around_delay_analysis.xlsx')
    df_merged = df.merge(df[['state','delay_at_checkout_in_minutes','previous_ended_rental_id']], left_on='rental_id', right_on='previous_ended_rental_id', suffixes=('', '_next'))
    if scope != 'All':
        df_merged = df_merged[df_merged['checkin_type'] == scope]
    run_simulation = st.button('Run the simulation')
    
    if run_simulation:
        st.write('Hello')
    
    
elif page == 'Price prediction':
    data = pd.read_csv('get_around_pricing_project.csv')
    unique_model_keys = data['model_key'].unique().tolist()
    unique_fuels = data['fuel'].unique().tolist()
    unique_paint_colors = data['paint_color'].unique().tolist()
    unique_car_types = data['car_type'].unique().tolist()

    if 'car_list' not in st.session_state:
        st.session_state['car_list'] = []
    if 'predicted' not in st.session_state:
        st.session_state['predicted'] = False
    if 'cars_df' not in st.session_state:
        st.session_state['cars_df'] = pd.DataFrame()
        st.title("Car Price Prediction")

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

    st.header("Add Car Details")
    with st.form(key='car_form'):
        car_data = add_car()
        submitted = st.form_submit_button(label='Add Car')

    if submitted:
        st.session_state.car_list.append(car_data)
        st.success("Car added successfully!")

    if st.session_state.car_list and not st.session_state.predicted:
        st.subheader("Cars to Predict")
        cars_df = pd.DataFrame(st.session_state.car_list)
        st.write(cars_df)

        if st.button('Predict Prices'):
            cars_dict = {key: [car[key] for car in st.session_state.car_list] for key in st.session_state.car_list[0]}
        
            api_url = "https://getaround-api-lg-b04147e374d7.herokuapp.com/predict"
            response = requests.post(api_url, json=cars_dict)
            if response.status_code == 200:
                prediction = response.json()
                predictions = prediction['prediction']

                cars_df['predicted_price'] = predictions
                st.session_state['cars_df'] = cars_df
                st.session_state['predicted'] = True
            else:
                st.write("Error: Unable to get prediction")

    if st.session_state.predicted:
        st.subheader('Prediction Results')
        st.write(st.session_state.cars_df)
