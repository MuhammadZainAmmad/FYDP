CREATE TABLE predicted_imgs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    img BLOB NOT NULL,
    label VARCHAR(20) NOT NULL
);