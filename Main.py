import pymysql
import requests
from Classy import *

from Create import exec_sql_file

API_URL = 'https://fr.openfoodfacts.org/'
categories = list()
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


def get_categories():
    """Get all categories from the DB"""
    cursor = cnx.cursor(pymysql.cursors.DictCursor)
    cursor.execute('SELECT id, name, url FROM categories')
    result = cursor.fetchall()
    cursor.close()
    categories = list()
    for element in result:
        categories.append(Categorie(element['id'], element['name'], element['url']))
    return categories


def update_categories():
    """DROP old categories, download new from API then stock into the DB"""
    categories = fetch("categories")
    cursor = cnx.cursor()
    cursor.execute('ALTER TABLE Product_categories DROP FOREIGN KEY Link_Categories')
    cursor.execute('TRUNCATE categories')
    cursor.execute('ALTER TABLE Product_categories ADD CONSTRAINT Link_Categories FOREIGN KEY Link_Categories (Categories_id) REFERENCES Categories (id);')
    # clear result from useless data
    cleared_categories = list()
    for element in categories['tags']:
        if element['products'] < 10:
            continue
        if element['id'][:3] in ['en:', 'ru:', 'de:', 'es:']:
            continue
        cleared_categories.append(element)
    for element in cleared_categories:
        cursor.execute("INSERT INTO categories(name, url) VALUES (%s, %s)",
                       (element['name'], element['url']))
    cursor.close()
    cnx.commit()
    print("Catégories mises à jour.")


def categories_browser():
    global categories
    page_min = 0
    page_max = 10
    while "user won't quit":
        categories = get_categories()
        print("Il y a {} catégories.".format(len(categories)))
        print("Sélectionnez une catégorie:")
        if len(categories)-page_max < 10:
            page_max = len(categories)
            page_min = page_max-10
        for i in range(page_min, page_max):
            print("{} - {}".format(categories[i].id, categories[i].name))

        uinput = input("Entrez: Numéro - selectionner la catégorie "
                       "| > page suivante | < page précédente "
                       "| 0 - revenir au menu principal\n")

        if uinput == '0':
            break
        if uinput == '>' and page_max < len(categories):
            page_max += 10
            page_min += 10
        if uinput == '<' and page_min > 0:
            page_max -= 10
            page_min -= 10

        if uinput.isdigit():
            # appel de fonction qui ouvre la catégorie ciblé
            continue


def user_menu():
    global new
    if new == 1:
        print("Nouvelle database, mise à jour des catégories...")
        update_categories()

    while "user won't quit":
        print("\n\t<__/ Menu Principal \__>")
        print("1 : Trouver un produit par catégorie")
        print("2 : Afficher mes produits substitué")
        print("3 : Mettre à jour les catégories")
        uinput = input("Entrez: Un numéro pour choisir un menu | 0 pour quitter\n")

        if uinput == '1':
            categories_browser()
            continue
        if uinput == '2':
            continue
        if uinput == '3':
            print("Mise à jour des catégories en cours...")
            update_categories()
            continue
        if uinput == '0':
            break

user_menu()
print("\n\t  <__/ Aurevoir \__>")
