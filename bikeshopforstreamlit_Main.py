import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import FuncFormatter
import folium
from folium.plugins import MarkerCluster
from IPython.display import display
import streamlit as st
import plotly.express as px

# Load the data
store_data = pd.read_csv('sales_data.csv')

# Data adjustments
store_data['Date'] = pd.to_datetime(store_data['Date'])
store_data['Year'] = store_data['Year'].astype('object')
store_data['Day'] = store_data['Day'].astype('object')

months = ["January", "February", "March", "April", "May", "June", 
          "July", "August", "September", "October", "November", "December"]
store_data['Month'] = pd.Categorical(store_data['Month'], categories=months, ordered=True)

# Custom color palette
custom_colors = ['#f6546a', '#468499', '#81d8d0', '#dddddd', '#f36d5f', '#40e0d0']
countries_ordered = ['United States', 'Canada', 'United Kingdom', 'Australia', 'Germany', 'France']

# Set page configuration to wide mode
st.set_page_config(layout="wide")
st.sidebar.markdown(
    """
    [![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?style=flat-square&logo=linkedin&labelColor=0077B5&logoColor=white)](https://www.linkedin.com/in/mohamed-eldakrory89/)
    """
)
st.sidebar.title("Filters")
# Sidebar filters
selected_country = st.sidebar.selectbox('Select Country', ['All Countries'] + sorted(store_data['Country'].unique().tolist()))

# Check if a country is selected before showing the state filter
if selected_country == 'All Countries':
    selected_state = None
else:
    # If a specific country is selected, show the state filter
    selected_state = st.sidebar.selectbox("Select State", ['All States'] + sorted(store_data[store_data['Country'] == selected_country]['State'].unique().tolist()))

# Add the Product_Category filter
selected_product_category = st.sidebar.selectbox("Select Product Category", ['All Categories'] + sorted(store_data['Product_Category'].unique().tolist()))

# Initialize selected_sub_category
selected_sub_category = None

# Only show the Sub_Category filter when a Product_Category is selected
if selected_product_category != 'All Categories':
    selected_sub_category = st.sidebar.selectbox("Select Sub-Category", ['All Sub-Categories'] + sorted(store_data[store_data['Product_Category'] == selected_product_category]['Sub_Category'].unique().tolist()))

# Filter the data based on the selected country, state, product category, and sub-category
filtered_data = store_data
if selected_country != 'All Countries':
    filtered_data = store_data[store_data['Country'] == selected_country]

    # Only show the state filter when a country is selected
    if selected_state and selected_state != 'All States':
        filtered_data = filtered_data[filtered_data['State'] == selected_state]

# Filter the data based on the selected product category
if selected_product_category != 'All Categories':
    filtered_data = filtered_data[filtered_data['Product_Category'] == selected_product_category]

# Filter the data based on the selected sub-category
if selected_sub_category and selected_sub_category != 'All Sub-Categories':
    filtered_data = filtered_data[filtered_data['Sub_Category'] == selected_sub_category]

# Add filter by Year and Month in the sidebar
selected_year = st.sidebar.selectbox('Filter by Year', ['All Years'] + [str(year) for year in sorted(store_data['Year'].unique())])
if selected_year != 'All Years':
    # Convert 'Month' category to string for sorting
    months_available = store_data[store_data['Year'] == int(selected_year)]['Month'].astype(str).unique()
    # Sort the months based on their order in the calendar year
    month_order = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    months_available = sorted(months_available, key=lambda x: month_order.index(x))
    selected_month = st.sidebar.selectbox('Filter by Month', ['All Months'] + [str(month) for month in months_available])
else:
    selected_month = 'All Months'

# Filter data based on selected Year and Month
if selected_year != 'All Years':
    filtered_data = filtered_data[store_data['Year'] == int(selected_year)]
    if selected_month != 'All Months':
        filtered_data = filtered_data[filtered_data['Month'] == selected_month]

st.markdown(
    """
    <style>
        .st-eg {
            display: inline-block;
            background-color: #FFFFFF;
            color: #468499;  /* Text color is set to white for better visibility on the light blue background */
            padding: 0px;   /* Optional: Add padding for better aesthetics */
            border-radius: 2px; /* Optional: Add border radius for rounded corners */
        }
    </style>
    """,
    unsafe_allow_html=True
)
st.header('Bike Store Sales Dashboard')
## Business Metrics
# Update business metrics based on filtered data
try:
    # Update business metrics based on filtered data
    total_profit = filtered_data['Profit'].sum()
    total_revenues = filtered_data['Revenue'].sum()
    total_expenses = filtered_data['Cost'].sum()
    most_profitable_country = store_data.groupby('Country')['Profit'].sum().idxmax()
    least_profitable_country = store_data.groupby('Country')['Profit'].sum().idxmin()
    most_profitable_subcategory = filtered_data.groupby('Sub_Category')['Profit'].sum().idxmax()
    least_profitable_subcategory = filtered_data.groupby('Sub_Category')['Profit'].sum().idxmin()
    average_age = filtered_data['Customer_Age'].median()
    total_order_quantity = filtered_data['Order_Quantity'].sum()
    num_products_sold = (
        filtered_data[filtered_data['Product_Category'] == 'Accessories']['Product'].nunique() +
        filtered_data[filtered_data['Product_Category'] == 'Bikes']['Product'].nunique() +
        filtered_data[filtered_data['Product_Category'] == 'Clothing']['Product'].nunique()
    )
    st.markdown("---")
    # Display updated business metrics
    st.subheader('Business Metrics')

    col1, col2, col3, col4, col5 = st.columns(5)

    font_size = "16px"

    # Display updated metrics based on filtered data
    with col1:
        st.markdown(f'<div style="color: white; background-color: {custom_colors[0]}; padding: 15px; text-align: center; margin-bottom: 15px; border-radius: 10px;">'
                    f'<h3 style="font-size: {font_size}; ; font-weight: bold;">Total Profits</h3>'
                    f'<p style="font-size: {font_size}; font-weight: bold;">${total_profit:,.2f}</p>'
                    f'</div>', unsafe_allow_html=True)

    # Total Revenue
    with col2:
        st.markdown(f'<div style="color: white; background-color: {custom_colors[1]}; padding: 15px; text-align: center; margin-bottom: 15px; border-radius: 10px;">'
                    f'<h3 style="font-size: {font_size}; font-weight: bold;">Total Revenue</h3>'
                    f'<p style="font-size: {font_size}; font-weight: bold;">${total_revenues:,.2f}</p>'
                    f'</div>', unsafe_allow_html=True)

    # Total Expenses
    with col3:
        st.markdown(f'<div style="color: white; background-color: {custom_colors[0]}; padding: 15px; text-align: center; margin-bottom: 15px; border-radius: 10px;">'
                    f'<h3 style="font-size: {font_size}; font-weight: bold;">Total Expenses</h3>'
                    f'<p style="font-size: {font_size}; font-weight: bold;">${total_expenses:,.2f}</p>'
                    f'</div>', unsafe_allow_html=True)

    # Most Profitable Country
    with col4:
        st.markdown(f'<div style="color: white; background-color: {custom_colors[1]}; padding: 15px; text-align: center; margin-bottom: 15px; border-radius: 10px;">'
                    f'<h3 style="font-size: {font_size}; font-weight: bold;">Most Profitable Country</h3>'
                    f'<p style="font-size: {font_size}; font-weight: bold;">{most_profitable_country}</p>'
                    f'</div>', unsafe_allow_html=True)

    # Least Profitable Country
    with col5:
        st.markdown(f'<div style="color: white; background-color: {custom_colors[0]}; padding: 15px; text-align: center; margin-bottom: 15px; border-radius: 10px;">'
                    f'<h3 style="font-size: {font_size}; font-weight: bold;">Least Profitable Country</h3>'
                    f'<p style="font-size: {font_size}; font-weight: bold;">{least_profitable_country}</p>'
                    f'</div>', unsafe_allow_html=True)

    # Most Profitable Subcategory
    with col1:
        st.markdown(f'<div style="color: white; background-color: {custom_colors[1]}; padding: 15px; text-align: center; margin-bottom: 15px; border-radius: 10px;">'
                    f'<h3 style="font-size: {font_size}; font-weight: bold;">Most Profitable Subcategory</h3>'
                    f'<p style="font-size: {font_size}; font-weight: bold;">{most_profitable_subcategory}</p>'
                    f'</div>', unsafe_allow_html=True)

    # Least Profitable Subcategory
    with col2:
        st.markdown(f'<div style="color: white; background-color: {custom_colors[0]}; padding: 15px; text-align: center; margin-bottom: 15px; border-radius: 10px;">'
                    f'<h3 style="font-size: {font_size}; font-weight: bold;">Least Profitable Subcategory</h3>'
                    f'<p style="font-size: {font_size}; font-weight: bold;">{least_profitable_subcategory}</p>'
                    f'</div>', unsafe_allow_html=True)

    # Average Age of Customers
    with col3:
        st.markdown(f'<div style="color: white; background-color: {custom_colors[1]}; padding: 15px; text-align: center; margin-bottom: 15px; border-radius: 10px;">'
                    f'<h3 style="font-size: {font_size}; font-weight: bold;">Average Age of Customers</h3>'
                    f'<p style="font-size: {font_size}; font-weight: bold;">{average_age:.2f}</p>'
                    f'</div>', unsafe_allow_html=True)

    # Total Orders Quantity
    with col4:
        st.markdown(f'<div style="color: white; background-color: {custom_colors[0]}; padding: 15px; text-align: center; margin-bottom: 15px; border-radius: 10px;">'
                    f'<h3 style="font-size: {font_size}; font-weight: bold;">Total Orders Quantity</h3>'
                    f'<p style="font-size: {font_size}; font-weight: bold;">{total_order_quantity:,}</p>'
                    f'</div>', unsafe_allow_html=True)

    # Number of Products Being Sold
    with col5:
        st.markdown(f'<div style="color: white; background-color: {custom_colors[1]}; padding: 15px; text-align: center; margin-bottom: 15px; border-radius: 10px;">'
                    f'<h3 style="font-size: {font_size}; font-weight: bold;">Number of Products Being Sold</h3>'
                    f'<p style="font-size: {font_size}; font-weight: bold;">{num_products_sold}</p>'
                    f'</div>', unsafe_allow_html=True)

except ValueError as ve:
    st.warning("No data available for the selected filters. Please adjust your filter criteria.")
    st.info('2011 and 2012 had Only Bike Sales')
except Exception as e:
    st.error(f"An error occurred: {e}")

st.markdown("---")
# Add a map with customer demographics
st.subheader('Bike Store Sales Geographical Distribution')

# Function to format currency values in the popup
def format_currency(value, color):
    return f'<span style="color: {color}; font-weight: bold;">${value:,.0f}</span>'

# Map data
country_coordinates = {
    'All Countries': [0, 0],  # Default location for All Countries
    'Australia': [-25.2744, 133.7751],
    'Canada': [56.1304, -106.3468],
    'France': [46.6035, 1.888334],
    'Germany': [51.1657, 10.4515],
    'United Kingdom': [55.3781, -3.4360],
    'United States': [37.0902, -95.7129]
    # Add more countries and coordinates as needed
}

# Manually specified coordinates for the states
state_coordinates = {
    'All States': [0, 0],  # Default location for All States
    'Alabama': [32.806671, -86.791130],
    'Alberta': [53.9333, -116.5765],
    'Arizona': [33.7298, -111.4312],
    'Bayern': [48.7904, 11.4979],
    'Brandenburg': [52.3001, 12.6159],
    'British Columbia': [53.7267, -127.6476],
    'California': [36.7783, -119.4179],
    'Charente-Maritime': [45.7500, -0.9994],
    'England': [52.3555, -1.1743],
    'Essonne': [48.4487, 2.3195],
    'Florida': [27.9944, -81.7603],
    'Garonne (Haute)': [43.6465, 0.8858],
    'Georgia': [32.1574, -82.9071],
    'Hamburg': [53.5511, 9.9937],
    'Hauts de Seine': [48.8566, 2.3522],
    'Hessen': [51.1657, 9.6216],
    'Illinois': [40.3495, -88.9861],
    'Kentucky': [37.6681, -84.6701],
    'Loir et Cher': [47.4037, 1.3972],
    'Loiret': [47.9794, 2.2519],
    'Massachusetts': [42.4072, -71.3824],
    'Minnesota': [46.7296, -94.6859],
    'Mississippi': [32.7416, -89.6787],
    'Missouri': [38.4561, -92.2884],
    'Montana': [46.9219, -110.4544],
    'Moselle': [49.1193, 6.1727],
    'New South Wales': [-31.8402, 145.6128],
    'New York': [40.7128, -74.0060],
    'Nord': [50.6927, 3.1751],
    'Nordrhein-Westfalen': [51.4332, 7.6616],
    'North Carolina': [35.7596, -79.0193],
    'Ohio': [40.4173, -82.9071],
    'Ontario': [51.2538, -85.3232],
    'Oregon': [43.8041, -120.5542],
    'Pas de Calais': [50.5879, 2.9522],
    'Queensland': [-20.9176, 142.7028],
    'Saarland': [49.3964, 7.0229],
    'Seine (Paris)': [48.8566, 2.3522],
    'Seine et Marne': [48.8414, 2.8128],
    'Seine Saint Denis': [48.9382, 2.3801],
    'Somme': [49.9762, 2.5375],
    'South Australia': [-30.0002, 136.2092],
    'South Carolina': [33.8361, -81.1637],
    'Tasmania': [-41.4545, 145.9707],
    'Texas': [31.9686, -99.9018],
    'Utah': [39.3200, -111.0937],
    'Val de Marne': [48.7904, 2.4068],
    'Val d\'Oise': [49.0720, 2.1445],
    'Victoria': [-36.7789, 144.6970],
    'Virginia': [37.4316, -78.6569],
    'Washington': [47.7511, -120.7401],
    'Wyoming': [43.0750, -107.2903],
    'Yveline': [48.7718, 1.9659]
    # Add more states and coordinates as needed
}

# Create a base map centered at a location
all_coordinates = list(country_coordinates.values()) + list(state_coordinates.values())
min_lat, min_lon = min(c[0] for c in all_coordinates), min(c[1] for c in all_coordinates)
max_lat, max_lon = max(c[0] for c in all_coordinates), max(c[1] for c in all_coordinates)

center_lat, center_lon = ((min_lat + max_lat) / 2)-30, (min_lon + max_lon) / 2

mymap = folium.Map(location=[center_lat, center_lon], zoom_start=2)

# Create a MarkerCluster to handle overlapping markers
marker_cluster = MarkerCluster().add_to(mymap)

# Add markers for countries with profit information
for country, coordinates in country_coordinates.items():
    if country == 'All Countries':
        continue
    country_data = store_data[store_data['Country'] == country]
    country_profit = country_data['Profit'].sum()
    country_revenue = country_data['Revenue'].sum()
    country_expenses = country_data['Cost'].sum()

    # Enhanced popup content with larger font size and styling
    popup_content = f"""
    <div style="font-size: 16px; padding: 10px; background-color: white; border-radius: 5px; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);">
        <strong>{country}</strong><br>
        Revenue: {format_currency(country_revenue, 'blue')}<br>
        Profit: {format_currency(country_profit, 'green')}<br>
        Expenses: {format_currency(country_expenses, 'red')}<br>
    </div>
    """

    folium.Marker(location=coordinates,
                  popup=folium.Popup(popup_content, max_width=300),
                  icon=folium.Icon(color='blue', icon_color='black', icon='glyphicon glyphicon-globe')).add_to(marker_cluster)

# Add markers for states with profit information
for state, coordinates in state_coordinates.items():
    if state == 'All States':
        continue
    state_data = store_data[store_data['State'] == state]
    state_profit = state_data['Profit'].sum()
    state_revenue = state_data['Revenue'].sum()
    state_expenses = state_data['Cost'].sum()

    # Enhanced popup content with larger font size and styling
    popup_content = f"""
    <div style="font-size: 16px; padding: 10px; background-color: white; border-radius: 5px; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);">
        <strong>{state}</strong><br>
        Revenue: {format_currency(state_revenue, 'blue')}<br>
        Profit: {format_currency(state_profit, 'green')}<br>
        Expenses: {format_currency(state_expenses, 'red')}<br>
    </div>
    """

    folium.Marker(location=coordinates,
                  popup=folium.Popup(popup_content, max_width=300),
                  icon=folium.Icon(color='green', icon_color='#FFFFFF', icon='glyphicon glyphicon-home')).add_to(marker_cluster)

# Save the map to HTML as a string
map_html = mymap._repr_html_()

# Embed the Folium Map using an HTML iframe with dynamic width and height
st.components.v1.html(map_html, height=600)


# Display the subheader with the specified background color
#st.markdown('<h3 class="st-eg">Customers Demographics</h3>', unsafe_allow_html=True)
st.markdown("---")
# Create an interactive boxplot using plotly
# Age Variation across Country - Boxplot with Filters
st.subheader('Customers Demographics')
fig_age_variation = px.box(
    filtered_data,
    x='Country',
    y='Customer_Age',
    category_orders={"Country": countries_ordered},
    color='Country',  # You can remove this line if you don't want to color by Country
    color_discrete_map={country: color for country, color in zip(countries_ordered, custom_colors)},
    labels={'Customer_Age': 'Age', 'Country': 'Country'},
    title=f'Age Variation across ({selected_country}, {selected_state}, {selected_year})',
)

# Apply additional customization or layout adjustments if needed
fig_age_variation.update_layout(
    title_font=dict(size=20),
    title_x=0.31)
# Display the plot using Streamlit
st.plotly_chart(fig_age_variation, use_container_width=True)

if not filtered_data.empty:
    # Calculate average age of customers
    average_age_of_customers = filtered_data['Customer_Age'].mean().round(2)
    
    #Bar Chart for Age
    # Use st.expander to create a collapsible section
    with st.expander("Additional Charts", expanded=False):  # Set expanded to True to show the charts by default
        # Bar Chart for Age Distribution
        if not filtered_data.empty:
            fig_age_distribution, ax_age_distribution = plt.subplots(figsize=(14, 5))
            customer_age_ax = filtered_data['Age_Group'].value_counts().sort_values(ascending=False).plot(kind='bar', color=custom_colors, ax=ax_age_distribution)
            customer_age_ax.bar_label(customer_age_ax.containers[0], label_type='edge', color='white', fontsize=10, padding=2, fontweight='bold')
            title_text = f'Customers Distribution by Age ({selected_state})'
            customer_age_ax.set_title(title_text, fontsize=15, fontweight='bold', color='white')
            customer_age_ax.tick_params(axis='both', colors='white')  # Set tick color
            plt.xticks(rotation=0, ha='center')
            customer_age_ax.set_xlabel('')
        
            # Set background color and font color for the figure and subplot
            fig_age_distribution.patch.set_facecolor('#1d232f')  # Updated color
            ax_age_distribution.set_facecolor('#1d232f')  # Updated color
        
            st.pyplot(fig_age_distribution)
        else:
            # Display a message if the filtered data is empty
            st.warning("No data available for the selected filters. Please adjust your filter criteria.")
        
        # Density Chart for Age
        # Density Estimate for Customer Age
        if not filtered_data.empty:
            fig_density_estimate, ax_density_estimate = plt.subplots(figsize=(14, 5))
            sns.kdeplot(data=filtered_data, x='Customer_Age', fill=True, color=custom_colors[2], ax=ax_density_estimate)
            median_age_of_customers = filtered_data['Customer_Age'].median()
        
            ax_density_estimate.axvline(x=median_age_of_customers, color='#f6546a', linestyle='--', label=f'Median: {median_age_of_customers:.1f}')
            ax_density_estimate.axvline(x=average_age_of_customers, color='#468499', linestyle='--', label=f'Mean: {average_age_of_customers:.1f}')
        
            title_text = f'Density Estimate for Customer Age ({selected_state})'
            ax_density_estimate.set_title(title_text, fontsize=15, fontweight='bold', color='white')
        
            ax_density_estimate.set_xlabel('Customer Age', fontsize=9, color='white')
            ax_density_estimate.set_ylabel('', fontsize=9, color='white')
            ax_density_estimate.legend()
            legend = ax_density_estimate.legend()
        
            legend = ax_density_estimate.legend(frameon=True, facecolor='#81d8d0', fontsize=8)
            # Set background color for the figure and subplot
            fig_density_estimate.patch.set_facecolor('#1d232f')  # Updated color
            ax_density_estimate.set_facecolor('#1d232f')  # Updated color
            ax_density_estimate.tick_params(axis='both', colors='white')
        
            # Show the density estimate plot in Streamlit
            st.pyplot(fig_density_estimate)
        else:
            # Display a message if the filtered data is empty
            st.warning("No data available for the selected filters. Please adjust your filter criteria.")
else:
    # Display a message if the filtered data is empty
    st.warning("No data available for the selected filters. Please adjust your filter criteria.") 
        
#Pie Chart for Customer Gender    
# Group by Customer_Gender and calculate the size
# Custom colors
if not filtered_data.empty:
    pie_custom_colors = ['#f6546a', '#468499']
    
    # Group by Customer_Gender and calculate the size
    gender_distribution = filtered_data.groupby('Customer_Gender').size().reset_index(name='Count')
    
    # Plot pie chart using Plotly Express
    fig = px.pie(
        gender_distribution,
        names='Customer_Gender',
        values='Count',
        color='Customer_Gender',
        color_discrete_map=dict(zip(gender_distribution['Customer_Gender'], pie_custom_colors)),
        labels={'Customer_Gender': 'Gender'},
        title=f'Customers Distribution by Gender ({selected_country} - {selected_state if selected_state and selected_state != "All States" else "All States"})',
    )
    
    # Set layout properties
    fig.update_layout(
        title_font=dict(size=20),
        font=dict(size=20),
        height=600,
        width=600,
        title_x=0.28,
    )
    
    # Add labels to the chart
    fig.for_each_trace(lambda t: t.update(textinfo='label+percent'))
    
    # Display the chart using Streamlit with specified width
    st.plotly_chart(fig, use_container_width=True)
else:
    # Display a message if the filtered data is empty
    st.warning("No data available for the selected filters. Please adjust your filter criteria.")

# Bar plot using Plotly Express COUNTRY WITH THE MOST CUSTOMERS
if not filtered_data.empty:
    custom_colors_range = ['#81d8d0', '#468499', '#f6546a']
    customers_per_country = filtered_data['Country'].value_counts().sort_values(ascending=True)
    fig = px.bar(
        x=customers_per_country.values,
        y=customers_per_country.index,
        orientation='h',  # horizontal bar chart
        text=customers_per_country.values,
        color=customers_per_country.values,  # Use values for color scale
        color_continuous_scale=custom_colors_range,
        labels={'y': '', 'x': 'Number of customers'},
        title='Country with the most Customers',
    )
    
    # Set layout properties
    fig.update_layout(
        title_font=dict(size=20),
        font=dict(size=17),
        height=400,
        title_x=0.40
    )
    
    # Make bar labels bold and white using HTML styling
    fig.update_traces(texttemplate='<b>%{text}</b>', textfont=dict(color='white'))
    
    # Display the chart using Streamlit with specified width
    st.plotly_chart(fig, use_container_width=True)
else:
    # Display a message if the filtered data is empty
    st.warning("No data available for the selected filters. Please adjust your filter criteria.")
    
# Bar plot using Plotly Express STATE WITH THE MOST CUSTOMERS

# Calculate the top 10 states with the most customers
customers_per_state = filtered_data['State'].value_counts().head(10).sort_values(ascending=True)
if not filtered_data.empty:
    # Plot bar chart using Plotly Express
    fig = px.bar(
        x=customers_per_state.values,
        y=customers_per_state.index,
        text=customers_per_state.values,
        orientation='h',
        color=customers_per_state.values,  # Use values for color scale
        color_continuous_scale=custom_colors_range,
        labels={'y': '', 'x': 'Number of customers'},
        title=f'Top 10 States with the Most Customers ({selected_country})',
    )
    
    # Set layout properties
    fig.update_layout(
        title_font=dict(size=20),
        font=dict(size=17),
        height=500,
        title_x=0.37
    )
    
    # Make bar labels bold and white using HTML styling
    fig.update_traces(texttemplate='<b>%{text}</b>', textfont=dict(color='white'))
    
    # Display the chart using Streamlit with specified width
    st.plotly_chart(fig, use_container_width=True)
else:
    # Display a message if the filtered data is empty
    st.warning("No data available for the selected filters. Please adjust your filter criteria.")

st.markdown("---")
st.subheader('Orders Quantity Analysis')
# BOXPLOT ORDER QUANTITY
if not filtered_data.empty:
    # Average Order Quantity
    average_order_quantity = filtered_data['Order_Quantity'].mean().round(2)
    # Boxplot for Order Quantity
    fig_boxplot = px.box(
        filtered_data,
        y='Order_Quantity',
        color_discrete_sequence=[custom_colors[1]],
        labels={'Order_Quantity': 'Order Quantity'},
        title=f'Orders Quantity ({selected_country} - {selected_state if selected_state and selected_state != "All States" else "All States"})<br>'
        f'                   Average Order Quantity: {average_order_quantity}',
    )

    # Set layout properties for boxplot
    fig_boxplot.update_layout(
        title_font=dict(size=20),
        font=dict(size=12, color=custom_colors[1]),
        title_x=0.38
    )
    
    # Display the boxplot using Streamlit with specified width
    st.plotly_chart(fig_boxplot, use_container_width=True)
else:
    # Display a message if the filtered data is empty
    st.warning("No data available for the selected filters. Please adjust your filter criteria.")

#HISTOGRAM
# Orders Quantity Histogram
with st.expander("Additional Charts", expanded=False):
    if not filtered_data.empty:
        # Create a Matplotlib figure and axis
        fig_order_quantity, ax_order_quantity = plt.subplots(figsize=(14, 5))
        
        # Use seaborn's histplot for the Orders Quantity Histogram with a darker color
        sns.histplot(x='Order_Quantity', data=filtered_data, color='#f6546a', bins=len(filtered_data['Order_Quantity'].unique()), ax=ax_order_quantity)
        
        # Set plot properties
        ax_order_quantity.set_title(f'Orders Quantity Histogram ({selected_country} - {selected_state if selected_state and selected_state != "All States" else "All States"})', fontsize=15, fontweight='bold', color= 'white')
        ax_order_quantity.set_ylabel('Count', fontsize=12, color='white')
        ax_order_quantity.set_xlabel('Order Quantity', fontsize=12, color='white')  # Set x-axis label color to white
        
        # Set x-axis and y-axis tick colors to white
        ax_order_quantity.tick_params(axis='x', colors='white')
        ax_order_quantity.tick_params(axis='y', colors='white')
        
        # Set background color for the figure and subplot without transparency
        fig_order_quantity.patch.set_facecolor('#1d232f')  # Updated color
        ax_order_quantity.set_facecolor('#1d232f')  # Updated color
        
        # Display the Matplotlib figure in Streamlit
        st.pyplot(fig_order_quantity)
    else:
        # Display a message if the filtered data is empty
        st.warning("No data available for the selected filters. Please adjust your filter criteria.")
    
#CUSTOMERS PER CATEGORY BAR
# Bar plot using Plotly Express
if not filtered_data.empty:
    customers_per_category = filtered_data['Product_Category'].value_counts().sort_values(ascending=False)
    fig_category = px.bar(
        x=customers_per_category.index,
        y=customers_per_category.values,
        text=customers_per_category.values,
        color=customers_per_category.index,
        color_discrete_sequence=custom_colors,
        labels={'x': 'Product Category', 'y': 'Number of customers'},
        title=f'Total Customers per Category ({selected_country} - {selected_state if selected_state and selected_state != "All States" else "All States"})',
    )
    
    # Set layout properties for the bar chart
    fig_category.update_layout(
        title_font=dict(size=20),
        font=dict(size=12),
        title_x=0.36,
        height= 500
    )
    
    # Make bar labels bigger and bold
    fig_category.update_traces(
        texttemplate='<b>%{text}</b>',
        textfont=dict(size=12, color='white', family='Arial'),
        textposition='outside'
    )
    
    # Display the chart using Streamlit with specified width
    st.plotly_chart(fig_category, use_container_width=True)
else:
    # Display a message if the filtered data is empty
    st.warning("No data available for the selected filters. Please adjust your filter criteria.")
    
# SUBCATEGORY WITH THE MOST ORDERS
if not filtered_data.empty:
    # Group by Sub_Category and sum the Order_Quantity
    subcategory_orders = filtered_data.groupby('Sub_Category')['Order_Quantity'].sum().sort_values(ascending=False)
    
    # Create a bar chart using Plotly Express
    fig_subcategory_orders = px.bar(
        x=subcategory_orders.index,
        y=subcategory_orders.values,
        color=subcategory_orders.values,
        color_continuous_scale=custom_colors_range,
        labels={'x': 'Subcategory', 'y': 'Order Quantity'},
        title='Total Orders per Subcategory',
        orientation='v',  # 'h' for horizontal, 'v' for vertical
    )
    
    # Update layout for better appearance
    fig_subcategory_orders.update_layout(
    title={
        'text': f'Total Orders per Subcategory({selected_country} - {selected_state if selected_state and selected_state != "All States" else "All States"})',
        'x': 0.5,
        'y': 0.95,
        'xanchor': 'center',
        'yanchor': 'top'
    },
    xaxis_title='',
    yaxis_title='Order Quantity',
    showlegend=False,
    margin=dict(t=60)
    )
    
    # Update font properties for bar labels
    fig_subcategory_orders.update_traces(
        textposition='outside',  # Display labels outside the bar
        insidetextanchor='start',
        texttemplate='%{y:.3s}',  # Display the actual values as labels
        textfont=dict(size=15, color='white', family='Arial')  # Font properties
    )
    fig_subcategory_orders.update_layout(
        title_font=dict(size=20),
        height=500,
        title_x=0.50
    )
    
    # Show the plot
    st.plotly_chart(fig_subcategory_orders, use_container_width=True)
else:
    # Display a message if the filtered data is empty
    st.warning("No data available for the selected filters. Please adjust your filter criteria.")
        
st.markdown("---")
st.subheader('Total Revenue & Profit Analysis')
# Sales Revenue by Category PIE 
# Pie chart using Plotly Express
if not filtered_data.empty:
    fig_pie = px.pie(
        filtered_data,
        names='Product_Category',
        values='Revenue',
        color='Product_Category',
        color_discrete_sequence=custom_colors,
        labels={'Product_Category': 'Product Category', 'Revenue': 'Revenue'},
        title=f'Total Revenue by Product Category ({selected_country} - {selected_state if selected_state and selected_state != "All States" else "All States"})',
        template='plotly_dark',  # You can choose a different template if needed
    )
    
    # Set layout properties for the pie chart
    fig_pie.update_layout(
        title_font=dict(size=20),
        font=dict(size=15),
        height=600,
        width=600,
        title_x=0.28,
        showlegend= False
    )
    
    # Add custom text inside each pie slice
    fig_pie.update_traces(
        textinfo='percent+label',
        pull=[0.1, 0, 0],
        textfont=dict(color='white')
    )
    
    # Display the chart using Streamlit with specified width
    st.plotly_chart(fig_pie, use_container_width=True)
else:
    # Display a message if the filtered data is empty
    st.warning("No data available for the selected filters. Please adjust your filter criteria.")
    
#SALES REVENUE BY AGE GROUP BAR
# Filter data based on selected country, state, product category, and subcategory
if not filtered_data.empty:
    # Bar chart using Plotly Express
    fig_age_revenue = px.bar(
        filtered_data.groupby('Age_Group')['Revenue'].sum().sort_values(ascending=False).reset_index(),
        x='Age_Group',
        y='Revenue',
        color='Age_Group',
        color_discrete_sequence=custom_colors,
        labels={'Revenue': 'Total Revenue', 'Age_Group': 'Age Group'},
        title=f'Total Revenue by Age Group ({selected_country} - {selected_state if selected_state and selected_state != "All States" else "All States"})'
    )
    
    # Update text template for bar labels with two decimal places
    fig_age_revenue.update_traces(texttemplate='%{y:.3s}', textposition='outside')
    
    # Update layout
    fig_age_revenue.update_layout(
        yaxis=dict(
            tickmode='array',
        ),
        title_font=dict(size=20),
        font=dict(size=13),
        xaxis_title='Age Group',
        yaxis_title='Total Revenue',
        xaxis_tickangle=0,
        title_x=0.36,
        height= 500,
        showlegend= False
    )
    fig_age_revenue.update_traces(
    hovertemplate='<b>Total Revenue:</b> $%{y:,.2f}<br>%{x}',  # Customize hover template
    hoverlabel=dict(
        font=dict(size=18)  # Set the font size for hover text
        )
    )
    
    # Display the chart using Streamlit
    st.plotly_chart(fig_age_revenue, use_container_width=True)
else:
    # Display a message if the filtered data is empty
    st.warning("No data available for the selected filters. Please adjust your filter criteria.")

# REVENUE PER COUNTRY
# Calculate total revenues for percentage calculation
if not filtered_data.empty:
    filtered_data = store_data
        # Filter based on selected product category
    if selected_product_category != 'All Categories':
            filtered_data = filtered_data[filtered_data['Product_Category'] == selected_product_category]
    
            # Filter based on selected subcategory
            if selected_sub_category != 'All Sub-Categories':
                filtered_data = filtered_data[filtered_data['Sub_Category'] == selected_sub_category]
    if selected_year != 'All Years':
        filtered_data = filtered_data[store_data['Year'] == int(selected_year)]
        if selected_month != 'All Months':
            filtered_data = filtered_data[filtered_data['Month'] == selected_month]
    # Total Revenues
    total_revenues_filtered = filtered_data['Revenue'].sum()
    
    # Revenue per Country using Plotly Express
    fig_revenue_per_country = px.bar(
        filtered_data.groupby('Country')['Revenue'].sum().sort_values(ascending=False).reset_index(),
        x='Country',
        y='Revenue',
        color='Country',
        color_discrete_sequence=custom_colors,
        labels={'Revenue': 'Revenue', 'Country': 'Country'},
        title=f'Total Revenue per Country ({selected_product_category}, {selected_sub_category if selected_sub_category and selected_product_category != "All Categoris" else "All Sub-Categories"})'
    )
    
    revenue_per_country = filtered_data.groupby('Country')['Revenue'].sum().sort_values(ascending=False)
    
    for i, value in enumerate(revenue_per_country):
        percentage = (value / total_revenues_filtered) * 100
        fig_revenue_per_country.add_annotation(
            x=i,
            y=value + 5,
            text=f'{value/1000000:.2f}M<br>({percentage:.2f}%)',
            showarrow=False,
            font=dict(size=13),
            xanchor='center',
            yanchor='bottom'
        )
    
    # Update text template for bar labels with two decimal places and accurate percentages
    fig_revenue_per_country.update_layout(
        xaxis=dict(
            tickangle=0,  # Adjust the rotation angle as needed
            tickfont=dict(size=10)
        ),
        title_font=dict(size=20),
        title_x=0.36,
        yaxis_title='Revenue',
        showlegend=False,
        xaxis_title=''
    )
    
    # Display the chart using Streamlit
    st.plotly_chart(fig_revenue_per_country, use_container_width=True)
else:
    # Display a message if the filtered data is empty
    st.warning("No data available for the selected filters. Please adjust your filter criteria.")

# PROFIT PER COUNTRY BAR CHART
# Filter the data based on the selected country and state
if not filtered_data.empty:
    filtered_data = store_data
    if selected_product_category != 'All Categories':
            filtered_data = filtered_data[filtered_data['Product_Category'] == selected_product_category]
    
            # Filter based on selected subcategory
            if selected_sub_category != 'All Sub-Categories':
                filtered_data = filtered_data[filtered_data['Sub_Category'] == selected_sub_category]
    if selected_year != 'All Years':
        filtered_data = filtered_data[store_data['Year'] == int(selected_year)]
        if selected_month != 'All Months':
            filtered_data = filtered_data[filtered_data['Month'] == selected_month]
            
    # Calculate total profit for percentage calculation
    total_profit_filtered = filtered_data['Profit'].sum()
    
    # Profit per Country using Plotly Express
    fig_profit_per_country = px.bar(
        filtered_data.groupby('Country')['Profit'].sum().sort_values(ascending=False).reset_index(),
        x='Country',
        y='Profit',
        color='Country',
        color_discrete_sequence=custom_colors,
        labels={'Profit': 'Profit', 'Country': 'Country'},
        title=f'Total Profit per Country ({selected_product_category}, {selected_sub_category if selected_sub_category and selected_product_category != "All Categoris" else "All Sub-Categories"})'
    )
    
    profit_per_country = filtered_data.groupby('Country')['Profit'].sum().sort_values(ascending=False)
    
    for i, value in enumerate(profit_per_country):
        percentage = (value / total_profit_filtered) * 100
        fig_profit_per_country.add_annotation(
            x=i,
            y=value + 5,
            text=f'{value/1000000:.2f}M<br>({percentage:.2f}%)',
            showarrow=False,
            font=dict(size=13),
            xanchor='center',
            yanchor='bottom'
        )
    
    # Update text template for bar labels with two decimal places and percentage
    fig_profit_per_country.update_traces(
        textposition='outside'
    )
    
    # Manually set x-axis tick labels with rotation
    fig_profit_per_country.update_layout(
        xaxis=dict(
            tickangle=0,  # Adjust the rotation angle as needed
            tickfont=dict(size=10)
        ),
        title_font=dict(size=20),
        title_x=0.36,
        yaxis_title='Profit',
        showlegend=False  # Hide the legend
    )
    
    # Display the chart using Streamlit
    st.plotly_chart(fig_profit_per_country, use_container_width=True)
else:
    # Display a message if the filtered data is empty
    st.warning("No data available for the selected filters. Please adjust your filter criteria.")
    
#Profit Variations Across Countries BOXPLOT
# Filter the data based on the selected country and state
if not filtered_data.empty:
    filtered_data = store_data
    if selected_product_category != 'All Categories':
            filtered_data = filtered_data[filtered_data['Product_Category'] == selected_product_category]
    
            # Filter based on selected subcategory
            if selected_sub_category != 'All Sub-Categories':
                filtered_data = filtered_data[filtered_data['Sub_Category'] == selected_sub_category]
    if selected_year != 'All Years':
        filtered_data = filtered_data[store_data['Year'] == int(selected_year)]
        if selected_month != 'All Months':
            filtered_data = filtered_data[filtered_data['Month'] == selected_month]
            
    # Order countries
    countries_ordered = ['United States', 'Australia', 'United Kingdom', 'Canada', 'Germany', 'France']
    
    # Boxplot using Plotly Express
    fig_profit_variations = px.box(
        filtered_data,
        x='Country',
        y='Profit',
        category_orders={'Country': countries_ordered},
        color='Country',
        color_discrete_sequence=custom_colors,
        labels={'Profit': 'Profit', 'Country': 'Country'},
        title=f'Profit Variations Across Countries ({selected_product_category}, {selected_sub_category if selected_sub_category and selected_product_category != "All Categoris" else "All Sub-Categories"})'
    )
    
    # Update layout for better visualization
    fig_profit_variations.update_layout(
        yaxis_title='Profit',
        title_x=0.30,
        title_font=dict(size=20),
    )
    
    # Display the chart using Streamlit
    st.plotly_chart(fig_profit_variations, use_container_width=True)
else:
    # Display a message if the filtered data is empty
    st.warning("No data available for the selected filters. Please adjust your filter criteria.")
    
st.markdown("---")    
st.subheader('Top Charts')
#Top 10 Most Purchased Products BAR CHART
# Filter the data based on the selected country and state
if not filtered_data.empty:
    # Add a new column for labels including both Product and Product_Category
    store_data['Product_Label'] = filtered_data['Product'] + '<br>(' + store_data['Product_Category'] + ')'
    
    # Top 10 Most Purchased Products using Plotly Express
    most_purchased_item= filtered_data.groupby('Product')['Order_Quantity'].sum().sort_values(ascending=False).head(10)
    fig_most_purchased_item = px.bar(
        filtered_data.groupby('Product')['Order_Quantity'].sum().sort_values(ascending=False).head(10).reset_index(),
        x='Product',
        y='Order_Quantity',
        color=most_purchased_item.values,
        color_continuous_scale=custom_colors_range,
        labels={'Order_Quantity': 'Order Quantity', 'Product': 'Product'},
        title=f'Top 10 Most Purchased Products ({selected_country} - {selected_state if selected_state and selected_state != "All States" else "All States"})'
    )
    
    # Manually set x-axis tick labels with HTML line breaks
    product_labels = store_data.loc[store_data['Product'].isin(fig_most_purchased_item.data[0].x), 'Product_Label']
    fig_most_purchased_item.update_layout(
        xaxis=dict(
            ticktext=product_labels,
            tickangle=0,
            tickfont=dict(size=10)
        ),
        title_font=dict(size=20),
        title_x=0.36,
        showlegend=False,
        yaxis_title='Order Quantity',
        xaxis_title=''
    )
    # Update text template for bar labels with two decimal places
    fig_most_purchased_item.update_traces(texttemplate='%{y:.3s}', textposition='outside')
    
    # Display the chart using Streamlit
    st.plotly_chart(fig_most_purchased_item, use_container_width=True)
else:
    # Display a message if the filtered data is empty
    st.warning("No data available for the selected filters. Please adjust your filter criteria.")

    
# TOP 10 BEST SELLING PRODUCTS BAR CHART 
if not filtered_data.empty:
    # Top 10 Best Selling Products using Plotly Express
    revenue_by_product= filtered_data.groupby('Product')['Revenue'].sum().sort_values(ascending=False).head(10)
    fig_revenue_by_product = px.bar(
        filtered_data.groupby('Product')['Revenue'].sum().sort_values(ascending=False).head(10).reset_index(),
        x='Product',
        y='Revenue',
        color=revenue_by_product,
        color_continuous_scale=custom_colors_range,
        labels={'Revenue': 'Revenue', 'Product': 'Product'},
        title=f'Top 10 Best Selling Products ({selected_country} - {selected_state if selected_state and selected_state != "All States" else "All States"})'
    )
    
    # Update text template for bar labels with two decimal places
    fig_revenue_by_product.update_traces(texttemplate='%{y:.3s}', textposition='outside')
    
    # Manually set x-axis tick labels with rotation
    fig_revenue_by_product.update_layout(
        xaxis=dict(
            ticktext=fig_revenue_by_product.data[0].x,
            tickangle=0,
            tickfont=dict(size=10)
        ),
        title_font=dict(size=20),
        title_x=0.36,
        showlegend=False,
        yaxis_title='Revenue',
        xaxis_title=''
    )
    
    # Display the chart using Streamlit
    st.plotly_chart(fig_revenue_by_product, use_container_width=True)
else:
    # Display a message if the filtered data is empty
    st.warning("No data available for the selected filters. Please adjust your filter criteria.")

# WORST SELLING PRODUCTS BAR CHART 
if not filtered_data.empty:
    with st.expander("**Expand for WORST SELLING PRODUCTS CHART**", expanded=False):
        lowest_revenue_by_product= filtered_data.groupby('Product')['Revenue'].sum().sort_values(ascending=True).head(10)
        fig_revenue_by_product = px.bar(
            filtered_data.groupby('Product')['Revenue'].sum().sort_values(ascending=True).head(10).reset_index(),
            x='Product',
            y='Revenue',
            color=lowest_revenue_by_product,
            color_continuous_scale=custom_colors_range,
            labels={'Revenue': 'Revenue', 'Product': 'Product'},
            title=f'WORST Selling Products ({selected_country} - {selected_state if selected_state and selected_state != "All States" else "All States"})'
        )
        
        # Update text template for bar labels with two decimal places
        fig_revenue_by_product.update_traces(texttemplate='%{y:.3s}', textposition='outside')
        
        # Manually set x-axis tick labels with rotation
        fig_revenue_by_product.update_layout(
            xaxis=dict(
                ticktext=fig_revenue_by_product.data[0].x,
                tickangle=0,
                tickfont=dict(size=10),
            ),
            title_font=dict(size=20),
            title_x=0.36,
            showlegend=False,
            yaxis_title='Revenue',
            xaxis_title=''
        )
        
        # Display the chart using Streamlit
        st.plotly_chart(fig_revenue_by_product, use_container_width=True)
else:
    # Display a message if the filtered data is empty
    st.warning("No data available for the selected filters. Please adjust your filter criteria.")
    
#TOP 20 PERFORMING STATES
# Top 20 Performing States using Plotly Express
if not filtered_data.empty:
    filtered_data = store_data
    if selected_country != 'All Countries':
        filtered_data = store_data[store_data['Country'] == selected_country]
    
        # Filter based on selected product category
    if selected_product_category != 'All Categories':
            filtered_data = filtered_data[filtered_data['Product_Category'] == selected_product_category]
    
            # Filter based on selected subcategory
            if selected_sub_category != 'All Sub-Categories':
                filtered_data = filtered_data[filtered_data['Sub_Category'] == selected_sub_category]
                
    if selected_year != 'All Years':
        filtered_data = filtered_data[store_data['Year'] == int(selected_year)]
        if selected_month != 'All Months':
            filtered_data = filtered_data[filtered_data['Month'] == selected_month]
    
    # Top 20 Performing States using Plotly Express
    best_performing_state= filtered_data.groupby('State')['Revenue'].sum().sort_values(ascending=False).head(20)
    fig_best_performing_state = px.bar(
        filtered_data.groupby('State')['Revenue'].sum().sort_values(ascending=False).head(20).reset_index(),
        x='State',
        y='Revenue',
        color=best_performing_state,
        color_continuous_scale=custom_colors_range,
        labels={'Revenue': 'Revenue', 'State': 'State'},
        title=f'Top 20 Performing States ({selected_country})'
    )
    
    # Update text template for bar labels with two decimal places
    fig_best_performing_state.update_traces(texttemplate='%{y:.3s}', textposition='outside')
    
    # Manually set x-axis tick labels with rotation
    fig_best_performing_state.update_layout(
        xaxis=dict(
            ticktext=fig_best_performing_state.data[0].x,
            tickangle=0,
            tickfont=dict(size=10)
        ),
        title_font=dict(size=20),
        yaxis_title='Revenue',
        title_x=0.36,
        height=500,
        showlegend=False,
        xaxis_title=''
    )
    
    # Display the chart using Streamlit
    st.plotly_chart(fig_best_performing_state, use_container_width=True)
else:
    # Display a message if the filtered data is empty
    st.warning("No data available for the selected filters. Please adjust your filter criteria.")
    
st.markdown("---")
st.subheader('Sales Trend Analysis')
#SALES TREND OVER YEARS
# Line plot using Plotly Express
if not filtered_data.empty:
    filtered_data = store_data.copy()
    if selected_country != 'All Countries':
        filtered_data = filtered_data[filtered_data['Country'] == selected_country]
    
        if selected_state and selected_state != 'All States':
            filtered_data = filtered_data[filtered_data['State'] == selected_state]
    
    if selected_product_category != 'All Categories':
        filtered_data = filtered_data[filtered_data['Product_Category'] == selected_product_category]
    
        if selected_sub_category != 'All Sub-Categories':
            filtered_data = filtered_data[filtered_data['Sub_Category'] == selected_sub_category]
    
    # Calculate sales per year for the filtered data
    sales_per_year_filtered = filtered_data.groupby('Year')['Revenue'].sum().reset_index()
    
    fig_sales_per_year = px.line(
        x=sales_per_year_filtered['Year'],
        y=sales_per_year_filtered['Revenue'],
        markers=True,
        line_shape='linear',  # Choose the line shape (linear, spline, etc.)
        labels={'y': 'Revenue', 'x': 'Year'},
        title=f'Total Sales per Year ({selected_country} - {selected_state if selected_state and selected_state != "All States" else "All States"})',
        hover_name=sales_per_year_filtered['Year'],  # Use the year as the line label
        text=sales_per_year_filtered['Revenue'].apply(lambda x: f'${x/1000000:.2f}M'),  # Display values on lines
    )
    
    # Update layout for better visualization
    fig_sales_per_year.update_layout(
        yaxis_title='Revenue',
        title_x=0.36,
        title_font=dict(size=20),
    )
    
    # Format y-axis tick labels in millions
    fig_sales_per_year.update_yaxes(
        tickformat='$.3s',  # Format ticks in millions (e.g., $1M)
    )
    fig_sales_per_year.update_traces(
        textposition='top center',  # Change the text position
        textfont=dict(size=14),
        hovertemplate='<b>Year:</b> %{x}<br><b>Revenue:</b> $%{y:,.3s}',
        hoverlabel=dict(font=dict(size=25))
    )
    
    # Display the chart using Streamlit
    st.plotly_chart(fig_sales_per_year, use_container_width=True)
else:
    # Display a message if the filtered data is empty
    st.warning("No data available for the selected filters. Please adjust your filter criteria.")
    
#SALES MONTHLY TREND FOR EVERY YEAR
# Line plot using Plotly Express
if not filtered_data.empty:
    filtered_data = store_data
    if selected_country != 'All Countries':
        filtered_data = store_data[store_data['Country'] == selected_country]
    
        # Only show the state filter when a country is selected
        if selected_state and selected_state != 'All States':
            filtered_data = filtered_data[filtered_data['State'] == selected_state]
    
        # Filter based on selected product category
    if selected_product_category != 'All Categories':
            filtered_data = filtered_data[filtered_data['Product_Category'] == selected_product_category]
    
            # Filter based on selected subcategory
            if selected_sub_category != 'All Sub-Categories':
                filtered_data = filtered_data[filtered_data['Sub_Category'] == selected_sub_category]
    
    # Calculate sales trend for the filtered data
    sales_trend = filtered_data.groupby(['Year', 'Month'])['Revenue'].sum().reset_index()
    
    # Sales Trend Over Time using Plotly Express
    fig_sales_trend = px.line(
        sales_trend,
        x='Month',
        y='Revenue',
        color='Year',
        markers=True,
        line_shape='linear',
        labels={'Revenue': 'Revenue', 'Month': 'Month'},
        title=f'Sales Trend Over Time ({selected_country} - {selected_state if selected_state and selected_state != "All States" else "All States"})'
    )
    
    # Update layout for better visualization
    fig_sales_trend.update_layout(
        xaxis_title='Month',
        yaxis_title='Revenue',
        title_x=0.36,
        title_font=dict(size=20),
    )
    
    # Update y-axis tick format
    fig_sales_trend.update_yaxes(
        tickformat='$.3s',  # Format ticks in millions (e.g., $1M)
    )
    
    # Increase text size of the hover area
    fig_sales_trend.update_traces(
        hovertemplate='<b>Month:</b> %{x}<br><b>Revenue:</b> $%{y:,.3s}',
        hoverlabel=dict(font=dict(size=25))  # Increase text size of hover labels
    )
    
    # Display the chart using Streamlit
    st.plotly_chart(fig_sales_trend, use_container_width=True)
else:
    # Display a message if the filtered data is empty
    st.warning("No data available for the selected filters. Please adjust your filter criteria.")

st.markdown("---")
st.subheader('Business Correlation Insights')
#COST-PRICE CORRELATION SCATTERPLOT
# Scatter plot using Plotly Express
if not filtered_data.empty:
    filtered_data = store_data
    if selected_country != 'All Countries':
        filtered_data = store_data[store_data['Country'] == selected_country]
    
        # Only show the state filter when a country is selected
        if selected_state and selected_state != 'All States':
            filtered_data = filtered_data[filtered_data['State'] == selected_state]
    
        # Filter based on selected product category
    if selected_product_category != 'All Categories':
            filtered_data = filtered_data[filtered_data['Product_Category'] == selected_product_category]
    
            # Filter based on selected subcategory
            if selected_sub_category != 'All Sub-Categories':
                filtered_data = filtered_data[filtered_data['Sub_Category'] == selected_sub_category]
    if selected_year != 'All Years':
        filtered_data = filtered_data[store_data['Year'] == int(selected_year)]
        if selected_month != 'All Months':
            filtered_data = filtered_data[filtered_data['Month'] == selected_month]
    # Cost-Price Correlation using Plotly Express
    fig_cost_price_correlation = px.scatter(
        filtered_data,
        x='Unit_Cost',
        y='Unit_Price',
        color='Product_Category',
        color_discrete_sequence=custom_colors[0:3],
        labels={'Unit_Cost': 'Unit Cost', 'Unit_Price': 'Unit Price'},
        title=f'Cost-Price Correlation ({selected_country} - {selected_state if selected_state and selected_state != "All States" else "All States"})',
        size_max=150,
    )
    
    # Update layout for better visualization
    fig_cost_price_correlation.update_layout(
        height=500,
        title_x=0.36,
        title_font=dict(size=20),
    )
    fig_cost_price_correlation.update_traces(
        hovertemplate='<b>Unit Cost:</b> %{x}<br><b>Unit Price:</b> $%{y:,.3s}',
        hoverlabel=dict(font=dict(size=25))  # Increase hover text size
    )
    # Increase the size of markers
    fig_cost_price_correlation.update_traces(marker=dict(size=18))
    
    # Display the chart using Streamlit
    st.plotly_chart(fig_cost_price_correlation, use_container_width=True)
else:
    # Display a message if the filtered data is empty
    st.warning("No data available for the selected filters. Please adjust your filter criteria.")

#QUANTITY-PROFIT CORRELATION
# Scatter plot using Plotly Express
if not filtered_data.empty:
    filtered_data = store_data
    if selected_country != 'All Countries':
        filtered_data = store_data[store_data['Country'] == selected_country]
    
        # Only show the state filter when a country is selected
        if selected_state and selected_state != 'All States':
            filtered_data = filtered_data[filtered_data['State'] == selected_state]
    
        # Filter based on selected product category
    if selected_product_category != 'All Categories':
            filtered_data = filtered_data[filtered_data['Product_Category'] == selected_product_category]
    
            # Filter based on selected subcategory
            if selected_sub_category != 'All Sub-Categories':
                filtered_data = filtered_data[filtered_data['Sub_Category'] == selected_sub_category]
    if selected_year != 'All Years':
        filtered_data = filtered_data[store_data['Year'] == int(selected_year)]
        if selected_month != 'All Months':
            filtered_data = filtered_data[filtered_data['Month'] == selected_month]
    # Quantity-Profit Correlation using Plotly Express
    fig_quantity_profit_correlation = px.scatter(
        filtered_data,
        x='Order_Quantity',
        y='Profit',
        color='Product_Category',
        color_discrete_sequence=custom_colors[0:3],
        labels={'Order_Quantity': 'Order Quantity', 'Profit': 'Profit'},
        title=f'Order Quantity & Profit Correlation ({selected_country} - {selected_state if selected_state and selected_state != "All States" else "All States"})',
        size_max=150,
    )
    
    # Increase the size of markers
    fig_quantity_profit_correlation.update_traces(marker=dict(size=13, symbol='x'))
    fig_quantity_profit_correlation.update_traces(
        hovertemplate='<b>Order Quantity:</b> %{x}<br><b>Profit:</b> $%{y:,.3s}',
        hoverlabel=dict(font=dict(size=25))
    )
    
    # Update layout for better visualization
    fig_quantity_profit_correlation.update_layout(
        height=500,
        title_x=0.36,
        title_font=dict(size=20),
    )
    
    # Display the chart using Streamlit
    st.plotly_chart(fig_quantity_profit_correlation, use_container_width=True)
else:
    # Display a message if the filtered data is empty
    st.warning("No data available for the selected filters. Please adjust your filter criteria.")

st.markdown("---")