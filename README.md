# Recipe Web Scraper

This Python project is a web scraper that extracts recipes from [ketodietapp.com](https://ketodietapp.com/Blog) and saves the extracted data in JSON format.

The project uses Selenium for web scraping and BeautifulSoup for parsing the HTML content. The extracted information includes the recipe title, overview, photos, serving unit, serving yield, nutritional information, ingredients, steps, food allergies, categories, allergy rules, and tags.

## Dependencies

- selenium
- webdriver-manager
- beautifulsoup4

## Installation

### Option 1: Using pip

Install the required packages using `pip`:
```bash
pip install selenium webdriver-manager beautifulsoup4
```

### Option 2: Using pipenv

Install `pipenv` if you haven't already
```bash
pip install pipenv
```

Navigate to the project directory and install the required packages using pipenv:
```bash
pipenv install
```

This will install the dependencies listed in the Pipfile.

## Usage

Add the list of recipe URLs to a text file named recipes_links.txt inside the resources folder.

### Option 1: Using pip

Run the Python script:
```bash
python recipe_scraper.py
```

### Option 2: Using pipenv
Activate the pipenv virtual environment:
```bash
pipenv shell
```

Run the Python script:
```bash
python recipe_scraper.py
```

Deactivate the pipenv virtual environment when you're done:
```bash
exit
```

For both options, the extracted data will be saved as JSON files in the output folder. Once all the recipes have been scraped, the output files will be compressed into a zip file named recipes.zip.