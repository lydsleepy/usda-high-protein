# defining function to fetch food data from USDA FoodData Central API
# query is the search term
#max_results is max num of food items to return, defaulted to 60
def fetch_category(query, max_results=60):
  all_foods = []
  page_size = 50 # max number of results returned in single request

  # dictionary of parameters that will be sent to the api
  params = {
      'api_key': api_key,
      'query': query,
      'pageSize': page_size,
      # which database to search
      # branded is commerical (like cheerios)
      # survey is generic (like "chicken breast, cooked")
      'dataType': ['Branded', 'Survey (FNDDS)']
  }

  print(f"Fetching {query} foods...")

  try:
    response = requests.get(base_url, params=params)
    response.raise_for_status()
    # takes text response from api and turns it into python dictionary
    data = response.json()

    # looks for key called 'foods' in data dictionary
    # if it finds it, returns the list / if not, returns empty list
    foods = data.get('foods', [])
    # adds items in foods to the all_foods list
    all_foods.extend(foods[:max_results])
    print(f"Retrieved {len(foods[:max_results])} items")
  except Exception as e:
    print(f"Error fetching {query}: {e}")
  # waits half a second before continuing to not overwhelm api
  time.sleep(0.5)
  return all_foods

# defining function that extracts nutritional info from food item
def extract_nutrients(food_item):
  nutrients_dict = {}

  nutrients_dict['fdc_id'] = food_item.get('fdcId', '')
  # food name / description
  nutrients_dict['description'] = food_item.get('description', '')
  # like Chobani for yogurt
  nutrients_dict['brand_owner'] = food_item.get('brandOwner', 'N/A')
  nutrients_dict['data_type'] = food_item.get('dataType', '')
  nutrients_dict['food_category'] = food_item.get('foodCategory', 'N/A')

  # api will return nutrients as a list of dictionaries
  nutrients = food_item.get('foodNutrients', [])

  # dictionary
  # left side is what the api calls the nutrient
  # right side is what we call it in our csv
  nutrient_map = {
      'Energy': 'calories',
      'Protein': 'protein_g',
      'Total lipid (fat)': 'fat_g',
      'Carbohydrate, by difference': 'carbs_g',
      'Sugars, total including NLEA': 'sugar_g',
      'Fiber, total dietary': 'fiber_g',
      'Sodium, Na': 'sodium_mg',
      'Cholesterol': 'cholesterol_mg',
      'Fatty acids, total saturated': 'saturated_fat_g'
  }

  # makes sure every food has those columns (in nutrient_map) even if the
  # api didnt provide the value for it
  for key in nutrient_map.values():
    nutrients_dict[key] = None

  # extracts name and number from each nutrient
  for nutrient in nutrients:
    nutrient_name = nutrient.get('nutrientName', '')
    nutrient_value = nutrient.get('value', None)

    for search_name, dict_key in nutrient_map.items():
      # converts both to lowercase to handle case-insensitive
      if search_name.lower() in nutrient_name.lower():
        # saves nutrient value using our naming convention
        nutrients_dict[dict_key] = nutrient_value
        break

  return nutrients_dict