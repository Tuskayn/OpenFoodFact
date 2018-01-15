CREATE DATABASE openfoodfacts;
USE openfoodfacts;


-- tables
-- Table: Categories
CREATE TABLE Categories (
    id int NOT NULL AUTO_INCREMENT,
    prod_cat VARCHAR(500) NULL,
    name varchar(500) NULL,
    url varchar(500) NULL,
    CONSTRAINT id PRIMARY KEY (id)
);

-- Table: Products
CREATE TABLE Products (
    id int NOT NULL AUTO_INCREMENT,
    name varchar(500) NULL,
    brands varchar(500) NULL,
    url varchar(500) NULL,
    nutrition_grade char(1) NULL,
    fat float NULL,
    saturated_fat float NULL,
    sugars float NULL,
    salt float NULL,
    category VARCHAR(500) NULL,
    CONSTRAINT id PRIMARY KEY (id)
);

-- Table: User_Products
CREATE TABLE User_Products (
    id int NOT NULL AUTO_INCREMENT,
    name varchar(500) NULL,
    brands varchar(500) NULL,
    url varchar(500) NULL,
    nutrition_grade char(1) NULL,
    fat float NULL,
    saturated_fat float NULL,
    sugars float NULL,
    salt float NULL,
    category VARCHAR(500) NULL,
    CONSTRAINT id PRIMARY KEY (id)
);

