CREATE TABLE IF NOT EXISTS Users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(255) NOT NULL UNIQUE,
  password VARCHAR(255) NOT NULL
);

INSERT INTO Users (username, password) VALUES ('admin', 'TISC{n0t_th3_fl4g}');
INSERT INTO Users (username, password) VALUES ('bobby', 'password');
