import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import json

# Streamlit application title
st.title("Vehicle Trajectory Visualization in Belgium")

# Sidebar for range sliders
with st.sidebar:
    # Uploading multiple files section
    uploaded_files = st.file_uploader("Choose CSV files", type=["csv"], accept_multiple_files=True)
    uploaded_geojson = st.file_uploader("Upload trajectories_geojson.json", type=["json"])
    uploaded_csv = st.file_uploader("Upload stations.csv", type=["csv"])

    # Anomaly detection methods selection box
    anomaly_column = st.selectbox("Anomaly Detection Methods", ["isolation_forest_anamoly", "lof_anamoly", "svm_anamoly", "knn_anamoly", "final_anomaly_flag"])

    # Range sliders for various columns
    lat_range = st.slider("Select a Latitude range", min_value=49.90, max_value=51.30, value=(49.90, 51.30), step=0.01)
    lon_range = st.slider("Select a Longitude range", min_value=3.55, max_value=5.55, value=(3.55, 5.55), step=0.01)
    temperature_range = st.slider("Select a temperature range", min_value=-6.0, max_value=35.0, value=(-6.0, 35.0), step=0.1)
    humidity_range = st.slider("Select a Relative Humidity range", min_value=23.0, max_value=100.0, value=(23.0, 100.0))
    dewpoint_range = st.slider("Select a Dew Point range", min_value=-10.0, max_value=25.0, value=(-10.0, 25.0), step=0.1)
    precipitation_range = st.slider("Select a Precipitation range", min_value=0.0, max_value=20.0, value=(0.0, 20.0), step=0.1)
    snowfall_range = st.slider("Select a Snowfall range", min_value=0.00, max_value=2.00, value=(0.00, 2.00), step=0.01)
    rain_range = st.slider("Select a Rain range", min_value=0.0, max_value=20.0, value=(0.0, 20.0), step=0.1)

# Display the selected ranges
with st.expander('What is this Specific Scenario?'):
    st.title('What is this Specific Scenario?')
    st.write(f"Selected Latitude range: {lat_range[0]} to {lat_range[1]}")
    st.write(f"Selected Longitude range: {lon_range[0]} to {lon_range[1]}")
    st.write(f"Selected temperature range: {temperature_range[0]} to {temperature_range[1]}")
    st.write(f"Selected Relative Humidity range: {humidity_range[0]} to {humidity_range[1]}")
    st.write(f"Selected Dew Point range: {dewpoint_range[0]} to {dewpoint_range[1]}")
    st.write(f"Selected Precipitation range: {precipitation_range[0]} to {precipitation_range[1]}")
    st.write(f"Selected Snowfall range: {snowfall_range[0]} to {snowfall_range[1]}")
    st.write(f"Selected Rain range: {rain_range[0]} to {rain_range[1]}")

# Creating an empty DataFrame to store all data
all_data = pd.DataFrame()

if uploaded_files:
    for uploaded_file in uploaded_files:
        data = pd.read_csv(uploaded_file)
        data['minute'] = pd.to_datetime(data['minute'])  # Convert time format

        # Create marker color column based on selected anomaly detection method
        data['marker_color'] = 'blue'
        data.loc[data[anomaly_column] == -1, 'marker_color'] = 'red'

        # Filtering data based on the selected ranges
        data = data[
            (data['lat'] >= lat_range[0]) & (data['lat'] <= lat_range[1]) &
            (data['lon'] >= lon_range[0]) & (data['lon'] <= lat_range[1]) &
            (data['Temperature'] >= temperature_range[0]) & (data['Temperature'] <= temperature_range[1]) &
            (data['RelativeHumidity'] >= humidity_range[0]) & (data['RelativeHumidity'] <= humidity_range[1]) &
            (data['DewPoint'] >= dewpoint_range[0]) & (data['DewPoint'] <= dewpoint_range[1]) &
            (data['Precipitation'] >= precipitation_range[0]) & (data['Precipitation'] <= precipitation_range[1]) &
            (data['Snowfall'] >= snowfall_range[0]) & (data['Snowfall'] <= snowfall_range[1]) &
            (data['Rain'] >= rain_range[0]) & (data['Rain'] <= rain_range[1])
        ]

        # Merging data into the main DataFrame
        all_data = pd.concat([all_data, data], ignore_index=True)

    # Create map trajectory using Plotly Express
    fig = px.scatter_mapbox(all_data, 
                            lat='lat', 
                            lon='lon',
                            color='marker_color',
                            hover_data=['Elevation','mapped_veh_id', 'lat', 'lon', 'minute','RS_E_InAirTemp_PC1','RS_E_InAirTemp_PC2','RS_E_OilPress_PC1','RS_E_OilPress_PC2','RS_E_RPM_PC1','RS_E_RPM_PC2', 'RS_E_WatTemp_PC1','RS_E_WatTemp_PC2','RS_T_OilTemp_PC1','RS_T_OilTemp_PC2','Temperature','RelativeHumidity', 'DewPoint', 'Precipitation', 'Snowfall',  'Rain'],
                            title="Vehicle Trajectory Visualization in Belgium",
                            color_discrete_map={'red': 'red', 'blue': 'blue'})

    fig.update_layout(mapbox_style="open-street-map")
else:
    fig = go.Figure()

# 读取Railway line sections的轨迹数据
if uploaded_geojson:
    railway_sections_data = json.load(uploaded_geojson)
    
    # 处理 JSON 数据，提取坐标和相关属性
    for item in railway_sections_data:
        coordinates = item['geo_shape']['geometry']['coordinates']
        line = go.Scattermapbox(
            lat=[coord[1] for coord in coordinates],
            lon=[coord[0] for coord in coordinates],
            mode='lines',
            line=dict(
                width=2,
                color='gray'
            ),
            name=f"Railway Line {item['ls_id']}",
            hovertext=f"Label: {item['label']}, From: {item['ptcarfromname']} To: {item['ptcartoname']}"  # 添加悬停文本
        )
        fig.add_trace(line)

# Read station data
if uploaded_csv:
    station_data = pd.read_csv(uploaded_csv)
    fig.add_trace(go.Scattermapbox(
        lat=station_data['latitude'],
        lon=station_data['longitude'],
        text=station_data['name'],
        mode='markers',
        marker=dict(
            size=8,
            color='#2E8745',
            opacity=0.8,
            symbol='circle'
        ),
        name='Stations'
    ))

fig.update_layout(height=400, margin={"r":0,"t":0,"l":0,"b":0})
fig.update_layout(legend_title_text='Removable trails')

# Display the chart with Streamlit
st.plotly_chart(fig)

# Calculate and display anomaly statistics
if not all_data.empty:
    total_count = all_data.shape[0]
    anomaly_count = all_data[all_data[anomaly_column] == -1].shape[0]
    normal_count = total_count - anomaly_count
    anomaly_ratio = (anomaly_count / total_count) * 100 if total_count > 0 else 0
    with st.expander('Result in Specific Scenario:'):
        st.title('Result:')
        st.write(f"Total number of points: {total_count}")
        st.write(f"Number of normal points: {normal_count}")
        st.write(f"Number of anomaly points: {anomaly_count}")
        st.write(f"Anomaly ratio: {anomaly_ratio:.2f}%")

    # Filter out the anomalous data points
    anomalous_data = all_data[all_data[anomaly_column] == -1]

    # Display the anomalous data in a table
    if not anomalous_data.empty:
        with st.expander('Anomalous Data Points'):
            st.title('Anomalous Data Points:')
            st.dataframe(anomalous_data)
    else:
        st.write("No anomalous data points detected.")

