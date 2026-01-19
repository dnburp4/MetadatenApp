CREATE TABLE metadaten_info (
    meta_id int IDENTITY(1,1) PRIMARY KEY, -- Eindeutiger Key für jeden Eintrag
    datenbank_id varchar(128) not null unique, 
    datenbank_name varchar(256) not null, -- Name der DB, auf die sich die Info bezieht
    verantwortlicher_person varchar(256) not null,
    rolle varchar(256) not null, 
    pfad_quellen varchar(512) not null, 
    erstell_datum datetime DEFAULT GETDATE(), -- Automatisiertes Datum
    letztes_update datetime not null
);

drop table metadaten_info

SELECT * FROM metadaten_info

INSERT INTO metadaten_info (datenbank_id, datenbank_name, verantwortlicher_person, rolle,pfad_quellen,letztes_update) VALUES ('Test_Workshop_140126test', 'Test_Workshop', 'nicolas', 'admin', 'excel.xlsx', GETDATE())