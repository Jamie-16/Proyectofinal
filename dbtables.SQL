-- Crear tabla Users
CREATE TABLE User(
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
);

-- Crear tabla Categories
CREATE TABLE Category(
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_name TEXT NOT NULL UNIQUE
);

-- Crear tabla Posts
CREATE TABLE Post (
    post_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    user_id INTEGER,
    category_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    image_path TEXT, -- Campo para almacenar la ruta local de la imagen
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (category_id) REFERENCES Categories(category_id)
);
CREATE TABLE Comment (
    comment_id INTEGER PRIMARY KEY,
    body TEXT NOT NULL,
    rating INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    post_id INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user (user_id),
    FOREIGN KEY (post_id) REFERENCES post (post_id)
);


INSERT INTO Category (category_name) VALUES ('Makeup');
INSERT INTO Category (category_name) VALUES ('Hair Stuffs');
INSERT INTO Category (category_name) VALUES ('Outfits');

DROP TABLE Post;
DELETE FROM Post;
DELETE FROM Comment;
DROP TABLE alembic_version;


