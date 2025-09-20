from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
from time import sleep
import csv
import sys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
import time

# Khởi tạo WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
print('- Finish initializing a driver')
list_url = []
list_brand = []

try:
    url = 'https://ntntech.vn/en/'
    driver.get(url)
    wait = WebDriverWait(driver, 20)
    
    # XPath định nghĩa
    outer_elements_xpath = '//*[@id="post-13769"]/div/div/section[4]/div/div/div/div/div/div/div/div'
    inner_elements_xpath = '//*[@id="main_loop"]/div'
    
    # Hàm helper để lấy dữ liệu
    def get_brands():
        page_source = BeautifulSoup(driver.page_source, 'html.parser')
        return [brand_div.find('a').get_text().strip() for brand_div in 
                page_source.find_all('div', class_='stocklist-info') if brand_div.find('a')]
    
    def get_urls():
        page_source = BeautifulSoup(driver.page_source, 'html.parser')
        return ['https://ntntech.vn' + link.get('href') for link in 
                page_source.find_all('a', class_='xts-product-link xts-fill')]
    
    # Xử lý các phần tử ngoài
    outer_elements = wait.until(EC.presence_of_all_elements_located((By.XPATH, outer_elements_xpath)))
    
    for i in range(len(outer_elements)):
        try:
            # Click phần tử ngoài
            element_to_click = wait.until(EC.element_to_be_clickable((By.XPATH, f"({outer_elements_xpath})[{i+1}]")))
            element_to_click.click()
            time.sleep(3)
            
            # Xử lý các phần tử trong
            inner_elements = wait.until(EC.presence_of_all_elements_located((By.XPATH, inner_elements_xpath)))
            
            for j in range(len(inner_elements)):
                try:
                    # Click phần tử trong
                    inner_element = wait.until(EC.element_to_be_clickable((By.XPATH, f"({inner_elements_xpath})[{j+1}]")))
                    inner_element.click()
                    time.sleep(3)
                    
                    # Lấy dữ liệu
                    brands = get_brands()[1::2]  # Lấy các phần tử ở vị trí lẻ
                    
                    if not brands:  # Nếu không có brand, xử lý phần tử pant
                        pant_elements = wait.until(EC.presence_of_all_elements_located((By.XPATH, inner_elements_xpath)))
                        
                        for k in range(len(pant_elements)):
                            try:
                                pant_element = wait.until(EC.element_to_be_clickable((By.XPATH, f"({inner_elements_xpath})[{k+1}]")))
                                pant_element.click()
                                time.sleep(3)
                                
                                # Thu thập dữ liệu
                                list_url.extend(get_urls())
                                list_brand.extend(get_brands()[1::2])
                                
                                driver.back()
                            except (StaleElementReferenceException, TimeoutException):
                                driver.refresh()
                                time.sleep(2)
                                continue
                    else:
                        # Thu thập dữ liệu trực tiếp
                        list_url.extend(get_urls())
                        list_brand.extend(brands)
                    
                    driver.back()
                except (StaleElementReferenceException, TimeoutException):
                    driver.refresh()
                    time.sleep(2)
                    continue
                    
            driver.back()
        except (StaleElementReferenceException, TimeoutException):
            driver.refresh()
            time.sleep(2)
            continue
            
except Exception as e:
    print(f"\nAn unexpected error occurred: {e}")

finally:
    print(f"\n- Total URLs collected: {len(list_url)}")
    print(f"- Total Brands collected: {len(list_brand)}")

    # Ghi dữ liệu sản phẩm vào file CSV
    with open('data.csv', 'w', newline='', encoding='utf-8') as file_output:
        headers = ['product_name', 'description_1', 'description_2', 'download_link', 'Categories', 'Brands', 'URL']
        writer = csv.DictWriter(file_output, delimiter=',', lineterminator='\n', fieldnames=headers)
        writer.writeheader()

        for product_URL in list_url:
            try:
                driver.get(product_URL)
                print(f'- Accessing profile: {product_URL}')
                sleep(3)

                page_source = driver.page_source
                soup = BeautifulSoup(page_source, 'html.parser')

                # Trích xuất dữ liệu sản phẩm
                product_name = ''
                name = soup.find('div', class_='summary entry-summary xts-single-product-summary')
                product_name = name.find('h1', class_='product_title entry-title').get_text().strip() if name else None

                download_link = ''
                link_loc = soup.find('a', class_='stocklist-btn2 download')
                if link_loc:
                    download_link = link_loc.get('href')

                Categories = ''
                categories_loc = soup.find('div', class_='product_meta')
                if categories_loc:
                    category_a = categories_loc.find('a')
                    if category_a:
                        Categories = category_a.get_text().strip()

                Brands = ''
                    
                description_1 = ''
                des_1_loc = soup.find('div', class_='woocommerce-Tabs-panel--description')
                if des_1_loc:
                    description_1_text = []
                    all_content_tags = des_1_loc.find_all(['p', 'li'])
                    for tag in all_content_tags:
                        description_1_text.append(tag.get_text().strip())
                    description_1 = ' '.join(description_1_text)

                description_2 = ''
                des_2_loc = soup.find('div', class_='chong-copy')
                if des_2_loc:
                    image_urls = []
                    all_images = des_2_loc.find_all('img')
                    for img in all_images:
                        src = img.get('src')
                        if src:
                            image_urls.append(src)
                    description_2 = ', '.join(image_urls)
                
                # Ghi dữ liệu vào file CSV
                writer.writerow({
                    'product_name': product_name,
                    'description_1': description_1,
                    'description_2': description_2,
                    'download_link': download_link,
                    'Categories': Categories,
                    'Brands': Brands,
                    'URL': product_URL
                })
                
                print('--- Product name is:', product_name)
                print('--- Download link is:', download_link)
                print('--- Categories is:', Categories)
                print('--- Brands is:', Brands)
                print('--- Description 1 is:', description_1)
                print('--- Description 2 is:', description_2)
                print('--- Product URL is:', product_URL)
                print('\n')

            except Exception as e:
                print(f"Could not scrape data from {product_URL}: {e}")
                print('\n')

    # Ghi dữ liệu brand vào file CSV
    with open('Brand.csv', 'w', newline='', encoding='utf-8') as file_output:
        headers = ['Brands']
        writer = csv.DictWriter(file_output, delimiter=',', lineterminator='\n', fieldnames=headers)
        writer.writeheader()

        for brand_name in list_brand:
            writer.writerow({
                'Brands': brand_name,
            })
            print('--- Brands is:', brand_name)
        
    print("\n- Script finished. Quitting driver.")
    driver.quit()