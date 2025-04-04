import streamlit as st
from scraper import scrape_and_clean, analyze_with_model
import matplotlib.pyplot as plt

st.title("Deals analyzer (Kolesa.kz)")

st.sidebar.header("🔧 Choose Scraping Parameters (only lowercase letters)")

city = st.sidebar.text_input("City", value="astana")
car_company = st.sidebar.text_input("Car brand", value="toyota")
car_model = st.sidebar.text_input("Car model", value="camry")
start_year = st.sidebar.number_input("Start year", value=2019, min_value=1990, max_value=2025)
max_page = st.sidebar.slider("Pages to scrape", min_value=1, max_value=50, value=15)

if st.button("Scrape and analyze"):
    with st.spinner("Scraping and analyzing data..."):
        df = scrape_and_clean(city=city, car_company=car_company, car_model=car_model, start_year=start_year, max_page=max_page)
        
        df_model = analyze_with_model(df)

        st.success("Done")

        st.subheader("Top 10 underrated camry deals")
        top = df_model[df_model['Deal Type'] == 'Underpriced'].sort_values(by='Residual', ascending=False).head(10)
        top['URL'] = top['URL'].apply(lambda link: f"[Open]({link})")
        top['Predicted Price'] = top['Predicted Price'].apply(lambda x: f"{int(x):,}")
        top['Residual'] = top['Residual'].apply(lambda x: f"{int(x):,}")
        top['Price'] = top['Price'].apply(lambda x: f"{int(x):,}")

        st.write(top[['Title', 'Price', 'Predicted Price', 'Residual', 'URL']].to_markdown(index=False), unsafe_allow_html=True)

        st.subheader("Full dataset")
        st.dataframe(df_model)

        with st.expander("Show charts"):
            st.subheader("Average price by year")
            avg_price_year = df.groupby("Year")["Price"].mean().reset_index()
            avg_price_year = avg_price_year.sort_values("Year")
            st.line_chart(data=avg_price_year, x='Year', y='Price')

            st.subheader("average price by condition")
            avg_price = df.groupby('Condition')['Price'].mean().reset_index()
            st.bar_chart(data=avg_price, x='Condition', y='Price')

            st.subheader("Mileage vs price")
            scatter_data = df[['Mileage (km)', 'Price']].sort_values('Mileage (km)')
            scatter_data = scatter_data.set_index('Mileage (km)')
            st.scatter_chart(scatter_data)