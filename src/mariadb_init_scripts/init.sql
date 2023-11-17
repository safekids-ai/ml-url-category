CREATE DATABASE IF NOT EXISTS safekids_db;
USE safekids_db;

CREATE TABLE IF NOT EXISTS urls_table (
    id INT AUTO_INCREMENT,
    url VARCHAR(255),
    meta VARCHAR(255),
    prediction VARCHAR(255),
    PRIMARY KEY (id)
);
