import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import json

# Streamlit 应用的标题
st.title("Vehicle Trajectory Visualization in Belgium")

# 上传多个文件的部分
uploaded_files = st.file_uploader("Choose CSV files", type=["csv"], accept_multiple_files=True)
uploaded_geojson = st.file_uploader("Upload trajectories_geojson.json", type=["json"])
uploaded_csv = st.file_uploader("Upload stations.csv", type=["csv"])

# 添加异常值标记列的选择框
anomaly_column = st.selectbox("Anomaly Detection Methods", ["isolation_forest_anamoly", "lof_anamoly", "svm_anamoly", "knn_anamoly", "final_anomaly_flag"])

# 创建一个空的数据框以存储所有数据
all_data = pd.DataFrame()

if uploaded_files:
    # 循环读取每个上传的文件并合并它们
    for uploaded_file in uploaded_files:
        data = pd.read_csv(uploaded_file)
        data['minute'] = pd.to_datetime(data['minute'])  # 转换时间格式

        # 根据用户选择的异常值标记列来创建标记颜色列
        data['marker_color'] = 'blue'
        data.loc[data[anomaly_column] == -1, 'marker_color'] = 'red'

        # 合并数据到总数据框
        all_data = pd.concat([all_data, data], ignore_index=True)

    # 使用 Plotly Express 创建地图轨迹
    fig = px.scatter_mapbox(all_data, 
                      lat='lat', 
                      lon='lon',
                      color='marker_color',
                      hover_data=['Elevation','mapped_veh_id', 'lat', 'lon', 'minute','RS_E_InAirTemp_PC1','RS_E_InAirTemp_PC2','RS_E_OilPress_PC1','RS_E_OilPress_PC2','RS_E_RPM_PC1','RS_E_RPM_PC2', 'RS_E_WatTemp_PC1','RS_E_WatTemp_PC2','RS_T_OilTemp_PC1','RS_T_OilTemp_PC2','Temperature','RelativeHumidity', 'DewPoint', 'Precipitation', 'Snowfall',  'Rain'],
                      title="Vehicle Trajectory Visualization in Belgium",
                      color_discrete_map={'red': 'red', 'blue': 'blue'})  # 自定义颜色映射标签

    # 添加Google Maps图层作为基础图层
    fig.update_layout(mapbox_style="open-street-map")  # 使用OpenStreetMap图层
    #fig.update_layout(
    #mapbox_style="mapbox://styles/mapbox/satellite-streets-v11",
    #mapbox_accesstoken="#pk.eyJ1IjoiamludGFvLTE5OTkiLCJhIjoiY2xxYTJqdnBxMXU4cDJpbnVveG9lbWg2MCJ9.dBbBcVKb4hpO3d8WU2kYzw")
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

# 读取站点数据
if uploaded_csv:
    station_data = pd.read_csv(uploaded_csv)

    # 添加站点数据到基础地图图层
    fig.add_trace(go.Scattermapbox(
        lat=station_data['latitude'],
        lon=station_data['longitude'],
        text=station_data['name'],
        mode='markers',
        marker=dict(
            size=4,
            color='green',
            opacity=0.8,
            symbol='circle'
        ),
        name='Stations'
    ))

fig.update_layout(height=400, margin={"r":0,"t":0,"l":0,"b":0})
fig.update_layout(legend_title_text='Removable trails')

# 使用 Streamlit 显示图表
st.plotly_chart(fig)
