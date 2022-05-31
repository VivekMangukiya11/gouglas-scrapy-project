DROP TABLE IF EXISTS gouglas;


CREATE TABLE gouglas (
    id serial PRIMARY KEY,
    product_name VARCHAR (524),
    ern VARCHAR (100),
    page_url VARCHAR (200),
    rate INTEGER,
    review_count INTEGER,
    image VARCHAR (1024),
    product_ml VARCHAR (50),
    price VARCHAR (50),
    discount_price VARCHAR (50),
    product_lable VARCHAR (200),
    art_no VARCHAR (50),
    alter VARCHAR (524),
    Effekt VARCHAR (524),
    Konsistenz VARCHAR (524),
    Hauttyp VARCHAR (524),
    Eigenschaft TEXT,
    Produktauszeichnung TEXT,
    Produkttyp VARCHAR (200),
    Anwendungsbereich VARCHAR (200),
    description TEXT
)


