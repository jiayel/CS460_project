CREATE DATABASE IF NOT EXISTS photoshare;
USE photoshare;
DROP TABLE IF EXISTS Pictures CASCADE;
DROP TABLE IF EXISTS Users CASCADE;

CREATE TABLE Users (
    user_id int4  AUTO_INCREMENT,
    First_name VARCHAR(30) NOT NULL,
    Last_name VARCHAR(30) NOT NULL,
    email varchar(255) UNIQUE,
    password varchar(255),
    Hometown VARCHAR(100),
    Gender VARCHAR(1) NOT NULL,
    Date_of_birth DATE NOT NULL,
    constraint chk1 check (Gender = 'F' or Gender = 'M'),
    CONSTRAINT users_pk PRIMARY KEY (user_id)
);


DROP TABLE IF EXISTS Frinds CASCADE;

CREATE TABLE Friends(
    Friends_id INTEGER PRIMARY KEY,
    Friends_email varchar(225) UNIQUE,
    user_id INTEGER,
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
                    );

DROP TABLE IF EXISTS Albums CASCADE;
CREATE TABLE Albums(
    Album_id INTEGER PRIMARY KEY,
    name VARCHAR(30) NOT NULL,
    Date_of_creation DATE NOT NULL,
    user_id INTEGER,
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

CREATE TABLE Pictures
(
  picture_id int4  AUTO_INCREMENT,
  user_id int4,
  imgdata longblob ,
  caption VARCHAR(255),
  INDEX upid_idx (user_id),
  CONSTRAINT pictures_pk PRIMARY KEY (picture_id)
);




INSERT INTO Users (email, password) VALUES ('test@bu.edu', 'test');
INSERT INTO Users (email, password) VALUES ('test1@bu.edu', 'test');
