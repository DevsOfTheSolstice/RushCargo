-- Legal identifications
INSERT INTO legal_identifications (legal_id, country_id, document_description, expedition_date, identification_type)
VALUES (0, 0, 'Legal identification 0', '2022-12-01', 'AdminID');

INSERT INTO legal_identifications (legal_id, country_id, document_description, expedition_date, identification_type)
VALUES (1, 0, 'Legal identification 1', '2022-12-01', 'AdminID');

-- Admins
INSERT INTO root_users (username, warehouse_id, id_document, user_password, user_type, first_name, last_name)
-- Passwd: admin0
VALUES ('admin0', 0, 0, '$2a$04$9LHD8K3Icib7/x89QSKOCO1nH2fNH43hj7nd/cob3ZMKwYj2v9edq', 'PkgAdmin', 'Sans', 'Undertale');

INSERT INTO root_users (username, warehouse_id, id_document, user_password, user_type, first_name, last_name)
-- Passwd: admin1
VALUES ('admin1', 3, 1, '$2a$04$33X714FkR6Ddmfh8zlZYLuEu5caLY2glCFmoF3dyes74.f0Ff/Okq', 'PkgAdmin', 'Ichiban', 'Kasuga');