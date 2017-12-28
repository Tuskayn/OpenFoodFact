CREATE DATABASE openfoodfacts;
USE openfoodfacts;


-- tables
-- Table: Categories
CREATE TABLE Categories (
    id int NOT NULL AUTO_INCREMENT,
    name varchar(100) NULL,
    url varchar(200) NULL,
    CONSTRAINT id PRIMARY KEY (id)
);

-- Table: Historic
CREATE TABLE Historic (
    id int NOT NULL AUTO_INCREMENT,
    Products_id int NOT NULL,
    CONSTRAINT Historic_pk PRIMARY KEY (id)
);

-- Table: Product_categories
CREATE TABLE Product_categories (
    id int NOT NULL AUTO_INCREMENT,
    Categories_id int NOT NULL,
    Products_id int NOT NULL,
    CONSTRAINT Product_categories_pk PRIMARY KEY (id)
);

-- Table: Products
CREATE TABLE Products (
    id int NOT NULL AUTO_INCREMENT,
    name varchar(100) NULL,
    brands varchar(100) NULL,
    url varchar(200) NULL,
    nutrition_grade char(1) NULL,
    fat float NULL,
    satured_fat float NULL,
    sugars float NULL,
    salt float NULL,
    CONSTRAINT id PRIMARY KEY (id)
);

-- foreign keys
-- Reference: Historic_Products (table: Historic)
ALTER TABLE Historic ADD CONSTRAINT Historic_Products FOREIGN KEY Historic_Products (Products_id)
    REFERENCES Products (id);

-- Reference: Link_Categories (table: Product_categories)
ALTER TABLE Product_categories ADD CONSTRAINT Link_Categories FOREIGN KEY Link_Categories (Categories_id)
    REFERENCES Categories (id);

-- Reference: Link_Products (table: Product_categories)
ALTER TABLE Product_categories ADD CONSTRAINT Link_Products FOREIGN KEY Link_Products (Products_id)
    REFERENCES Products (id);

-- End of file.

