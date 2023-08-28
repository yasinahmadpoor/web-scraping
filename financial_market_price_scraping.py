import requests
from bs4 import BeautifulSoup
import datetime 
import os
import csv

# Function to retrieve the HTML content of the target page
def get_page_html():
    # Send an HTTP GET request to the specified URL
    whole_page = requests.get('https://www.tgju.org/')
    
    # Get the status code of the HTTP response
    status = whole_page.status_code
    
    # Create a BeautifulSoup object to parse the HTML content
    soup = BeautifulSoup(whole_page.content, 'html.parser')
    
    return soup, status

# Function to extract cryptocurrency prices from the HTML
def get_crypto_price(html_page):
    # Find the HTML div element containing cryptocurrency data
    crypto_table = html_page.find('div', class_="index-tabs-data crypto-tabs-mobile2")
    crypto_table = crypto_table.find('tbody')
    
    # Find all the cryptocurrency dollar prices
    crypto_dollar_prices = crypto_table.find_all('td', class_="market-price")
    
    # Find all the cryptocurrency names
    crypto_names = crypto_table.find_all('th')

    dict = {}
    for crypto_name, crypto_price in zip(crypto_names, crypto_dollar_prices):
        crypto_name = crypto_name.get_text().strip()
        dict[crypto_name] = crypto_price.get_text().strip()

    return dict

# Function to extract currency prices from the HTML
def get_currency_price(html_page):
    # Find the HTML div element containing currency data
    currency_table = html_page.find('div', class_="col-12 col-xl-12 index-tabs-hide-mobile acc-index-tabs")
    currency_table = currency_table.find('tbody')
    
    # Find all the currency dollar prices
    currency_dollar_prices = currency_table.find_all('td', class_="market-currency-sana-sell")
    
    # Find all the currency names
    currency_names = currency_table.find_all('th')

    dict = {}
    for currency_name, currency_price in zip(currency_names, currency_dollar_prices):
        currency_name = currency_name.get_text().strip()
        dict[currency_name] = currency_price.get_text().strip()

    return dict

# Function to extract other financial market prices from the HTML
def get_all_financial_market_prices(html_page):
    # Find the HTML container element for financial market data
    financial_market_table = html_page.find(class_="container")
    
    # Find all the financial market prices
    financial_market_prices = financial_market_table.find_all('span', class_="info-value")
    
    # Find all the financial market names
    financial_market_names = financial_market_table.find_all('h3')

    dict = {}
    for financial_market_name, financial_market_price in zip(financial_market_names, financial_market_prices):
        financial_market_name = financial_market_name.get_text().strip()
        dict[financial_market_name] = financial_market_price.get_text().strip()

    return dict

# Function to check if data for the given date and hour already exists in the CSV
def check_existing_data(csv_path, target_date):
    if not os.path.exists(csv_path):
        return False
    
    # Open the CSV file to check for existing data
    with open(csv_path, mode='r', newline='', encoding='utf-8-sig') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[-1] == target_date:
                return True
    return False

# Function to write data to the CSV file
def write_to_txtfile(crypto_price, currancy_price, financial_market_price):
    merged_dict = {**crypto_price, **crypto_price, **financial_market_price}
    current_datetime = datetime.datetime.now().strftime('%Y-%m-%d %H')  # Get current date and time
    merged_dict['تاریخ و ساعت'] = current_datetime
        
    # Path to the CSV file
    csv_file_path = "financial_market.csv"
    
    # Check if data already exists for the current date and hour
    if check_existing_data(csv_file_path, current_datetime):
        print(f"Data already exists for the date and hour: {current_datetime}. Skipping addition.")
        return

    # Check if the CSV file exists or not
    file_exists = os.path.exists(csv_file_path)

    # Open the CSV file in append mode ('a+') to create if it doesn't exist
    with open(csv_file_path, mode='a+',  newline='', encoding='utf-8-sig') as file:
        # Create a CSV writer object
        writer = csv.writer(file)

        # Write the header row if the file was just created
        if not file_exists:
            writer.writerow(list(merged_dict.keys()))

        # Write the new data to the file
        writer.writerow(merged_dict.values())

    print("Data appended to CSV file.")

# Main code execution starts here
if __name__ == '__main__':
    # Retrieve the HTML content of the target page
    page, _ = get_page_html()
    
    # Extract cryptocurrency prices
    crypto_price = get_crypto_price(page)
    
    # Extract currency prices
    currancy_price = get_currency_price(page)
    
    # Extract other financial market prices
    financial_market_price = get_all_financial_market_prices(page)
    
    # Write the extracted data to the CSV file
    write_to_txtfile(crypto_price, currancy_price, financial_market_price)
