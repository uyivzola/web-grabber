import multiprocessing
import os
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

base_url = "https://candy-gold.uz"

url = base_url + "/products"

response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

# Main Directory where all images will be stored
main_directory = 'Candy-Gold'
os.makedirs(main_directory, exist_ok=True)

# Extract all product links from the main page

product_links = [a['href'] for a in soup.find_all('a', class_='products-item__more')]


def download_product_image(link):
    product_url = link

    if not product_url.startswith('http'):
        product_url = base_url + product_url

    # Get the content of the product page
    product_response = requests.get(product_url)
    product_soup = BeautifulSoup(product_response.content, 'html.parser')

    # Extract Product title
    product_title = product_soup.find('h1', class_='product__title').text.strip()

    # Extract the category for the subfolder (e.g. "shokolad" from 'product/shokolad-uzum")
    category = product_url.split('/')[-1].split('-')[0]

    # Directory for the specific category
    category_directory = os.path.join(main_directory, category)
    os.makedirs(category_directory, exist_ok=True)

    # Find the download link for the product image

    download_link = product_soup.find('a', class_='product-main__btn')['href']
    if not download_link.startswith('http'):
        download_link = base_url + download_link

    # Download the image and save it in the category subfolder with the product title as file_name.expression expression => png
    img_data = requests.get(download_link).content
    img_extension = os.path.splitext(download_link)[-1]  # Get the file name extension like jpg or png or heif or jpeg

    img_name = os.path.join(category_directory, f"{product_title}{img_extension}")

    with open(img_name, 'wb') as handler:
        handler.write(img_data)

    print(f'Downloaded image for product: {product_title} in the category-folder: {category}')

num_workers = multiprocessing.cpu_count()
with ThreadPoolExecutor(max_workers=num_workers) as executor:
    executor.map(download_product_image, product_links)

print('All images have been downloaded and organized into subfolders')


