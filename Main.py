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
    db_categories = list()
    for element in result:
        db_categories.append(Categorie(element['id'], element['prod_cat'], element['name'], element['url']))
    return db_categories


def update():
    """DROP old data and get fresh new one"""
    global categories
    global products
    cursor = cnx.cursor()
    cursor.execute('TRUNCATE categories')
    cursor.execute('TRUNCATE Products')

    print("Mise à jour des produits...")
    get_products_from_france()
    products = get_products_from_db()

    print("Produits à jour, mise à jour des catégories...")
    categories = fetch("categories")
    cleared_categories = list()
    for element in categories['tags']:
        if element['products'] < 50:
            continue
        if element['id'][:3] not in ['en:', 'fr:']:
            continue
        emptytest = create_products_list_from_category(element['id'])
        if len(emptytest) < 1:
            continue
        cleared_categories.append(element)

    for element in cleared_categories:
        cursor.execute('INSERT INTO Categories(prod_cat, name, url) VALUES (%s, %s, %s)',
                       (element['id'], element['name'], element['url']))
    cnx.commit()
    cursor.close()
    categories = get_categories_from_db()
    print("Données à jour.")


def get_products_from_france():
    global products
    page = 1
    result = requests.get(
        "https://fr.openfoodfacts.org/cgi/search.pl?page_size=1000&page={}&action=process&json=1".format(page)).json()
    pagemax = int((result["count"]/1000)+1)
    while page < pagemax:
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
        print("Etape : ", page, "/", pagemax)
    save_products()


def categories_browser():
    global categories
    global products
    page_min = 0
    page_max = 10
    while "user won't quit":
        print("Il y a {} catégories.".format(len(categories)))
        print("Sélectionnez une catégorie:")

        # Test overflow
        if len(categories)-page_max < 10 <= page_max:
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


def category_product_browser(cid, category_id):
    global categories
    global products
    category_products = create_products_list_from_category(category_id)
    page_min = 0
    page_max = 10
    while "user won't quit":
        # Test overflow
        if len(category_products)-page_max < 10 <= page_max:
            page_max += len(category_products)-page_max
            if page_max < 10:
                page_min = 0
            else:
                page_min = page_max-10
        if page_min < 0:
            page_min = 0
            page_max = 10

        print("Affichage des produits de la catégorie {} | Page : {}".format(categories[cid].name, int(page_max/10)))
        for i in range(page_min, page_max):
            print("{} - {} {}".format(i+1, category_products[i].name, category_products[i].brands))

        uinput = input("Entrez: Numéro - selectionner un produit "
                       "| > page suivante | < page précédente "
                       "| 0 - revenir aux catégories\n")

        if uinput == '0':
            break
        if uinput == '>':
            page_max += 10
            page_min += 10
        if uinput == '<' and page_min > 0:
            page_max -= 10
            page_min -= 10
        if uinput.isdigit():
            if 0 < int(uinput) <= len(category_products):
                product_browser(category_products[int(uinput)-1], categories[cid].name)


def create_products_list_from_category(category_id):
    global products
    category_products = list()
    for element in products:
        if element.category != category_id:
            continue
        category_products.append(element)
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

        uinput = input("(Entrez: R - Recherche d'un produit plus sain | E - Enregistrer | S - Supprimer le produit "
                       "de votre liste | 0 - Revenir aux produits de {})\n".format(category_name))

        if uinput is '0':
            break

        if uinput.lower() == 's':
            drop_user_product(product)

        if uinput.lower() == 'r':
            substitutes_browser(product)

        if uinput.lower() == 'e':
            save_user_product(product)


def substitutes_browser(product):
    substitutes = get_substitutes(product)
    page_min = 0
    page_max = 10
    while "user won't quit":

        # Test overflow
        if len(substitutes)-page_max < 10 <= page_max:
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
    result = create_products_list_from_category(product.category)
    s_products = list()
    for element in result:
        # Nutri test
        if element.nutrition_grade >= product.nutrition_grade:
            continue

        s_products.append(element)
    return s_products


def save_products():
    """Save all the products in the DB"""
    global products
    cursor = cnx.cursor(pymysql.cursors.DictCursor)
    for elt in products:
        try:
            cursor.execute(
                'INSERT INTO Products(name, brands, url, nutrition_grade, fat, saturated_fat, sugars, salt,'
                'category) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)', (elt.name, elt.brands, elt.url,
                                                                          elt.nutrition_grade, elt.fat,
                                                                          elt.saturated_fat, elt.sugars, elt.salt,
                                                                          elt.category))
        except Exception:
            pass
    cursor.close()
    cnx.commit()


def drop_user_product(product):
    cursor = cnx.cursor(pymysql.cursors.DictCursor)
    sql = "DELETE FROM User_Products WHERE url = '%s' "
    cursor.execute(sql % product.url)
    cursor.close()
    cnx.commit()
    print("Produit supprimé de votre liste.")


def save_user_product(product):
    """Save the selected product in the DB"""
    cursor = cnx.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM User_Products")
    result = cursor.fetchall()
    exist = 0
    for element in result:
        # Test if the product already exist in the user's list
        if element['url'] == product.url:
            exist = 1
    if exist == 1:
        print("Produit déjà enregistré.")
    else:
        try:
            cursor.execute(
                'INSERT INTO User_Products(name, brands, url, nutrition_grade, fat, saturated_fat, sugars, salt, '
                'category) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)', (product.name, product.brands, product.url,
                                                                          product.nutrition_grade, product.fat,
                                                                          product.saturated_fat, product.sugars,
                                                                          product.salt, product.category))
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
    db_products = list()
    for element in result:
        db_products.append(Product(element['id'], element['name'], element['brands'], element['nutrition_grade'],
                                   element['fat'], element['saturated_fat'], element['sugars'], element['salt'],
                                   element['url'], element['category']))
    return db_products


def get_products_from_user_db():
    cursor = cnx.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM User_Products")
    result = cursor.fetchall()
    cursor.close()
    db_u_products = list()
    for element in result:
        db_u_products.append(Product(element['id'], element['name'], element['brands'], element['nutrition_grade'],
                                     element['fat'], element['saturated_fat'], element['sugars'], element['salt'],
                                     element['url'], element['category']))
    return db_u_products


def product_browser_from_db():
    """Display the user's saved product from the DB"""
    page_min = 0
    page_max = 10
    while "User won't exit":
        u_products = get_products_from_user_db()
        # Test overflow
        if len(u_products) - page_max < 10 <= page_max:
            page_max = len(u_products)
            if page_max < 10:
                page_min = 0
            else:
                page_min = page_max - 10
        if page_min < 0:
            page_min = 0
            page_max = 10
        if len(u_products) < 10:
            page_max = len(u_products)
            page_min = 0

        print("<__/ Liste des produits enregistrés \__>")
        for i in range(page_min, page_max):
            print("{} - {} {}".format(i+1, u_products[i].name, u_products[i].brands))
        uinput = input("(Entrez: Numéro - selectionner un produit | > - page suivante |"
                       " < - page précedente | 0 - revenir au menu principal)\n")

        # Exit substitute manager
        if uinput == '0':
            break

        if uinput == '>':
            page_max += 10
            page_min += 10

        if uinput == '<' and page_min > 0:
            page_max -= 10
            page_min -= 10

        # Select product
        if uinput.isdigit():
            if 0 < int(uinput) <= len(u_products):
                product_browser(u_products[int(uinput)-1], "votre liste")


def user_menu():
    global new
    global products
    global categories

    if new == 1:
        print("Nouvelle base de données, mise à jour des données...\n(Cela va prendre du temps...)")
        update()
    else:
        products = get_products_from_db()
        categories = get_categories_from_db()

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
            while "user won't quit":
                uinputu = input("Etes vous sûr ? (Cela va prendre du temps...) | 1 - Oui | 0 - Non\n")
                if uinputu == '1':
                    print("Mise à jour des données...\n(N'éteignez pas le programme.)")
                    update()
                if uinputu == '0':
                    break
        if uinput == '0':
            break

user_menu()
print("\t  <__/ Aurevoir \__>")
