from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import time
from sklearn.linear_model import LinearRegression

def scrape_and_clean(city, car_company, car_model, start_year, max_page):
    driver = webdriver.Chrome()
    base_url = f'https://kolesa.kz/cars/{car_company}/{car_model}/{city}/?year%5Bfrom%5D={start_year}'
    driver.get(base_url)
    time.sleep(5)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    pagination_links = soup.select('a[href*="page="]')
    pages = []
    for link in pagination_links:
        try:
            pages.append(int(link.get_text(strip=True)))
        except ValueError:
            continue
    
    cars = []
    
    if max_page == 50:
        max_page = max(pages) if pages else 5
    
    for page in range(1, max_page + 1):
        url = f'{base_url}&page={page}'
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'a-card__link')))
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        listings = soup.find_all('div', class_='a-list__item')

        for item in listings:
            header = item.find('div', class_='a-card__header')
            title_elem = header.find('h5', class_='a-card__title') if header else None
            link_elem = title_elem.find('a', class_='a-card__link') if title_elem else None
            price_elem = item.find('span', class_='a-card__price')
            desc_elem = item.find('p', class_='a-card__description')

            if title_elem and price_elem and desc_elem:
                title = title_elem.text.strip()
                price = price_elem.text.strip().replace('\xa0', ' ')
                description = desc_elem.text.strip()
                link = 'https://kolesa.kz' + link_elem['href'] if link_elem and link_elem.has_attr('href') else None

                cars.append({
                    'Title': title,
                    'Price': price,
                    'Description': description,
                    'URL': link
                })
        time.sleep(2)

    driver.quit()

    # DataFrame creation
    df = pd.DataFrame(cars)

    df['Year'] = df['Description'].str.extract(r'(\d{4}) г\.')
    df['Condition'] = df['Description'].str.extract(r'(Б/у|новый)')
    df['Car Type'] = df['Description'].str.extract(r'(седан|внедорожник|купе|хэтчбек|универсал|кроссовер)')
    df['Engine Size (L)'] = df['Description'].str.extract(r'(\d\.\d) л')
    df['Fuel Type'] = df['Description'].str.extract(r'(бензин|дизель|газ|гибрид|электро)')
    df['Transmission'] = df['Description'].str.extract(r'(КПП автомат|КПП механика|КПП вариатор|АКПП|МКПП)')
    df['Mileage (km)'] = df['Description'].str.extract(r'с пробегом ([\d\s]+) км')
    df.drop('Description', axis=1, inplace=True)

    df['Mileage (km)'] = df['Mileage (km)'].str.replace(' ', '').fillna('0').astype(int)

    condition_map = {"Б/у": "Used", "новый": "New"}
    car_type_map = {"седан": "Sedan", "внедорожник": "SUV", "купе": "Coupe", "хэтчбек": "Hatchback", "универсал": "Wagon", "кроссовер": "Crossover"}
    fuel_map = {"бензин": "Gasoline", "дизель": "Diesel", "газ": "Gas", "гибрид": "Hybrid", "электро": "Electric"}
    trans_map = {"КПП автомат": "Automatic", "КПП механика": "Manual", "КПП вариатор": "CVT", "АКПП": "Automatic", "МКПП": "Manual"}

    df['Condition'] = df['Condition'].map(condition_map)
    df['Car Type'] = df['Car Type'].map(car_type_map)
    df['Fuel Type'] = df['Fuel Type'].map(fuel_map)
    df['Transmission'] = df['Transmission'].map(trans_map)

    df['Year'] = pd.to_numeric(df['Year'], errors='coerce', downcast='integer')
    df['Price'] = df['Price'].str.replace(r'\D+', '', regex=True)
    df['Price'] = pd.to_numeric(df['Price'], errors='coerce', downcast='integer')
    df['Engine Size (L)'] = pd.to_numeric(df['Engine Size (L)'], errors='coerce')
    df['Engine Size (L)'] = df.apply(lambda row: 2.5 if '2.5' in row['Title'] else (3.5 if '3.5' in row['Title'] else row['Engine Size (L)']), axis=1)
    df['Engine Size (L)'] = df['Engine Size (L)'].fillna(df['Engine Size (L)'].mode()[0])
    df['Engine Size (L)'] = df['Engine Size (L)'].astype('category')

    return df

def analyze_with_model(df):
    df_model = df[['Title', 'URL', 'Price', 'Mileage (km)', 'Year', 'Engine Size (L)']].dropna()

    X = df_model[['Mileage (km)', 'Year', 'Engine Size (L)']]
    y = df_model['Price']

    model = LinearRegression()
    model.fit(X, y)

    df_model['Predicted Price'] = model.predict(X)
    df_model['Residual'] = df_model['Predicted Price'] - df_model['Price']

    def deal_type(residual):
        if residual > 1_000_000:
            return 'Underpriced'
        elif residual < -1_000_000:
            return 'Overpriced'
        return 'Fair'

    df_model['Deal Type'] = df_model['Residual'].apply(deal_type)

    return df_model
