import streamlit as st 
from dbhelper import DB
import plotly.graph_objects as go 
import plotly.express as px
from datetime import datetime, timedelta
import pandas as pd

# Configure Streamlit page
st.set_page_config(
    page_title="Flight Analytics Dashboard",
    page_icon="✈️",
    layout="wide"
)

# Initialize session state
if 'db' not in st.session_state:
    st.session_state.db = DB()

# Sidebar
with st.sidebar:
    st.title("✈️ Flight Analytics")
    user_option = st.selectbox(
        'Menu',
        ['Dashboard', 'Check Flights', 'Analytics', 'About']
    )

def main_dashboard():
    st.title("Flight Analytics Dashboard")
    
    # Summary metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        with st.container():
            st.metric("Total Airlines", len(st.session_state.db.fetch_airline_freq()[0]))
    with col2:
        st.metric("Total Cities", len(st.session_state.db.fetch_city_names()))
    with col3:
        dates, flights = st.session_state.db.daily_num_flights()
        st.metric("Average Daily Flights", round(sum(flights)/len(flights), 2))

def check_flights():
    st.title('Flight Search')

    col1, col2, col3 = st.columns([2, 2, 1])
    
    city = st.session_state.db.fetch_city_names()
    
    with col1:
        source = st.selectbox('From', sorted(city))
    with col2:
        # Filter out source city from destinations
        dest_cities = [c for c in sorted(city) if c != source]
        destination = st.selectbox('To', dest_cities)
    with col3:
        sort_by = st.selectbox('Sort by', ['Price', 'Duration', 'Dep_time'])

    if st.button('Search Flights', use_container_width=True):
        results = st.session_state.db.fetch_all_flights(source, destination, sort_by)
        if results:
            df = pd.DataFrame(results)
            
            # Price analysis
            st.subheader("Price Analysis")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Lowest Price", f"₹{df['Price'].min():,}")
            with col2:
                st.metric("Average Price", f"₹{int(df['Price'].mean()):,}")
            
            # Display results
            st.dataframe(
                df,
                column_config={
                    "Price": st.column_config.NumberColumn(
                        "Price (₹)",
                        format="₹%d"
                    ),
                    "Duration": "Duration (hrs)",
                    "Dep_time": "Departure Time"
                },
                hide_index=True,
                use_container_width=True
            )
        else:
            st.error("No flights found for this route!")

def show_analytics():
    st.title("Flight Analytics")
    
    tab1, tab2, tab3 = st.tabs(["Airline Distribution", "Busy Airports", "Daily Flights"])
    
    with tab1:
        airline, frequency = st.session_state.db.fetch_airline_freq()
        fig = go.Figure(
            go.Pie(
                labels=airline,
                values=frequency,
                hoverinfo="label+percent",
                textinfo="value"
            )
        )
        fig.update_layout(title="Airline Market Share")
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        city, frequency1 = st.session_state.db.busy_airport()
        fig = px.bar(
            x=city,
            y=frequency1,
            title="Busiest Airports",
            labels={'x': 'City', 'y': 'Number of Flights'}
        )
        st.plotly_chart(fig, theme="streamlit", use_container_width=True)
    
    with tab3:
        date, frequency2 = st.session_state.db.daily_num_flights()
        fig = px.line(
            x=date,
            y=frequency2,
            title="Daily Flight Trends",
            labels={'x': 'Date', 'y': 'Number of Flights'}
        )
        st.plotly_chart(fig, theme="streamlit", use_container_width=True)

def about():
    st.title("About This Project")
    st.write("""
    This Flight Analytics Dashboard provides comprehensive insights into flight operations,
    including:
    
    - **Real-time flight searches** across multiple cities
    - **Price analysis** and comparisons
    - **Interactive visualizations** of airline market share
    - **Airport traffic analysis**
    - **Daily flight trends**
    
    Built with Streamlit and MySQL, this dashboard helps users make informed decisions
    about their travel plans while providing valuable insights into the aviation industry.
    """)

# Route to appropriate function based on user selection
if user_option == 'Dashboard':
    main_dashboard()
elif user_option == 'Check Flights':
    check_flights()
elif user_option == 'Analytics':
    show_analytics()
else:
    about()

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("Made by Shujjad Ali")
