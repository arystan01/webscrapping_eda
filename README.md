# Web scraper & price analyzer for car listings on Kolesa.kz

This project is a full-featured web scraping and data analysis tool that extracts listings of cars from [kolesa.kz](https://kolesa.kz), cleans and analyzes the data, and builds a regression model to detect **underpriced** and **overpriced** cars.

> Built with: Python, Selenium, BeautifulSoup, Pandas, Scikit-learn, Matplotlib, and Streamlit

---

## Features

- Web scraping of car listings in a selected city (e.g., Astana)
- Extracts title, price, year, mileage, engine size, condition, transmission, etc.
- Translates data from Russian to English
- Handles missing engine size values (2.5L or 3.5L)
- Builds linear regression model:  
  `Price = β₀ + β₁ × Mileage + β₂ × Year + β₃ × Engine Size`
- Detects **underpriced** and **overpriced** listings based on residuals
- Generates interactive charts using Streamlit
- Links to actual listings on Kolesa.kz

---

## Sample Outputs

- Top 10 underrated Toyota Camry with clickable URLs
- Predicted vs Actual Price scatter plot
- Mileage vs Price 
- Average price by condition
- Price trend over the years

---

## Regression Model

Built using `sklearn.linear_model.LinearRegression`, trained on features:

- `Mileage (km)`
- `Year`
- `Engine Size (L)`

Then predictions are compared against actual prices to classify cars as:

- Overpriced  
- Underpriced  
- Fair market value

---

## File Structure
├── Arystan_Webscrapping.ipynb     # Main Jupyter notebook with scraping, preprocessing, modeling, and EDA
├── scraper.py                     # (optional) Python module version of the scraper and model
├── main.py                        # Streamlit web app interface (uses scraper functions)
├── requirements.txt               # Python dependencies
└── README.md                      # Project documentation

---
