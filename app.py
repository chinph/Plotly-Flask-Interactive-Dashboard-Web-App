from flask import Flask, render_template, request
import plotly.express as px
import pandas as pd
import random
import numpy as np
import plotly.express as px
app = Flask(__name__)
import plotly.graph_objects as go

@app.route('/', methods=['GET', 'POST'])
def index():
    def glimpse(df):
        info = {
            "shape": f"{df.shape[0]} rows and {df.shape[1]} columns",
            "missing_values": df.isnull().sum().to_dict(),
            "head": df.head().to_html(),
            # "description": df.describe().to_html(),
            # "info": df.info(),
        }
        return info
    
    
    
    if request.method == 'POST':
        products_file = request.files['products_file']
        stores_file = request.files['stores_file']
        transactions_file = request.files['transactions_file']
        
        products = pd.read_csv(products_file)
        stores = pd.read_csv(stores_file)
        transactions = pd.read_csv(transactions_file)
        
        # Rest of your code
        # dataset_summaries = {}
        # for name, dataset in zip(["Products", "Stores", "Transactions"], [products, stores, transactions]):
        #     dataset_summaries[name] = glimpse(dataset)

        # Create a list of datasets
        datasets = [products, stores, transactions]
        # datasets = {"Products": products, "Stores": stores, "Transactions": transactions}

        # Loop through each dataset and apply the glimpse function
        dataset_summaries = {}
        for name, dataset in zip(["Products", "Stores", "Transactions"], datasets):
            dataset_summaries[name] = glimpse(dataset)
        # return render_template('index.html', dataset_summaries=dataset_summaries)

        # Change the data type of Price
        def convert_price(price_str):
            try:
                return float(price_str.strip("$").replace(",", ""))
            except ValueError:
                return None
            
        # Convert 'Price' columns in both tables to float
        transactions["Price"] = transactions["Price"].apply(convert_price)
        products["Price"] = products["Price"].apply(convert_price)

        # Print the updated data types
        print(transactions.dtypes)
        print(products.dtypes)

        transactions["PurchaseDate"] = pd.to_datetime(transactions["PurchaseDate"])


        # ### Output Performance

        # ### Total Customers 



        total_customers = transactions["CustomerID"].count()

        print("Total Number of Unique Customers:", total_customers)


        # ### Top transaction category



        # Group by ProductID and count the number of occurrences
        product_counts = (
            transactions.groupby("ProductID").size().reset_index(name="TransactionCount")
        )

        # Join with the products table to get the corresponding categories
        product_counts_with_categories = pd.merge(product_counts, products, on="ProductID")

        # Find the category with the highest total transactions
        top_category = (
            product_counts_with_categories.groupby("ProductCategory")["TransactionCount"]
            .sum()
            .idxmax()
        )

        print("Top Transaction Category by Total Transactions:", top_category)


        # ### Top transaction product


        # Find the product with the highest total transactions
        top_product = (
            product_counts_with_categories.groupby("ProductName")["TransactionCount"]
            .sum()
            .idxmax()
        )

        print("Top Transaction Category by Total Transactions:", top_product)

        transactions2 = transactions.copy()
        transactions2.info()


        # Total Customer by Days
        daily_customers = (
            transactions2.groupby("PurchaseDate")["CustomerID"].count().reset_index()
        )

        fig = px.area(
            daily_customers,
            x="PurchaseDate",
            y="CustomerID",
            title="<b>Total Customers by Days</b>",
            labels={"CustomerID": "<b>Total Customers</b>"},
            template="plotly_dark"
        )

        fig.update_traces(
            mode="lines+markers",
            marker=dict(
                symbol="circle", size=8, color="#043c7c", line=dict(width=2, color="white")
            ),
            line=dict(color="#043c7c", width=2),
            hovertemplate="<b>Date</b>: %{x}<br><b>Total Customers</b>: %{y}<extra></extra>",
        )

        # fig.update_xaxes(rangeslider_visible=True)

        fig.update_xaxes(title_text="<b>Date</b>")
        fig.update_yaxes(title_text="<b>Total Customers</b>")

        div = fig.to_html(full_html=False)


########################################
#
#
#               FIGURE 2
#
#
########################################

        weekday_customers = (
            transactions2.groupby(transactions2["PurchaseDate"].dt.dayofweek + 1)["CustomerID"]
            .count()
            .reset_index()
        )

        # Adjust the weekday order list
        weekday_order = [1, 2, 3, 4, 5, 6, 7]  # Sunday to Saturday order

        # Sort the DataFrame by the adjusted weekday order
        weekday_customers = weekday_customers.sort_values("PurchaseDate")

        fig2 = px.area(
            weekday_customers,
            x="PurchaseDate",
            y="CustomerID",
            title="<b>Total Customers by Weekdays</b>",
            labels={"CustomerID": "<b>Total Customers</b>"},
            template="plotly_dark",
        )

        fig2.update_traces(
            mode="lines+markers",
            marker=dict(
                symbol="circle", size=8, color="#043c7c", line=dict(width=2, color="white")
            ),
            line=dict(color="#043c7c", width=2),
            hovertemplate="<b>Weekday</b>: %{x}<br><b>Total Customers</b>: %{y}<extra></extra>",
        )

        fig2.update_xaxes(
            title_text="<b>Weekday</b>",
            tickvals=weekday_order,
            ticktext=["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"],
        )
        fig2.update_yaxes(title_text="<b>Total Customers</b>")

        div2 = fig2.to_html(full_html=False)


########################################
#
#
#               FIGURE 3
#
#
########################################


        # Join transactions with stores to get state information
        transactions_with_state = pd.merge(transactions2, stores, on="StoreID")

        # Group by day and state, then count unique customers
        transactions_with_state["Day"] = transactions_with_state["PurchaseDate"].dt.to_period(
            "D"
        )
        state_customer_count_by_day = (
            transactions_with_state.groupby(["Day", "StoreState"])["CustomerID"]
            .nunique()
            .reset_index()
        )

        # Get top 5 states with highest customer count for each day
        top_states_by_day = (
            state_customer_count_by_day.groupby("Day")
            .apply(lambda x: x.nlargest(5, "CustomerID"))
            .reset_index(drop=True)
        )

        # Convert Period objects to strings for x-axis labels
        top_states_by_day["Day"] = top_states_by_day["Day"].dt.to_timestamp()

        top_states_by_day = top_states_by_day[top_states_by_day["StoreState"] != "MD"]
        # Define custom colors for lines
        line_colors = ["white", "lightgrey", "lightpink", "blue", "yellow"]

        fig3 = px.line(
            top_states_by_day,
            x="Day",
            y="CustomerID",
            color="StoreState",
            title="Top 5 States with Highest Customer Count by Day",
            labels={"Day": "Day", "CustomerID": "Customer Count", "StoreState": "State"},
            template="plotly_dark",
        )

        for idx, state in enumerate(fig3.data):
            fig3.data[idx].line.color = line_colors[idx % len(line_colors)]

        fig3.update_traces(
            mode="lines+markers",  # Add markers to lines
            marker=dict(size=8),
            hovertemplate="<b>Day</b>: %{x}<br><b>Customer Count</b>: %{y}<extra></extra>",
        )

        fig3.update_xaxes(title_text="<b>Day</b>")
        fig3.update_yaxes(title_text="<b>Customer Count</b>")

        div3 = fig3.to_html(full_html=False)


########################################
#
#
#               FIGURE 4
#
#
########################################


        # Top States with Highest Customer Count 
        transactions_with_store = transactions_with_state.copy()
        # Group by day and store, then count unique customers
        transactions_with_store["Day"] = transactions_with_store["PurchaseDate"].dt.to_period(
            "D"
        )
        store_customer_count_by_day = (
            transactions_with_store.groupby(["Day", "StoreID"])["CustomerID"]
            .count()
            .reset_index()
        )

        # Get top 5 stores with highest customer count for each day
        top_stores_by_day = (
            store_customer_count_by_day.groupby("Day")
            .apply(lambda x: x.nlargest(5, "CustomerID"))
            .reset_index(drop=True)
        )

        # Convert Period objects to strings for x-axis labels
        top_stores_by_day["Day"] = top_stores_by_day["Day"].dt.to_timestamp()

        # Filter to include only the top 5 stores
        top_stores_by_day = top_stores_by_day[
            top_stores_by_day["StoreID"].isin([123, 102, 115, 146, 127])
        ]

        # Define custom colors for lines
        line_colors = ["white", "lightgrey", "lightpink", "blue", "yellow"]

        fig4 = px.line(
            top_stores_by_day,
            x="Day",
            y="CustomerID",
            color="StoreID",
            title="Top 5 Stores with Highest Customer Count by Day",
            labels={"Day": "Day", "CustomerID": "Customer Count", "StoreID": "Store"},
            template="plotly_dark",
        )

        for idx, store in enumerate(fig4.data):
            fig4.data[idx].line.color = line_colors[idx % len(line_colors)]

        fig4.update_traces(
            mode="lines+markers",  # Add markers to lines
            marker=dict(size=8),
            hovertemplate="<b>Day</b>: %{x}<br><b>Customer Count</b>: %{y}<extra></extra>",
        )

        fig4.update_xaxes(title_text="<b>Day</b>")
        fig4.update_yaxes(title_text="<b>Customer Count</b>")

        div4 = fig4.to_html(full_html=False)


########################################
#
#
#               FIGURE 5
#
#
########################################


        # Join transactions with stores and products to get state information (same as before)
        transactions_with_state_product = pd.merge(transactions, stores, on="StoreID")
        transactions_with_state_product = pd.merge(
            transactions_with_state_product, products, on="ProductID"
        )

        # Group by state and count unique customers (same as before)
        state_customer_count = (
            transactions_with_state_product.groupby("StoreState")["CustomerID"]
            .nunique()
            .reset_index()
        )

        # Select the top 10 states based on customer counts
        top_states = state_customer_count.sort_values(by="CustomerID", ascending=False).head(10)

        # Create the Plotly bar chart with divided categories
        fig5 = px.bar(
            top_states,
            x="CustomerID",
            y="StoreState",
            title="Top 10 States with Highest Customer Count",
            labels={"CustomerID": "Customer Count", "StoreState": "State"},
            template="plotly_dark",
            orientation="h",  # Horizontal bar chart
        )
        # Set the color of the bars
        fig5.update_traces(marker_color="#043c7c")

        fig5.update_layout(
            xaxis_title="<b>Customer Count</b>", yaxis_title="<b>State</b>",
        )

        div5 = fig5.to_html(full_html=False)

########################################
#
#
#               FIGURE 6
#
#
########################################

                
        # Join transactions with stores to get store information (updated with string StoreID)
        transactions_with_stores = transactions_with_state_product.copy()
        transactions_with_stores["StoreID"] = transactions_with_stores["StoreID"].astype(str)

        # Group by store and count unique customers
        store_customer_count = (
            transactions_with_stores.groupby("StoreID")["CustomerID"].nunique().reset_index()
        )

        # Select the top 10 stores based on customer counts
        top_stores = store_customer_count.sort_values(by="CustomerID", ascending=False).head(10)

        # Create the Plotly bar chart
        fig6 = px.bar(
            top_stores,
            x="CustomerID",
            y="StoreID",
            title="Top 10 Stores with Highest Customer Count",
            labels={"CustomerID": "Customer Count", "StoreID": "Store"},
            template="plotly_dark",
            orientation="h",  # Horizontal bar chart
        )

        # Set the color of the bars
        fig6.update_traces(marker_color="#043c7c")

        fig6.update_layout(
            xaxis_title="<b>Customer Count</b>", yaxis_title="<b>Store</b>",
        )

        div6 = fig6.to_html(full_html=False)

########################################
#
#
#               FIGURE 7
#
#
########################################

        # ### Category Purchase frequency 



        transactions_with_stores

        transactions_with_category = transactions_with_stores.copy()

        category_purchase_frequency = (
            transactions_with_category["ProductCategory"].value_counts(normalize=True) * 100
        )

        # Specify custom colors for the pie chart slices
        custom_colors = ["white", "lightgrey", "lightblue", "lightcoral"]

        # Create the Plotly pie chart with custom colors
        fig7 = px.pie(
            values=category_purchase_frequency.values,
            names=category_purchase_frequency.index,
            title="Percentage of Purchase Frequency by Category",
            color_discrete_sequence=custom_colors,
            template="plotly_dark",
        )

        # fig7.show()

        div7 = fig7.to_html(full_html=False)

        return render_template('index.html', plot_div=div, plot_div_2=div2, plot_div_3=div3, plot_div_4=div4, plot_div_5=div5, plot_div_6=div6, plot_div_7=div7)
            
    return render_template('index.html')

# @app.route('/')
# def index():
#     #modify
#     def glimpse(df):
#         info = {
#             "shape": f"{df.shape[0]} rows and {df.shape[1]} columns",
#             "missing_values": df.isnull().sum().to_dict(),
#             "head": df.head().to_html(),
#             # "description": df.describe().to_html(),
#             # "info": df.info(),
#         }
#         return info

#     # Create a list of datasets
#     datasets = [products, stores, transactions]
#     # datasets = {"Products": products, "Stores": stores, "Transactions": transactions}

#     # Loop through each dataset and apply the glimpse function
#     dataset_summaries = {}
#     for name, dataset in zip(["Products", "Stores", "Transactions"], datasets):
#         dataset_summaries[name] = glimpse(dataset)
#     # return render_template('index.html', dataset_summaries=dataset_summaries)


#     # Change the data type of Price
#     def convert_price(price_str):
#         try:
#             return float(price_str.strip("$").replace(",", ""))
#         except ValueError:
#             return None


#     # Convert 'Price' columns in both tables to float
#     transactions["Price"] = transactions["Price"].apply(convert_price)
#     products["Price"] = products["Price"].apply(convert_price)

#     # Print the updated data types
#     print(transactions.dtypes)
#     print(products.dtypes)

#     transactions["PurchaseDate"] = pd.to_datetime(transactions["PurchaseDate"])


#     transactions2 = transactions.copy()
#     transactions2.info()


#     # Revenue daily
#     daily_data = (
#         transactions2.groupby(transactions2["PurchaseDate"])
#         .agg(TotalRevenue=("Price", "sum"), NumOrders=("PurchaseDate", "count"))
#         .reset_index()
#     )

#     # Calculate per-order revenue
#     daily_data["PerOrderRevenue"] = daily_data["TotalRevenue"] / daily_data["NumOrders"]
#     daily_data

#     # Calculate average daily revenue
#     average_daily_revenue = daily_data["TotalRevenue"].mean()

#     # Create the Line Chart using Plotly
#     fig = px.line(
#         daily_data, x="PurchaseDate", y="TotalRevenue", title="<b> Daily Revenue Trends</b>"
#     )
#     fig.update_traces(
#         mode="lines+markers", marker=dict(size=8, line=dict(width=2, color="DarkSlateGrey"))
#     )

#     # Add a line for average daily revenue
#     fig.add_hline(
#         y=average_daily_revenue,
#         line_dash="dash",
#         line_color="grey",
#         annotation_text=f"Average: {average_daily_revenue:.2f}",
#         annotation_position="bottom left",
#     )

#     # Customize layout
#     fig.update_layout(
#         xaxis_title="<b>Purchase Date</b>",
#         yaxis_title="<b>Total Revenue</b>",
#         font=dict(family="Arial", size=12, color="Black"),
#         title_font=dict(family="Arial", size=16, color="Black"),
#         legend=dict(
#             title=None, orientation="h", y=1, yanchor="bottom", x=0.5, xanchor="center"
#         ),
#         margin=dict(l=50, r=20, t=60, b=50),
#         plot_bgcolor="white",
#     )

#     # Show the plot
#     # fig.show()
#     div = fig.to_html(full_html=False)

#     def convert_price(price_str):
#         try:
#             return float(price_str.strip("$").replace(",", ""))
#         except ValueError:
#             return None
        
#     #modify
#     transactions["Price"] = transactions["Price"].apply(lambda x: convert_price(x) if isinstance(x, str) else x)
#     products["Price"] = products["Price"].apply(lambda x: convert_price(x) if isinstance(x, str) else x)

#     # Print the updated data types
#     print(transactions.dtypes)
#     print(products.dtypes)
    
#     transactions["PurchaseDate"] = pd.to_datetime(transactions["PurchaseDate"])

#     transactions2 = transactions.copy()
#     transactions2.info()

#     # Revenue daily
#     daily_data = (
#         transactions2.groupby(transactions2["PurchaseDate"])
#         .agg(TotalRevenue=("Price", "sum"), NumOrders=("PurchaseDate", "count"))
#         .reset_index()
#     )








#     # Revenue per week
#     transactions2["Week"] = transactions2["PurchaseDate"].dt.to_period("W").dt.start_time

#     # Calculate total weekly revenue and number of orders per week
#     weekly_data = (
#         transactions2.groupby("Week")
#         .agg(TotalRevenue=("Price", "sum"), NumOrders=("PurchaseDate", "count"))
#         .reset_index()
#     )

#     # Calculate per-order revenue
#     weekly_data["PerOrderRevenue"] = weekly_data["TotalRevenue"] / weekly_data["NumOrders"]
#     weekly_data.info()

#     # Calculate average daily revenue
#     average_weekly_revenue = weekly_data["TotalRevenue"].mean()

#     # Create the Line Chart using Plotly
#     fig2 = px.line(
#         weekly_data, x="Week", y="TotalRevenue", title="<b> Weekly Revenue Trends</b>",
#     )
#     fig2.update_traces(
#         mode="lines+markers", marker=dict(size=8, line=dict(width=2, color="DarkSlateGrey"))
#     )

#     # Add a line for average daily revenue
#     fig2.add_hline(
#         y=average_weekly_revenue,
#         line_dash="dash",
#         line_color="grey",
#         annotation_text=f"Average: {average_weekly_revenue:.2f}",
#         annotation_position="bottom left",
#     )

#     # Customize layout
#     fig2.update_layout(
#         xaxis_title="<b>Week</b>",
#         yaxis_title="<b>Total Revenue</b>",
#         font=dict(family="Arial", size=12, color="Black"),
#         title_font=dict(family="Arial", size=16, color="Black"),
#         legend=dict(
#             title=None, orientation="h", y=1, yanchor="bottom", x=0.5, xanchor="center"
#         ),
#         margin=dict(l=50, r=20, t=60, b=50),
#         plot_bgcolor="white",
#     )

#     div2 = fig2.to_html(full_html=False)

#     return render_template('index.html', plot_div=div, plot_div2=div2, dataset_summaries=dataset_summaries)

# # @app.route('/update_data')
# # def update_data():
# #     global current_data
# #     current_data = generate_random_data()
# #     return "Data updated successfully!"

# # if __name__ == '__main__':
# #     app.run(debug=True)
