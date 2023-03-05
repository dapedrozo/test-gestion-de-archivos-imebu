import sqlite3
conn=sqlite3.connect('ImebuInterno.db')
cur =conn.cursor()
cur.execute("""
    CREATE table  dependencias(
    dependencia VARCHAR(30) PRIMARY KEY
)
""")
cur.execute("""
INSERT into dependencias (dependencia) VALUES 
("direccion"),
("subdiraf"),
("juridica"),
("contabilidad"),
("tesoreria"),
("subtecnica"),
("controlintern"),
("sistemas")
""")
conn.commit()
cur.execute("""
    CREATE table cargos(
    cargo VARCHAR(30) PRIMARY KEY
)
""")
cur.execute("""
INSERT into cargos (cargo) VALUES
("gestDoc"),
("juridica")
""")
conn.commit()
cur.execute("""CREATE table  users(
    tipoDoc VARCHAR(30),
    numDoc VARCHAR(30),
    nombres VARCHAR(60),
    apellidos VARCHAR(60),
    cargo VARCHAR(30),
    pass VARCHAR(128),
    PRIMARY KEY(tipoDoc,numDoc),
    FOREIGN KEY(cargo) REFERENCES cargos(cargo)
)""")
cur.execute("""
INSERT into users (tipoDoc,numDoc,nombres,apellidos,cargo,pass) VALUES
("CC","1102372188","Natalia Juliana","Crusellas","gestDoc","CC1102372188"),
("CC", "1091681226", "Lesly Dayana","Perez Gaona","juridica","CC1091681226"),
("CC","1102384917","Yurley Katterinne", "Becerra Ortiz","juridica","CC1102384917")
""")
conn.commit()
cur.execute("""CREATE Table  inventarioDoc(
    Norden INT,
    codigo VARCHAR(10) NOT NULL,
    serie VARCHAR(60) NOT NULL,
    fechaInicial DATE NOT NULL, 
    fechaFinal DATE NOT NULL,
    Caja INT NOT NULL,
    Carpeta INT NOT NULL,
    Tomo INT NULL,
    otros VARCHAR(30) NULL,
    Nfolios INT NULL,
    Soporte VARCHAR(30) NULL,
    freqConsulta VARCHAR(30) NOT NULL,
    Notas TEXT NULL,
    Observaciones TEXT NULL,
    dependencia VARCHAR(30),
    PRIMARY KEY(Norden,dependencia),
    FOREIGN KEY(dependencia) REFERENCES dependencias(dependencia)
)""")
conn.commit()
conn.close()


