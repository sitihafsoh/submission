import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')



# create_daily_orders_df() digunakan untuk menyiapkan daily_orders_df
def create_daily_orders_df(df):
    daily_orders_df = df.resample(rule='D', on='order_purchase_timestamp').agg({
        "order_id": "nunique",
        "customer_id": "nunique",
        "seller_id": "nunique",
        "price": "sum"
    })
    daily_orders_df = daily_orders_df.reset_index()
    daily_orders_df.rename(columns={
        "order_id": "order_count",
        "customer_id": "customer_count",
        "seller_id": "seller_count",
        "price": "revenue"
    }, inplace=True)

    return daily_orders_df

# create_monthly_orders_df() bertanggung jawab untuk menyiapkan monthly_orders_df
def create_monthly_orders_df(df):
    monthly_orders_df = df.resample(rule='M', on='order_purchase_timestamp').agg({
        "order_id": "nunique",
        "price": "sum"
    })

    monthly_orders_df.index = monthly_orders_df.index.strftime('%y-%m')

    monthly_orders_df = monthly_orders_df.reset_index()
    monthly_orders_df.rename(columns={
        "order_id": "order_count",
        "price": "revenue"
    }, inplace=True)

    return monthly_orders_df

# create_sum_order_items_df digunakan untuk menyiapkan sum_order_items_df
def create_sum_order_items_df(df):
    sum_order_items_df = df.groupby("product_category_name").order_item_id.sum().sort_values(ascending=False).reset_index()
    return sum_order_items_df

# create_customer_state_df digunakan untuk menyiapkan customer_state_df
def create_customer_state_df(df):
    customer_state_df = df.groupby("customer_state").customer_id.nunique().sort_values(ascending=False).reset_index()
    
    customer_state_df.rename(columns={
        "customer_id": "customer_count"
    }, inplace=True)
    return customer_state_df

# create_customer_city_df digunakan untuk menyiapkan customer_city_df
def create_customer_city_df(df):
    customer_city_df = df.groupby("customer_city").customer_id.nunique().sort_values(ascending=False).reset_index().head(10)
    
    customer_city_df.rename(columns={
        "customer_id": "customer_count"
    }, inplace=True)
    return customer_city_df

# create_seller_state_df digunakan untuk menyiapkan seller_state_df
def create_seller_state_df(df):
    seller_state_df = df.groupby("seller_state").seller_id.nunique().sort_values(ascending=False).reset_index()

    seller_state_df.rename(columns={
        "seller_id": "seller_count"
    }, inplace=True)
    return seller_state_df

# create_seller_city_df digunakan untuk menyiapkan seller_city_df
def create_seller_city_df(df):
    seller_city_df = df.groupby("seller_city").seller_id.nunique().sort_values(ascending=False).reset_index().head(10)

    seller_city_df.rename(columns={
        "seller_id": "seller_count"
    }, inplace=True)
    return seller_city_df



# load berkas all_data sebagai sebuah DataFrame
all_df = pd.read_csv("main_data.csv")



# mengurutkan DataFrame berdasarkan order_purchase_timestamp
datetime_columns = ["shipping_limit_date", "order_purchase_timestamp", "order_approved_at", "order_delivered_carrier_date", "order_delivered_customer_date", "order_estimated_delivery_date"]
all_df.sort_values(by="order_purchase_timestamp", inplace=True)
all_df.reset_index(inplace=True)

for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])



# membuat filter dengan widget date input seta menambahka logo perusahaan pada sidebar
min_date = all_df["order_purchase_timestamp"].min()
max_date = all_df["order_purchase_timestamp"].max()

with st.sidebar:
    # Menambahkan logo perusahaan
    st.image("https://img.freepik.com/premium-vector/ecommerce-logo-design_691522-88.jpg?w=740")

    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

# start_date dan end_date di atas akan digunakan untuk memfilter all_df. Data yang telah difilter ini selanjutnya akan disimpan dalam main_df
main_df = all_df[(all_df["order_purchase_timestamp"] >= str(start_date)) &
                 (all_df["order_purchase_timestamp"] <= str(end_date))]

# main_df digunakan untuk menghasilkan berbagai DataFrame yang dibutuhkan untuk membuat visualisasi data. Memanggil helper function yang telah dibuat sebelumnya
daily_orders_df = create_daily_orders_df(main_df)
monthly_orders_df = create_monthly_orders_df(main_df)
sum_order_items_df = create_sum_order_items_df(main_df)
customer_state_df = create_customer_state_df(main_df)
customer_city_df = create_customer_city_df(main_df)
seller_state_df = create_seller_state_df(main_df)
seller_city_df = create_seller_city_df(main_df)



# memunculkan tampilan teks title dan markdown
st.title('**DASHBOARD**')
st.markdown('Evaluasi Performa Penjualan 2016-2018')



# menampilkan kolom berisi 4 metrik terkait Total Order, Total Revenue, Total Customer, dan Total Seller 
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_orders = daily_orders_df.order_count.sum()
    st.metric("**Total Order:**", value=total_orders)

with col2:
    total_revenue = format_currency(daily_orders_df.revenue.sum(), "BRL", locale='pt_BR')
    st.metric("**Total Revenue:**", value=total_revenue)

with col3:
    total_customers = daily_orders_df.customer_count.sum()
    st.metric("**Total Customer:**", value=total_customers)

with col4:
    total_sellers = daily_orders_df.seller_count.sum()
    st.metric("**Total Seller:**", value=total_sellers)



# menampilkan order & revenue summary
st.subheader("Order & Revenue Summary")

col1, col2 = st.columns(2)

with col1:
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(
        monthly_orders_df["order_purchase_timestamp"],
        monthly_orders_df["order_count"],
        marker='o',
        linewidth=2,
        color="#72BCD4"
    )

    ax.set_title("Total Order per Bulan (2016-2018)", loc="center", fontsize=20)
    ax.tick_params(axis='y', labelsize=20)
    ax.tick_params(axis='x', labelsize=15, rotation=45)
    st.pyplot(fig)
with col2:
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(
        monthly_orders_df["order_purchase_timestamp"],
        monthly_orders_df["revenue"],
        marker='o',
        linewidth=2,
        color="#72BCD4"
    )

    ax.set_title("Total Revenue per Bulan (2016-2018)", loc="center", fontsize=20)
    ax.tick_params(axis='y', labelsize=20)
    ax.tick_params(axis='x', labelsize=15, rotation=45)
    st.pyplot(fig)



# menampilkan produk paling banyak dan paling sedikit diminati oleh pelanggan
st.subheader("Produk Paling Banyak dan Paling Sedikit Diminati")

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(24,6))

colors = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

sns.barplot(x="order_item_id", y="product_category_name", data=sum_order_items_df.sort_values(by="order_item_id", ascending=False).head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("Produk yang Paling Banyak Diminati", loc="center", fontsize=15)
ax[0].tick_params(axis = 'y', labelsize=12)

sns.barplot(x="order_item_id", y="product_category_name", data=sum_order_items_df.sort_values(by="order_item_id", ascending=True).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Produk yang Paling Sedikit Diminati", loc="center", fontsize=15)
ax[1].tick_params(axis='y', labelsize=12)

st.pyplot(fig)



# menampilkan demografi pelanggan
st.subheader("Demografi Pelanggan")

#menampilkan demografi pelanggan berdasarkan negara (state)
fig, ax = plt.subplots(figsize=(10, 5))
colors_ = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
sns.barplot(
    x="customer_count",
    y="customer_state",
    data=customer_state_df.sort_values(by="customer_count", ascending=False),
    palette=colors_
)
ax.set_title("Demografi Pelanggan Berdasarkan Negara", loc="center", fontsize=15)
ax.set_ylabel(None)
ax.set_xlabel(None)
ax.tick_params(axis='y', labelsize=12)
st.pyplot(fig)

# menampilkan demografi pelanggan berdasarkan kota (city)
col1, col2 = st.columns(2)

with col1:
    fig, ax=plt.subplots(figsize=(10, 5))
    colors_ = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
    sns.barplot(
        x="customer_count",
        y="customer_city",
        data=customer_city_df.sort_values(by="customer_count", ascending=False),
        palette=colors_
    )
    ax.set_title("10 Kota dengan Pelanggan Paling Banyak", loc="center", fontsize=15)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.tick_params(axis='y', labelsize=12)
    st.pyplot(fig)

with col2:
    fig, ax=plt.subplots(figsize=(10, 5))
    colors_ = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
    sns.barplot(
        x="customer_count",
        y="customer_city",
        data=customer_city_df.sort_values(by="customer_count", ascending=True),
        palette=colors_
    )
    ax.set_title("10 Kota dengan Pelanggan Paling Sedikit", loc="center", fontsize=15)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.tick_params(axis='y', labelsize=12)
    st.pyplot(fig)




# menampilkan demografi penjual
st.subheader('Demografi Penjual')

# menampilkan demografi penjual (seller) berdasarkan negara
fig, ax=plt.subplots(figsize=(10, 5))
colors_ = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
sns.barplot(
    x="seller_count",
    y="seller_state",
    data=seller_state_df.sort_values(by="seller_count", ascending=False),
    palette=colors_
)
ax.set_title("Demografi Penjual Berdasarkan Negara", loc="center", fontsize=15)
ax.set_ylabel(None)
ax.set_xlabel(None)
ax.tick_params(axis='y', labelsize=12)
st.pyplot(fig)

# menampilkan demografi penjual berdasarkan kota
col1, col2 = st.columns(2)

with col1:
    fig, ax = plt.subplots(figsize=(10, 5))
    colors_ = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
    sns.barplot(
        x="seller_count",
        y="seller_city",
        data=seller_city_df.sort_values(by="seller_count", ascending=False),
        palette=colors_
    )
    ax.set_title("10 Kota dengan Penjual Paling Banyak", loc="center", fontsize=15)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.tick_params(axis='y', labelsize=12)
    st.pyplot(fig)
with col2:
    fig, ax = plt.subplots(figsize=(10, 5))
    colors_ = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
    sns.barplot(
        x="seller_count",
        y="seller_city",
        data=seller_city_df.sort_values(by="seller_count", ascending=True),
        palette=colors_
    )
    ax.set_title("10 Kota dengan Penjual Paling Sedikit", loc="center", fontsize=15)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.tick_params(axis='y', labelsize=12)
    st.pyplot(fig)