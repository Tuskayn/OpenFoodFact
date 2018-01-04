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

-- Table: Products
CREATE TABLE Products (
    id int NOT NULL AUTO_INCREMENT,
    name varchar(100) NULL,
    brands varchar(100) NULL,
    url varchar(200) NULL,
    nutrition_grade char(1) NULL,
    fat float NULL,
    saturated_fat float NULL,
    sugars float NULL,
    salt float NULL,
    category VARCHAR(100),
    CONSTRAINT id PRIMARY KEY (id)
);

