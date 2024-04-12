import pandas as pd
import streamlit as st
import numpy as np
import plotly.express as px

st.set_page_config(page_title="Sales Dashboard",
                   page_icon=":star:", layout="wide")
st.title("Home")

@st.cache_data
def load_data():
    df = pd.read_csv("re_modified_supermarket_sales.csv")
    df["hour"] = pd.to_datetime(df["Time"]).dt.hour
    df["month"] = pd.to_datetime(df["Date"]).dt.month
    df["year"] = pd.to_datetime(df["Date"]).dt.year
    df['Day of Week'] = pd.to_datetime(df['Date']).dt.day_name()
    df['Profit'] = df['Total'] - df['cogs']
    return df


df = load_data()


st.sidebar.header("Filter here")

year = st.sidebar.selectbox("Select year", df["year"].unique())

city = st.sidebar.multiselect(
    "Select city",
    df["City"].unique(),
    df["City"].unique()
)

customer_type = st.sidebar.multiselect(
    "Select customer type",
    df["Customer_type"].unique(),
    df["Customer_type"].unique()
)

gender = st.sidebar.multiselect(
    "Select gender",
    df["Gender"].unique(),
    df["Gender"].unique()
)

df_selection = df.query(
    "City == @city & Customer_type == @customer_type & Gender == @gender & year == @year")

st.dataframe(df_selection)

st.title("Top KPI:s")
total_sales = int(df_selection["Total"].sum())
average_sales = df_selection["Total"].mean()
average_rating = df_selection["Rating"].mean()


left_column, middle_column, right_column = st.columns(3)

with left_column:
    st.subheader(f"Total Sales: {total_sales}")

with middle_column:
    st.subheader(f"Average Sales: {average_sales:.2f}")


with right_column:
    st.subheader(f"Average Rating: {average_rating:.2f}")

customer_type_data = df_selection['Customer_type'].value_counts()


col1, col2 = st.columns(2)

# First Pie Chart for Customer Types
with col1:
    customer_type_pie_chart = px.pie(names=customer_type_data.index,
                                     values=customer_type_data,
                                     title='Customer Types')
    # Use full column width
    st.plotly_chart(customer_type_pie_chart, use_container_width=True)

# Second Pie Chart for Gender Distribution
with col2:
    gender_data = df['Gender'].value_counts()
    gender_pie_chart = px.pie(names=gender_data.index,
                              values=gender_data,
                              title='Gender Distribution')
    st.plotly_chart(gender_pie_chart, use_container_width=True)

st.title("Sales")
st.subheader("Sales by Product Line")
s1 = df_selection.groupby("Product line").sum(
    numeric_only=True)[["Total"]].sort_values("Total")

sales_chart = px.bar(s1, x="Total", y=s1.index, title="Sales by Product Line",
                     template="plotly_white", orientation="h")
st.plotly_chart(sales_chart)

st.subheader("Sales by hour")
s2 = df_selection.groupby("hour").sum(numeric_only=True)[
    ["Total"]].sort_values("Total")

sales_hour_chart = px.bar(s2, x="Total", y=s2.index,
                          title="Sales by the hour of day", template="plotly_white", orientation="h")
st.plotly_chart(sales_hour_chart)

st.subheader("Sales by month")
s3 = df_selection.groupby("month").sum(numeric_only=True)[
    ["Total"]].sort_values("Total")

sales_by_month = px.bar(s3, y="Total", x=s3.index,
                        title="Sales by month", template="plotly_white")
st.plotly_chart(sales_by_month)

product_line_data = df_selection.groupby('Product line')['Total'].sum()

# Distribution by sales by product line
product_line_pie_chart = px.pie(product_line_data,
                                values='Total',
                                names=product_line_data.index,
                                title='Distribution of Sales by Product Line')


st.plotly_chart(product_line_pie_chart)

# Profit
profitability_data = df_selection.groupby('Product line')['Profit'].sum()
profitability_chart = px.bar(x=profitability_data.index, y=profitability_data, title='Profitability by Product Line',
                             labels={'y': 'Profit', 'x': 'Product Line'})
st.plotly_chart(profitability_chart, use_container_width=True)


# Cum sales
cumulative_sales_data = df_selection.groupby('Date')['Total'].sum().cumsum()
cumulative_sales_chart = px.line(cumulative_sales_data, x=cumulative_sales_data.index, y=cumulative_sales_data,
                                 title='Cumulative Sales Over Time', labels={'y': 'Cumulative Total Sales', 'x': 'Date'})
st.plotly_chart(cumulative_sales_chart, use_container_width=True)


# Group data by Date
time_series_data = df_selection.groupby('Date')['Total'].sum()

# Time Series Chart
time_series_chart = px.line(time_series_data,
                            x=time_series_data.index,
                            y=time_series_data,
                            title='Daily total sales',
                            labels={'y': 'Total Sales', 'x': 'Date'})

# Add interactive features
time_series_chart.update_traces(mode='lines+markers')
time_series_chart.update_layout(hovermode='x')

# Display in Streamlit
st.plotly_chart(time_series_chart, use_container_width=True)

# HEATMAP
heatmap_data = df.pivot_table(index='Day of Week', 
                              columns='hour', 
                              values='Total', 
                              aggfunc='sum')


# Create the heatmap
sales_heatmap = px.imshow(heatmap_data,
                          labels=dict(x="Hour of Day", y="Day of Week", color="Total Sales"),
                          title="Heatmap of Sales by Day and Hour",
                          aspect="auto")  # 'auto' adjusts the cell aspect ratio to the data


# Display in Streamlit
st.plotly_chart(sales_heatmap, use_container_width=True)

