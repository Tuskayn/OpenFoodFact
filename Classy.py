class Categorie:
    """OpenFoodFacts Categorie"""
    def __init__(self, id, name, url):
        self.id = id
        self.name = name
        self.url = url


class Product:
    """OpenFoodFacts Product"""
    def __init__(self, id, name, brands, nutrition_grade, fat, saturated_fat, sugars, salt, url, category):
        self.id = id
        self.name = name
        self.brands = brands
        self.nutrition_grade = nutrition_grade
        self.fat = fat
        self.saturated_fat = saturated_fat
        self.sugars = sugars
        self.salt = salt
        self.url = url
        self.category = category
