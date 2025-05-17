import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

st.set_page_config(page_title="Broker Performance Dashboard", layout="wide")
st.title("📊 Broker Performance Analytics Dashboard")
st.subheader("A simple streamlit application by Kathya Reynosa :)")

file = st.file_uploader("Upload Broker Data CSV", type=["csv"])
if file:
    with st.spinner("Processing..."):
        df = pd.read_csv(file)

    # Filters
    st.sidebar.header("🔍 Filter Data")
    min_success = st.sidebar.slider("Minimum Order Success Rate (%)", 0, 100, 50)
    filtered_df = df[df["order_success_rate"] >= min_success]

    # Data Preview
    st.subheader("🔎 Data Preview")
    st.dataframe(filtered_df.head())

    # Summary Metrics
    st.subheader("📈 Summary Metrics")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Brokers", filtered_df['name'].nunique())
    col2.metric("Total Tickets", filtered_df['tickets'].sum())
    col3.metric("Average Success Rate", f"{filtered_df['order_success_rate'].mean():.1f}%")

    # tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Resolution Time", "Success Rate", "Correlation", "Rankings", "Download"
    ])

    with tab1:
        st.subheader("⏱️ Avg Resolution Time by Broker")
        broker_avg = filtered_df.groupby("name").agg({
            "avg_resolution_time": "mean",
            "order_success_rate": "mean"
        }).reset_index()
        top_brokers = broker_avg.sort_values("avg_resolution_time", ascending=False).head(20)
        fig1 = px.bar(top_brokers, x="avg_resolution_time", y="name", orientation='h',
                      labels={"avg_resolution_time": "Avg Resolution Time (hrs)", "name": "Broker"})
        st.plotly_chart(fig1, use_container_width=True)

    with tab2:
        st.subheader("✅ Order Success Rate Distribution")
        fig2, ax2 = plt.subplots()
        sns.boxplot(y="order_success_rate", data=filtered_df, ax=ax2)
        ax2.set_ylabel("Order Success Rate (%)")
        st.pyplot(fig2)

    with tab3:
        st.subheader("📊 Correlation Heatmap")
        fig3, ax3 = plt.subplots()
        sns.heatmap(filtered_df.corr(numeric_only=True), annot=True, cmap="coolwarm", ax=ax3)
        st.pyplot(fig3)

    with tab4:
        st.subheader("🏆 Top & Bottom Brokers")
        st.markdown("### Top 5 by Success Rate")
        st.dataframe(broker_avg.sort_values("order_success_rate", ascending=False).head(5))

        st.markdown("### Bottom 5 by Success Rate")
        st.dataframe(broker_avg.sort_values("order_success_rate", ascending=True).head(5))

        st.markdown("### Custom Efficiency Score")
        broker_avg["efficiency_score"] = broker_avg["order_success_rate"] / broker_avg["avg_resolution_time"]
        st.dataframe(broker_avg.sort_values("efficiency_score", ascending=False).head(5))

        worst_broker = broker_avg.sort_values("avg_resolution_time", ascending=False).iloc[0]
        st.warning(f"⚠️ {worst_broker['name']} has the highest avg resolution time: {worst_broker['avg_resolution_time']:.2f} hrs")

    with tab5:
        st.subheader("📥 Export Filtered Data")
        csv = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Filtered Data as CSV", csv, "filtered_data.csv", "text/csv")

else:
    st.info("Please upload a CSV to begin.")
