import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Sales Dashboard", 
                   page_icon=":star:",
                   layout="wide"
                   )

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

# Sidebar filter
st.sidebar.header("Filter on data")
year = st.sidebar.selectbox("Select year", options=df["year"].unique())

city = st.sidebar.multiselect("Select city", options=df["City"].unique(), default=df["City"].unique())
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

# df_selection = df.query("year == @year")
df_selection = df.query(
    "City == @city & Customer_type == @customer_type & Gender == @gender & year == @year")

st.title("Home")

st.write("Hello World")

st.divider()


show = st.toggle(label="Show dataframe", value=True)
if show:
    st.write(df_selection)

st.title("Top KPI:s")
total_sales = df_selection["Total"].sum()
average_sales = df_selection["Total"].mean()
average_rating = df_selection["Rating"].mean()

left_column, middle_column, right_column = st.columns(3)

with left_column:
    st.subheader(f"Total Sales: {total_sales}")

with middle_column:
    st.subheader(f"Average Sales: {average_sales:.2f}")

with right_column:
    st.subheader(f"Average Rating: {average_rating:.2f}")
    
    
col1, col2 = st.columns(2)

with col1:
    customer_type_data = df_selection["Customer_type"].value_counts().reset_index()
    customer_pie = px.pie(
        names=customer_type_data["Customer_type"],
        values=customer_type_data["count"],
        title="Customer types"
    )
    st.plotly_chart(customer_pie, use_container_width=True)

with col2:
    gender = df_selection["Gender"].value_counts()
    gender_pie_chart = px.pie(
        names=gender.index,
        values=gender,
        title="Gender"
    )
    gender_pie_chart.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(gender_pie_chart, use_container_width=True)
    
st.title("Sales")

st.subheader("Sales by product line")

s1 = (df_selection
                 .groupby("Product line")
                 .sum(numeric_only=True)[["Total"]]
                 .sort_values("Total")
                 )
sales_chart = px.bar(s1, x="Total", 
                     y=s1.index, 
                     orientation="h", 
                     title="Sales by product line", 
                     template="plotly_white")
st.plotly_chart(sales_chart)

# Sales by hour
st.subheader("Sales by hour")
s2 = df_selection.groupby("hour").sum(numeric_only=True)[
    ["Total"]].sort_values("Total")

sales_hour_chart = px.bar(s2, x="Total", y=s2.index,
                          title="Sales by the hour of day", template="plotly_white", orientation="h")
st.plotly_chart(sales_hour_chart)

# Sales by month
st.subheader("Sales by month")
s3 = df_selection.groupby("month").sum(numeric_only=True)[
    ["Total"]].sort_values("Total")

sales_by_month = px.bar(s3, y="Total", x=s3.index,
                        title="Sales by month", template="plotly_white")
st.plotly_chart(sales_by_month)

# Distribution by sales by product line
product_line_data = df_selection.groupby('Product line')['Total'].sum()

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


# Line charts

cumulative_sales_data = df_selection.groupby('Date')['Total'].sum().cumsum().reset_index()
cumulative_sales_chart = px.line(cumulative_sales_data, x=cumulative_sales_data["Date"],
                                 y=cumulative_sales_data["Total"],
                                 title='Cumulative Sales Over Time', 
                                 labels={'y': 'Cumulative Total Sales', 'x': 'Date'}
                                 )
st.plotly_chart(cumulative_sales_chart)

# Daily sales line chart

# Group data by Date
time_series_data = df_selection.groupby('Date')['Total'].sum().reset_index()

# Time Series Chart
time_series_chart = px.line(time_series_data,
                            x=time_series_data["Date"],
                            y=time_series_data["Total"],
                            title='Daily total sales',
                            labels={'y': 'Total Sales', 'x': 'Date'})

# Add interactive features
time_series_chart.update_traces(mode='lines+markers')
time_series_chart.update_layout(hovermode='x')

# Display in Streamlit
st.plotly_chart(time_series_chart, use_container_width=True)


# Heatmap

# HEATMAP
heatmap_data = df_selection.pivot_table(index='Day of Week', 
                              columns='hour', 
                              values='Total', 
                              aggfunc='sum')


# Create the heatmap
sales_heatmap = px.imshow(heatmap_data,
                          labels=dict(x="Hour of Day", y="Day of Week", color="Total Sales"),
                          title="Heatmap of Sales by Day and Hour",
                          aspect="auto"
                          )  # 'auto' adjusts the cell aspect ratio to the data


# Display in Streamlit
st.plotly_chart(sales_heatmap, use_container_width=True)

# Sales and Ratings Correlation Scatter Plot
st.title("Sales and Ratings Correlation")

# Filter data
filtered_data = df_selection[['Total', 'Rating']]

# Create the scatter plot
sales_ratings_scatter = px.scatter(filtered_data, x="Total", y="Rating",
                                   title="Correlation between Sales and Ratings",
                                   labels={'Total': 'Total Sales', 'Rating': 'Customer Rating'},
                                   trendline="ols",  # Add a trendline to analyze correlation
                                   template="plotly_white")

# Update layout for better visualization
sales_ratings_scatter.update_layout(xaxis_title='Total Sales',
                                    yaxis_title='Rating',
                                    xaxis_tickformat='$,.2f')  # Format x-axis as currency

# Display in Streamlit
st.plotly_chart(sales_ratings_scatter, use_container_width=True)


# Line chart

st.title("Product Line Profitability Over Time")

# Calculate monthly profit for each product line
monthly_profit_data = df_selection.groupby(['Date', 'Product line'])['Profit'].sum().reset_index()

# Sort the data by Date
monthly_profit_data.sort_values('Date', inplace=True)

# Create the line chart
profit_over_time_chart = px.line(monthly_profit_data, x='Date', y='Profit', color='Product line',
                                 title='Monthly Profit by Product Line',
                                 labels={'Profit': 'Monthly Profit', 'Date': 'Date'},
                                 template='plotly_white')

# Update layout for better visualization
profit_over_time_chart.update_layout(xaxis_title='Date',
                                     yaxis_title='Profit',
                                     xaxis_tickformat='%Y-%m')  # Format x-axis to show year-month

# Display in Streamlit
st.plotly_chart(profit_over_time_chart, use_container_width=True)