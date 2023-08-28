# Import necessary libraries
import aiohttp
import asyncio
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options  # For Chrome


# Define the initial URL to start scraping from
initial_url = 'https://divar.ir/s/tehran/car?brand_model_manufacturer_origin=domestic&has-photo=true'

# Initialize an empty list to store car data
car_data = []

# Define an asynchronous function to scroll down the page using the Selenium driver
async def scroll_down_page(driver):
    # Execute JavaScript to scroll to the bottom of the page
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    await asyncio.sleep(2)  # Wait for 2 seconds to allow content to load

# Define an asynchronous function to process post data from a specific post link
async def process_post_page(post_link):
    # Construct the URL of the post from the provided link
    post_url = 'https://divar.ir' + post_link['href']
    # Send a GET request to the post URL
    async with aiohttp.ClientSession() as session:  # Create an HTTP session using aiohttp
        async with session.get(post_url) as post_response:
            if post_response.status == 200:  # Check if the response status is OK
                # Parse the HTML content of the post page
                post_soup = BeautifulSoup(await post_response.text(), 'html.parser')
                record_dic = {}
                
                # Extract car information using specific classes and text patterns
                car_info_list = post_soup.find_all('div', class_='kt-base-row__end kt-unexpandable-row__value-box')
                for i in car_info_list: 
                    if i.previous_sibling.get_text() == 'برند و تیپ':
                        record_dic['title'] = i.get_text()
                    elif i.previous_sibling.get_text() == 'نوع سوخت':
                        record_dic['feul type'] = i.get_text()
                    elif i.previous_sibling.get_text() == 'وضعیت موتور':
                        record_dic['engine condition'] = i.get_text()
                    elif i.previous_sibling.get_text() == 'وضعیت شاسی‌ها':
                        record_dic['chassis condition'] = i.get_text()
                    elif i.previous_sibling.get_text() == 'وضعیت بدنه':
                        record_dic['body condition'] = i.get_text()
                    elif i.previous_sibling.get_text() == 'مهلت بیمهٔ شخص ثالث':
                        record_dic['insurance expiration'] = i.get_text()
                    elif i.previous_sibling.get_text() == 'گیربکس':
                        record_dic['gearbox type'] = i.get_text()
                    elif i.previous_sibling.get_text() == 'قیمت پایه':
                        record_dic['price'] = i.get_text()
                    # Continue extracting other car details using similar if-elif blocks
                
                # Extract additional car details like color, year, and mileage
                post_color_year_mileage_elements = post_soup.find_all('span', class_='kt-group-row-item__value')
                for i in post_color_year_mileage_elements: 
                    if i.previous_sibling.get_text() == 'کارکرد':
                        record_dic['mileage'] = i.get_text()
                    elif i.previous_sibling.get_text() == 'مدل (سال تولید)':
                        record_dic['production year'] = i.get_text()
                    elif i.previous_sibling.get_text() == 'رنگ':
                        record_dic['color'] = i.get_text()
                    # Continue extracting other details using similar if-elif blocks
                
                # Extract car description
                car_description = post_soup.find('p', class_='kt-description-row__text kt-description-row__text--primary')
                if car_description:
                    record_dic['car description'] = car_description.get_text()
                
                # Store the post URL
                record_dic['URL'] = post_url
                
                # Append the record to the car data list
                car_data.append(record_dic)

# Define the main asynchronous function
async def main():
    # Create a ChromeOptions object
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Add the headless argument
    # Set up the Selenium driver for web automation
    driver = webdriver.Chrome(options=chrome_options)  # You can replace this with your preferred browser driver
    driver.get(initial_url)  # Open the initial URL in the browser

    num_scroll = 0  # Number of times to scroll the page
    for scroll in range(0, num_scroll + 1):
        print(f"Processing scrolled page: {scroll + 1}")
        
        # check if it is the initial page, don't scroll
        if scroll != 0:
            await scroll_down_page(driver)  # Scroll down the page asynchronously
        
        # Extract post links from the page
        page_content = driver.page_source
        soup = BeautifulSoup(page_content, 'html.parser')
        post_list_element = soup.find('div', class_='browse-post-list-f3858')
        posts = post_list_element.find_all('div', class_='post-card-item-af972 kt-col-6-bee95 kt-col-xxl-4-e9d46')
        post_links = [post.find('a') for post in posts]

        if not post_links:
            break  # Stop crawling if there are no post links on the page

        tasks = []  # List to store asynchronous tasks
        for entry_number, post_link in enumerate(post_links, start=1):
            print(f"Processing scrolled page: {scroll + 1} - Entry: {entry_number}")
            tasks.append(process_post_page(post_link))  # Add tasks to the list
        
        # Execute the post-processing tasks concurrently
        await asyncio.gather(*tasks)
    
    driver.quit()  # Close the browser

# Run the event loop
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())  # Execute the main asynchronous function

# Create a DataFrame from the collected post data list and save it to a CSV file
try:
    df = pd.DataFrame(car_data)
    df.to_csv(r'divar.csv', index=False, encoding='utf-8-sig')
    print('=================================================')
    print('Data has been successfully saved to the file')
except Exception as e:
    print('=================================================')
    print('An error occurred:', str(e))
    print("An error occurred while saving the data to the file. Please check for any issues.")
