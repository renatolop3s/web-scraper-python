from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse
import json
import os
import shutil

def setup_selenium():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    return webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

def get_page_source(driver, url):
    print(f'Getting page source from {url}')
    driver.get(url)
    page_source = driver.page_source
    return page_source

def teardown_selenium(driver):
    print('Quitting webdriver')
    driver.quit()

def extract_recipe_title(soup):
    recipe_title = soup.find('h1', {'itemprop': 'name'})
    return recipe_title.get_text(strip=True) if recipe_title is not None else None

def extract_serving_unit(soup):
    serving_unit = soup.find('div', {'class': 'kdServingSize'})
    return serving_unit.strong.get_text() if serving_unit is not None else None

def extract_recipe_overview(soup):
    recipe_overview = soup.find('meta', {'itemprop': 'description'})
    return recipe_overview['content'] if recipe_overview is not None else None

def extract_recipe_photos(soup):
    recipe_photos = soup.find('a', {'class': 'kdPopupButton'})
    return urlparse(recipe_photos.img['src']).path if recipe_photos is not None else None

def extract_recipe_yield(soup):
    ingredients_h2 = soup.find('h2', {'id': 'ingredients'})
    recipe_yield = None
    if ingredients_h2 is not None:
        recipe_yield = re.search(r'\((.*?)\)', ingredients_h2.get_text(strip=True)).group(1)
    return recipe_yield

def extract_float_value_from(list, attrs={}, string=None):
    if string is not None:
        value = list.find('span', string=string).find_next_sibling('span')
    else: 
        value = list.find('span', attrs)

    if value:
        return float(value.text.split()[0].replace(',', ''))
    else:
        return None

def extract_nutritional_information_per_serving(soup):
    nutritional_values = soup.find('div', {'itemprop': 'nutrition'})
    nutritional_information_per_serving = {
        'proteinG': extract_float_value_from(nutritional_values, attrs={'itemprop': 'proteinContent'}),
        'fatG': extract_float_value_from(nutritional_values, attrs={'itemprop': 'fatContent'}),
        'caloriesKcal': extract_float_value_from(nutritional_values, attrs={'itemprop': 'calories'}),
        'carbsG': extract_float_value_from(nutritional_values, string='Total carbs'),
        'fiberG': extract_float_value_from(nutritional_values, attrs={'itemprop': 'fiberContent'}),
        'sugarG': extract_float_value_from(nutritional_values, string='Sugars'),
        'saturatedFatG': extract_float_value_from(nutritional_values, attrs={'itemprop': 'saturatedFatContent'}),
        'sodiumMg': extract_float_value_from(nutritional_values, attrs={'itemprop': 'sodiumContent'}),
        'magnesiumMg': extract_float_value_from(nutritional_values, string='Magnesium'),
        'potassiumMg': extract_float_value_from(nutritional_values, string='Potassium'),
    }
    return nutritional_information_per_serving

def extract_ingredients(soup):
    ingredients = []
    ingredients_list = soup.find_all('li', {'itemprop': 'recipeIngredient'})
    for ingredient in ingredients_list:
        text = ingredient.get_text()
        group = None
        ingredients.append({'text': text, 'group': group})
    return ingredients

def extract_recipe_steps(soup):
    recipe_steps = []
    instructions_list = soup.find_all('li', {'itemprop': 'recipeInstructions'})
    for instruction in instructions_list:
        text = instruction.get_text(strip=True)
        photos = urlparse(instruction.img['src']).path if instruction.img is not None else None
        recipe_steps.append({'recipeStepText': text, 'recipeStepPhotos': photos})
    return recipe_steps

def extract_food_allergies(soup):
    food_allergies = []
    allergies_tag = soup.find_all('div', {'class': 'kdAllergyTag'})
    for tag in allergies_tag:
        text = tag.get_text(strip=True).replace('\u2714\u00a0\u00a0', '')
        text_pascal_case = ''.join(word.capitalize() for word in text.split())
        food_allergies.append(text_pascal_case)
    return food_allergies

def extract_food_categories(soup):
    food_categories = []
    return food_categories

def extract_food_allergies_rules(soup):
    food_allergies_rules = []
    return food_allergies_rules

def extract_tags(soup):
    tags = []
    article_tags = soup.find_all('meta', {'property': 'article:tag'})
    for tag in article_tags:
        tags.append(tag['content'])
    return tags

def parse_and_extract_data_from(page_source):
    print('Extracting data...')
    soup = BeautifulSoup(page_source, 'html.parser')

    print('Creating dictionary with extracted data')
    recipe_data = {
        'recipeTitle': extract_recipe_title(soup),
        'recipeOverview': extract_recipe_overview(soup),
        'recipePhotos': extract_recipe_photos(soup),
        'servingUnit': extract_serving_unit(soup),
        'recipeYield': extract_recipe_yield(soup),
        'nutritionalInformationPerServing': extract_nutritional_information_per_serving(soup),
        'ingredients': extract_ingredients(soup),
        'recipeSteps': extract_recipe_steps(soup),
        'foodAllergies': extract_food_allergies(soup),
        'foodCategories': extract_food_categories(soup),
        'foodAllergiesRules': extract_food_allergies_rules(soup),
        'tags': extract_tags(soup)
    }

    return recipe_data

def save_as_json(dict):
    print('Converting dictionary data into json')
    output_folder = 'output/'
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    filename = f"{output_folder}{dict['recipeTitle'].replace(' ', '-').replace(',', '').lower()}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(dict, f, indent=3)



if __name__ == '__main__':
    print('Starting web scraping')

    driver = setup_selenium()

    with open('resources/recipes_links.txt') as f:
        urls = f.read().splitlines()

    for url in urls:
        page_source = get_page_source(driver, url)
        recipe_data = parse_and_extract_data_from(page_source)
        save_as_json(recipe_data)

    teardown_selenium(driver)

    shutil.make_archive('recipes', 'zip', 'output')
