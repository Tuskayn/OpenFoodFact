import pymysql
import requests
from Classy import *

from Create import exec_sql_file

API_URL = 'https://fr.openfoodfacts.org/'
categories = list()
products = list()
new = 0
try:
    cnx = pymysql.connect(user='root',
                          password='root',
                          host='localhost',
                          charset='utf8mb4',
                          db='openfoodfacts')
except pymysql.InternalError:
    print("No database detected, creating database...")
    cnx = pymysql.connect(user='root',
                          password='root',
                          host='localhost',
                          charset='utf8mb4')
    cur = cnx.cursor()
    exec_sql_file(cur, 'openfoodfacts_create.sql')
    new = 1


def fetch(path):
    """Get dynamically data from the REST API of OpenFoodFacts"""
    path = "%s%s.json" % (API_URL, path)
    response = requests.get(path)
    return response.json()


def get_categories_from_db():
    """Get all categories from the DB"""
    cursor = cnx.cursor(pymysql.cursors.DictCursor)
    cursor.execute('SELECT id, prod_cat, name, url FROM categories')
    result = cursor.fetchall()
    cursor.close()
    categories = list()
    for element in result:
        categories.append(Categorie(element['id'], element['prod_cat'], element['name'], element['url']))
    return categories


def update():
    """DROP old data and get fresh new one"""
    global categories
    categories = fetch("categories")
    cursor = cnx.cursor()
    cursor.execute('TRUNCATE categories')
    cursor.execute('TRUNCATE Products')
    # clear result from useless data
    cleared_categories = list()
    for element in categories['tags']:
        if element['products'] < 50:
            continue
        if element['id'][:3] not in ['en:', 'fr:']:
            continue
        cleared_categories.append(element)
    for element in cleared_categories:
        cursor.execute('INSERT INTO Categories(prod_cat, name, url) VALUES (%s, %s, %s)',
                       (element['id'], element['name'], element['url']))
    cnx.commit()
    cursor.close()
    print("Catégories à jour, mise à jour des produits...")
    get_products_from_france()
    print("Données à jour.")


def get_products_from_france():
    global products
    page = 170
    result = requests.get(
        "https://fr.openfoodfacts.org/cgi/search.pl?page_size=1000&page={}&action=process&json=1".format(page)).json()
    while page < 180:
        for element in result['products']:
            # Check for data matching
            if not all(tag in element for tag in ("product_name", "brands", "id", "nutrition_grade_fr", "url",
                                                  "categories_prev_tags")):
                continue
            if not all(tag in element['nutriments'] for tag in ("fat_100g", "saturated-fat_100g",
                                                                "sugars_100g", "salt_100g")):
                continue
            if not element['categories_prev_tags']:
                continue
            products.append(Product(element['id'], element['product_name'], element['brands'],
                                    element['nutrition_grade_fr'], element['nutriments']['fat_100g'],
                                    element['nutriments']['saturated-fat_100g'], element['nutriments']['sugars_100g'],
                                    element['nutriments']['salt_100g'], element['url'],
                                    element['categories_prev_tags'][-1]))
        page += 1
        result = requests.get(
            "https://fr.openfoodfacts.org/cgi/search.pl?page_size=1000&page={}&action=process&json=1".format(
                page)).json()
        print(len(products), " produits...")
        print("Etape : ", page, "/180")
    for i in range(len(products)):
        save_product(products[i])


def categories_browser():
    global categories
    page_min = 0
    page_max = 10
    while "user won't quit":
        categories = get_categories_from_db()
        print("Il y a {} catégories.".format(len(categories)))
        print("Sélectionnez une catégorie:")

        # Test overflow
        if len(categories)-page_max < 10 < page_max:
            page_max += len(categories)-page_max
            if page_max < 10:
                page_min = 0
            else:
                page_min = page_max-10
        if page_min < 0:
            page_min = 0
            page_max = 10

        for i in range(page_min, page_max):
            print("{} - {}".format(categories[i].id, categories[i].name))

        uinput = input("Entrez: Numéro - selectionner la catégorie "
                       "| > page suivante | < page précédente "
                       "| 0 - revenir au menu principal\n")

        if uinput == '0':
            break
        if uinput == '>':
            page_max += 10
            page_min += 10
        if uinput == '<' and page_min > 0:
            page_max -= 10
            page_min -= 10

        if uinput.isdigit():
            category_product_browser(int(uinput)-1, categories[int(uinput)-1].prod_cat)
            continue


def category_product_browser(id, category_id):
    global categories
    category_page = 1
    category_products = create_products_list_from_category(category_id)
    while "user won't quit":
        print("Affichage des produits de la catégorie {} | Page : {}".format(categories[id].name, category_page))
        for i in range(min(20, len(category_products))):
            print("{} - {} {}".format(i+1, category_products[i].name, category_products[i].brands))

        uinput = input("Entrez: Numéro - selectionner un produit "
                       "| > page suivante | < page précédente "
                       "| 0 - revenir aux catégories\n")

        if uinput == '0':
            break
        if uinput == '>':
            category_page += 1
        if uinput == '<' and category_page > 1:
            category_page -= 1
        if uinput.isdigit():
            product_browser(category_products[int(uinput) - 1], categories[category_id].name)
            continue


def create_products_list_from_category(category_id):
    global categories
    global products
    products = get_products_from_db()
    category_products = list()
    for element in products:
        if element.category != category_id:
            continue
        category_products.append(Product(element['id'], element['product_name'], element['brands'],
                                         element['nutrition_grade_fr'], element['nutriments']['fat_100g'],
                                         element['nutriments']['saturated-fat_100g'],
                                         element['nutriments']['sugars_100g'], element['nutriments']['salt_100g'],
                                         element['url'], element['categories_prev_tags'][-1]))
    return category_products


def product_browser(product, category_name):
    while "user won't quit":
        # Display selected product
        print("\t<__/ Fiche du Produit \__>\n")
        print("Nom du produit : " + product.name)
        print("Marques : " + product.brands)
        print("Nutri-score : " + product.nutrition_grade.upper())
        print("Repères nutritionnels pour 100g :")
        print("\tLipides : " + str(product.fat))
        print("\tAcides gras saturés : " + str(product.saturated_fat))
        print("\tSucres : " + str(product.sugars))
        print("\tSel : " + str(product.salt))
        print("URL : " + product.url)

        uinput = input("(Entrez: S - Substituer | E - Enregistrer |"
                       " 0 - Revenir aux produits de {})\n".format(category_name))

        if uinput is '0':
            break

        if uinput.lower() == 's':
            substitutes_browser(product)

        if uinput.lower() == 'e':
            save_product(product)
            continue


def substitutes_browser(product):
    substitutes = get_substitutes(product)
    page_min = 0
    page_max = 10
    while "user won't quit":

        # Test overflow
        if len(substitutes)-page_max < 10 < page_max:
            page_max += len(substitutes)-page_max
            if page_max < 10:
                page_min = 0
            else:
                page_min = page_max-10
        if page_min < 0:
            page_min = 0
            page_max = 10

        print("Liste des {} substitution pour le produit \"{}\" : \n".format(len(substitutes), product.name))
        if len(substitutes) == 0:
            print("Vous utilisez déjà un produit sain selon OpenFoodFacts.\nRetour à la fiche produit.\n")
            break
        else:
            for i in range(page_min, page_max):
                print("{} - {} {}".format(i + 1, substitutes[i].name, substitutes[i].brands))

        uinput = input("Entrez: Numéro - selectionner un produit | > - page suivante |"
                       " < - page précedente | 0 - revenir au produit\n")

        if uinput is '0':
            break
        if uinput.isdigit():
            product_browser(substitutes[int(uinput)-1], "substitution de {}".format(product.name))
            continue
        if uinput == '>':
            page_min += 10
            page_max += 10
        if uinput == '<' and page_min > 0:
            page_min -= 10
            page_max -= 10


def get_substitutes(product):
    """Get a list of healthier products from the selected one"""
    url = "cgi/search.pl?tagtype_0=categories&tag_contains_0=contains&tag_0={}" \
          "&page_size=500&page=1&action=process&json=1"
    result = fetch(url.format(product.category))
    products = list()
    for element in result['products']:
        # Check for data matching
        if not all(k in element for k in ("product_name", "brands", "id", "nutrition_grade_fr", "url",
                                          "categories_prev_tags")):
            continue
        if not all(k in element['nutriments'] for k in ("fat_100g", "saturated-fat_100g", "sugars_100g", "salt_100g")):
            continue

        # Nutri test
        if element["nutrition_grade_fr"] >= product.nutrition_grade:
            continue

        products.append(Product(element['id'], element['product_name'], element['brands'],
                                element['nutrition_grade_fr'], element['nutriments']['fat_100g'],
                                element['nutriments']['saturated-fat_100g'], element['nutriments']['sugars_100g'],
                                element['nutriments']['salt_100g'], element['url'],
                                element['categories_prev_tags'][-1]))
    return products


def save_product(product):
    """Save the selected product in the DB"""
    cursor = cnx.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM Products")
    result = cursor.fetchall()
    exist = 0
    print(product.url)
    for element in result:
        # Test if the product already exist in the DB
        if element['url'] == product.url:
            exist = 1
    if exist == 1:
        print("Produit déjà enregistré.")
    else:
        try:
            cursor.execute(
                'INSERT INTO Products(name, brands, url, nutrition_grade, fat, saturated_fat, sugars, salt, category)\
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)', (product.name, product.brands, product.url,
                                                               product.nutrition_grade, product.fat,
                                                               product.saturated_fat, product.sugars, product.salt,
                                                               product.category))
            print("Produit sauvegardé.")
        except Exception as e:
            print("[Erreur] ", e)
    cursor.close()
    cnx.commit()


def get_products_from_db():
    """Get a list of products from the database"""
    cursor = cnx.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM Products")
    result = cursor.fetchall()
    cursor.close()
    products = list()
    for element in result:
        products.append(Product(element['id'], element['name'], element['brands'], element['nutrition_grade'],
                                element['fat'], element['saturated_fat'], element['sugars'],
                                element['salt'], element['url'], element['category']))
    return products


def product_browser_from_db():
    """Display the user's saved product from the DB"""
    products = get_products_from_db()
    while "User won't exit":
        print("<__/ Liste des produits enregistrés \__>")
        for i in range(min(10, len(products))):
            print("{} - {} {}".format(i+1, products[i].name, products[i].brands))
        uinput = input("(Entrez: Numéro - selectionner un produit | S - page suivante |"
                       " P - page précedente | 0 - revenir au menu principal)\n")

        # Exit substitute manager
        if uinput is '0':
            break

        # Select product
        if uinput.isdigit():
            product_browser(products[int(uinput)-1], "vote liste")
            continue


def user_menu():
    global new
    if new == 1:
        print("Nouvelle base de données, mise à jour des données...\n(Cela va prendre du temps...)")
        update()

    while "user won't quit":
        print("\n\t<__/ Menu Principal \__>")
        print("1 : Trouver un produit par catégorie")
        print("2 : Afficher mes produits enregistré")
        print("3 : Mettre à jour les catégories")
        uinput = input("Entrez: Un numéro pour choisir un menu | 0 pour quitter\n")

        if uinput == '1':
            categories_browser()
            continue
        if uinput == '2':
            product_browser_from_db()
            continue
        if uinput == '3':
            print("Mise à jour des données...\n(Cela va prendre du temps...)")
            update()
            continue
        if uinput == '0':
            break

user_menu()
print("\t  <__/ Aurevoir \__>")
