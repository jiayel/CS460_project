CREATE DATABASE IF NOT EXISTS photoshare;
USE photoshare;

DROP TABLE IF EXISTS Albums CASCADE;
DROP TABLE IF EXISTS Pictures CASCADE;
DROP TABLE IF EXISTS Friends CASCADE;
DROP TABLE IF EXISTS Users CASCADE;

CREATE TABLE Users (
    User_id int4 AUTO_INCREMENT,
    First_name VARCHAR(30) NOT NULL,
    Last_name VARCHAR(30) NOT NULL,
    email varchar(255) UNIQUE,
    password varchar(255),
    Hometown VARCHAR(100),
    Gender VARCHAR(10) NOT NULL,
    Date_of_birth DATE NOT NULL,
    constraint chk1 check (Gender = 'F' or Gender = 'M' or Gender = 'other'),
    CONSTRAINT users_pk PRIMARY KEY (User_id)
);





CREATE TABLE Albums(
    Album_id INTEGER AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(30) NOT NULL,
    Date_of_creation DATETIME NOT NULL,
    user_id INTEGER,
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);


CREATE TABLE Pictures
(
  picture_id int4  AUTO_INCREMENT,
  User_id int4,
  imgdata longblob ,
  caption VARCHAR(255),
  INDEX upid_idx (User_id),
  CONSTRAINT pictures_pk PRIMARY KEY (picture_id)
);


CREATE TABLE Friends(
    Friends_id INTEGER PRIMARY KEY,
    First_name VARCHAR(30),
    Last_name VARCHAR(30),
    User_id int4 AUTO_INCREMENT,
    constraint fk_User 
    FOREIGN KEY (User_id) REFERENCES Users(User_id)
                    );




-- INSERT INTO Users (email, password) VALUES ('test@bu.edu', 'test');
-- INSERT INTO Users (email, password) VALUES ('test1@bu.edu', 'test');
