CREATE DATABASE IF NOT EXISTS photoshare;
USE photoshare;

DROP TABLE IF EXISTS Albums CASCADE;
DROP TABLE IF EXISTS Pictures CASCADE;
DROP TABLE IF EXISTS Friends CASCADE;
DROP TABLE IF EXISTS Users CASCADE;

CREATE TABLE Users (
    user_id int4  AUTO_INCREMENT,
    First_name VARCHAR(30) NOT NULL,
    Last_name VARCHAR(30) NOT NULL,
    email varchar(255) UNIQUE,
    password varchar(255),
    Hometown VARCHAR(100),
    Gender VARCHAR(10) NOT NULL,
    Date_of_birth DATE NOT NULL,
    constraint chk1 check (Gender = 'F' or Gender = 'M' or Gender='other'),
    CONSTRAINT users_pk PRIMARY KEY (user_id)
);




CREATE TABLE Friends(
    Friends_id INTEGER,
    Friends_email varchar(225) UNIQUE,
    user_id INTEGER,
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    PRIMARY KEY(user_id, Friends_id)
                    );


CREATE TABLE Albums(
    Album_id int4 AUTO_INCREMENT,
    Album_name VARCHAR(30) NOT NULL,
    Date_of_creation DATE NOT NULL,
    user_id INTEGER,
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
	CONSTRAINT Album_id PRIMARY KEY (Album_id)

);

CREATE TABLE Pictures
(
  picture_id int4  AUTO_INCREMENT,
  imgdata longblob NOT NULL,
  caption VARCHAR(255),
  Album_id int4,
  user_id int4,
  FOREIGN KEY (Album_id) REFERENCES Albums(Album_id),
  FOREIGN KEY (user_id) REFERENCES Users(user_id),
  INDEX upid_idx (user_id),
  CONSTRAINT pictures_pk PRIMARY KEY (picture_id)
);


