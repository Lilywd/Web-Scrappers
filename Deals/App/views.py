from django.shortcuts import render,  redirect
import requests 
from bs4 import BeautifulSoup
from django.http import JsonResponse
import re
import aiohttp
import asyncio
from django.core.mail import send_mail
from django.conf import settings

# product_list = [
#     {'image_link': 'https://www.beautysquareke.com/beautykcot/uploads/2023/10/Anua-TONER.webp', 'product_name': 'Anua Heartleaf  77% Soothing Toner, 250ml', 'product_price': 'KSh3,200', 'source': 'Beautysquareke', 'link': 'https://www.beautysquareke.com/product/anua-heartleaf--77%-soothing-toner,-250ml/'},
#     {'image_link': 'https://www.beautysquareke.com/beautykcot/uploads/2023/10/Anua-TONER.webp', 'product_name': 'Anua Heartleaf  77% Soothing Toner, 250ml', 'product_price': 'KSh3,200', 'source': 'Beautysquareke', 'link': 'https://www.beautysquareke.com/product/anua-heartleaf--77%-soothing-toner,-250ml/'},
#     {'image_link': 'https://www.beautysquareke.com/beautykcot/uploads/2023/10/Anua-TONER.webp', 'product_name': 'Anua Heartleaf  77% Soothing Toner, 250ml', 'product_price': 'KSh3,200', 'source': 'Beautysquareke', 'link': 'https://www.beautysquareke.com/product/anua-heartleaf--77%-soothing-toner,-250ml/'},
#     {'image_link': 'https://www.beautysquareke.com/beautykcot/uploads/2023/10/Anua-TONER.webp', 'product_name': 'Anua Heartleaf  77% Soothing Toner, 250ml', 'product_price': 'KSh3,200', 'source': 'Beautysquareke', 'link': 'https://www.beautysquareke.com/product/anua-heartleaf--77%-soothing-toner,-250ml/'},
#     {'image_link': 'https://www.beautysquareke.com/beautykcot/uploads/2023/10/Anua-TONER.webp', 'product_name': 'Anua Heartleaf  77% Soothing Toner, 250ml', 'product_price': 'KSh3,200', 'source': 'Beautysquareke', 'link': 'https://www.beautysquareke.com/product/anua-heartleaf--77%-soothing-toner,-250ml/'}
# ]

async def extract_price(price_string):
    # Use regular expression to find the first numeric part of the string
    match = re.search(r'\b\d+(,\d{3})*\b', price_string)
    
    if match:
        # Extracted first numeric part from the matched group
        numeric_part = match.group()
        
        # Remove commas and convert to an integer
        numeric_value = int(numeric_part.replace(',', ''))
        
        return numeric_value
    else:
        # Return None if no match is found
        return None

async def beauty_square(name):
    try:
        URL = f"https://www.beautysquareke.com/?s={name}&post_type=product&product_cat="
        # r = requests.get(URL) 
        async with aiohttp.ClientSession() as session:
            async with session.get(URL) as response:
                soup = BeautifulSoup(await response.text(), 'html5lib')
        
        product_divs = soup.find_all('div', class_='product-block')
        products_list = []
        # Iterate through each product div
        for product_div in product_divs:
            # Check for the presence of "Out Of Stock" label
            stock_label = product_div.find('span', class_='stock-label')
            if stock_label and stock_label.text.strip().lower() == 'out of stock':
                # Skip the product if it's out of stock
                continue

            # Extract image link
            image_tag = product_div.find('img')
            image_link = image_tag['src'] if image_tag else None

                # Extract product name
            product_name_tag = product_div.find('h3').find('a') if product_div.find('h3') else None
            product_name = product_name_tag.text.strip() if product_name_tag else None

                # Extract product price
            price_div = product_div.find('div', class_='price-title')
            price_span = price_div.find('span', class_='woocommerce-Price-amount')
            product_price = price_span.bdi.get_text(strip=True) if price_span else "Price not available"
            product_link = product_name_tag['href'] if product_name_tag and 'href' in product_name_tag.attrs else None

                # Create a dictionary with extracted information
            product_info = {
                'image_link': image_link,
                'product_name': product_name,
                'product_price': product_price,
                'source': 'Beauty Square',
                'link': product_link,
                'price': await extract_price(product_price)
            }

                # Append the dictionary to the products list
            products_list.append(product_info)
        return products_list
    except Exception as e:
        print(f"Error in beauty_square: {e}")
        return []

async def dream_skin_haven(name):
    try:
        URL = f"https://dreamskinhaven.co.ke/?s={name}&post_type=product"
        # r = requests.get(URL) 
        async with aiohttp.ClientSession() as session:
            async with session.get(URL) as response:
                soup = BeautifulSoup(await response.text(), 'html5lib')
               
        product_ul_list = soup.find_all('ul', class_='products elementor-grid columns-4')

        if product_ul_list:
            # Access the first element of the list
            product_ul = product_ul_list[0]

            # Find all li tags within the product_ul
            li_tags = product_ul.find_all('li', class_='product')
            products_list = []

            for li_tag in li_tags:
                # Extracting image URL
                image_url = li_tag.find('img')['data-src']

                # Extracting href link
                href_link = li_tag.find('a', class_='woocommerce-LoopProduct-link')['href']

                # Extracting name
                name = li_tag.find('h2', class_='woocommerce-loop-product__title').text.strip()

                # Extracting price
                price = li_tag.find('span', class_='price').text.strip()
                product_info = {
                'image_link': image_url,
                'product_name': name,
                'product_price': price,
                'source': 'Dream Skin Haven',
                'link': href_link,
                'price': await extract_price(price)
                }
                products_list.append(product_info)
            return products_list
    except Exception as e:
        print(f"Error in dream_skin_haven: {e}")
        return []

async def joinherglow(name):
    try:
        URL = f"https://joinherglow.com/?s={name}&post_type=product&product"
        # r = requests.get(URL) 
        async with aiohttp.ClientSession() as session:
            async with session.get(URL) as response:
                soup = BeautifulSoup(await response.text(), 'html5lib')
        
        product_divs = soup.find_all('div', class_='product-wrapper')
        products_list = []
        # Iterate through each product div
        for product_div in product_divs:
            # Check for the presence of "Out Of Stock" label
            stock_label = product_div.find('span', class_='out-of-stock product-label')
            if stock_label and stock_label.text.strip().lower() == 'sold out':
                # Skip the product if it's out of stock
                continue

            # Extract image link
            image_tag = product_div.find('a').find('img')
            image_link = image_tag['src'] if image_tag else None

                # Extract product name
            product_link_tag = product_div.find('a', class_='product-image-link')   
            product_name = product_div.find('h3', class_='wd-entities-title').text.strip()
            
               
                # Extract product price
            price_div = product_div.find('div', class_='wrapp-product-price')
            price_span = price_div.find('span', class_='woocommerce-Price-amount amount')
            product_price = price_span.bdi.get_text(strip=True) if price_span else "Price not available"
            product_link = product_link_tag['href'] if product_link_tag else None


                # Create a dictionary with extracted information
            product_info = {
                'image_link': image_link,
                'product_name': product_name,
                'product_price': product_price,
                'source': 'Joinherglow',
                'link': product_link,
                'price': await extract_price(product_price)
            }

                # Append the dictionary to the products list
            products_list.append(product_info)
        return products_list
    except Exception as e:
        print(f"Error in joinherglow: {e}")
        return []

async def agnes(name):
    try:
        URL = f"https://agnespureandregal.com/search?q={name}"
        async with aiohttp.ClientSession() as session:
            async with session.get(URL) as response:
                soup = BeautifulSoup(await response.text(), 'html5lib')
        products_list = []
        grid_divs = soup.find_all('div', class_='grid')
        for div in grid_divs:
            grid_item = div.find('div', class_='grid__item one-fifth')
            
            if grid_item:
                info_div = div.find('div', class_='grid__item four-fifths')
                if info_div.find('span', itemprop='price'):
                    product_link = grid_item.find('a')['href']
                    product_name = grid_item.find('img')['alt']
                    image_link = grid_item.find('img')['data-src'].replace('{width}', "250")
                    product_price = info_div.find('span', itemprop='price').find('span', class_='money').text.strip()
                    product_info = {
                        'image_link': f"https://{image_link.lstrip('//')}",
                        'product_name': product_name,
                        'product_price': product_price,
                        'source': 'Agnes',
                        'link': f"https://agnespureandregal.com/{product_link}",
                        'price': await extract_price(product_price)
                    }
                    products_list.append(product_info)
        return products_list
    except BaseException as e:
        print(f"Error in agnes: {e}")
        return []

'''
async def agnes(name):
    try:
        URL = f"https://agnespureandregal.com/search?q={name}"
        # r = requests.get(URL)
        async with aiohttp.ClientSession() as session:
            async with session.get(URL) as response:
                soup = BeautifulSoup(await response.text(), 'html5lib')
        
        product_divs = soup.find_all('div', class_='grid__item four-fifths')
        products_list = []
        # Iterate through each product div
        for product_div in product_divs:

           # Extract image link
            image_link = product_div.find_previous('div', class_='grid__item one-fifth').find('img')['src']

            # Extract product name
            product_name = product_div.find('h2', class_='h3').text.strip()

            # Extract product price
            product_price = product_div.find('span', class_='money conversion-bear-money').text.strip()

            # Extract product link
            product_link = product_div.find_previous('div', class_='grid__item one-fifth').find('a')['href']

            # Create a dictionary with extracted information
            product_info = {
                'image_link': image_link,
                'product_name': product_name,
                'product_price': product_price,
                'source': 'Agnes Pure and Regal',
                'link': product_link,
                'price': await extract_price(product_price)  
            }
              #Append the dictionary to the products list
            products_list.append(product_info)
        return products_list
    except Exception as e:
        print(f"Error in agnes: {e}")
        return []
'''
def home(request):
    return render(request, 'Home.html')

async def search(request):
    context = {}
    if request.method == 'POST':
        name = request.POST.get('name')

        async with aiohttp.ClientSession() as session:
            # Use asyncio.gather to concurrently fetch data from multiple sources
            tasks = [
                joinherglow(name),
                beauty_square(name),
                agnes(name),
                dream_skin_haven(name),
               
            ]

            # Ensure the tasks are scheduled as coroutines
            tasks = [asyncio.ensure_future(task) for task in tasks]

            results = await asyncio.gather(*tasks)

            # Combine the results into a single list
            products_list = []
            for result in results:
                if result:
                    products_list.extend(result)

            context = {"products": products_list}

    return JsonResponse(context)


def contact(request):
    if request.method == 'POST':
        subject = "Question or Feedback" 
        body = {
		'name': request.POST.get('name'), 
		'email': request.POST.get('email'), 
		'message':request.POST.get('message'),
		}
        message = "\n".join(body.values())
        try:
            from_email = settings.EMAIL_HOST_USER 
            send_mail(subject, message, from_email, ['ndungulilianwanjiku@gmail.com'], fail_silently=True)
        except BaseException:
            return JsonResponse({"status": "false"})
        return JsonResponse({"status": "true"})
    return render(request, 'App/Home.html')