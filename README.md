# OpenFoodFacts
Project 5 OpenClassroom.

https://github.com/Tuskayn/OpenFoodFacts
https://trello.com/b/MUJujbBI/openfoodfacts
## Instructions

### Setup
```
Install python
Install mysql
Launch Main.py
```

### How to use
```
The first launch will download automatically the data from OpenFoodFacts and stock it.
From main menu you have 3 choice:
    - 1 : Search products from categories.
    - 2 : Search your saved products.
    - 3 : Update the OpenFoodfacts's data (This can take some times)
When a product is selected you can save/delete to your personnal database, search for a healthier product in the same 
category.
```

## Informations

### Create.py
This file is used by the Main.py to create the database from the SQL script openfoodfacts_create.sql
```
exec_sql_file() : Create database and tables from openfoodfacts_create.sql.
```

### openfoodfacts_create.sql
This is the SQL script used by Create.py to create the database.

### Classy.py
This file contain the used python class objects for Main.py
```
class Categorie
class Product
```

### Main.py
```
- fetch() : get data from an url in a json format.
- get_categories_from_db() : Get a list of all the stocked categories in the DB.
- update() : Main function to update categories and products.
- get_products_from_france() : Get all the products from france with some data check.
- categories_browser() : Called by the option 1 of user_menu(), used to navigate within the categories.
- category_product_browser() : Called by the user when he select a category, used to navigate in a category.
- create_products_list_from_category() : create a list of products for the given category and return it.
- product_browser() : the menu for a product, it's display product's informations and let the user decide the next step.
- substitutes_browser() : Display the list of products given by get_substitutes() and let the user decide the next step.
- get_substitutes() : Compare the selected product with others in the same category and pick only those with a better
    nutriscore (A, B, C, D, E) to create a list for substitutes_browser().
- save_products(): Used for the first lunch or the update() to commit all the product in the DB.
- drop_user_product() : Delete a product from his choice of the table User_Product.
- save_user_product() : Save a specified product in the table User_Product.
- get_products_from_db() : Get all the product from the table Products. (Take some times)
- get_products_from_user_db() : Get all the product from the table User_Product.
- product_browser_from_db() : Navigate in the user's saved products.
- user_menu() : Main menu.

```