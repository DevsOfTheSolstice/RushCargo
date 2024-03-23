-- Legal identifications
INSERT INTO legal_identification (id, country_id, document, due_date, expedition_date)
VALUES (0, 0, 'Legal identification 0', '2024-12-01', '2022-12-01');

INSERT INTO legal_identification (id, country_id, document, due_date, expedition_date)
VALUES (1, 0, 'Legal identification 1', '2024-12-01', '2022-12-01');

-- Admins
INSERT INTO root_user (username, warehouse_id, identity_document, user_password)
-- Passwd: admin0
VALUES ('admin0', 0, 0, '$2a$04$9LHD8K3Icib7/x89QSKOCO1nH2fNH43hj7nd/cob3ZMKwYj2v9edq');

INSERT INTO root_user (username, warehouse_id, identity_document, user_password)
-- Passwd: admin1
VALUES ('admin1', 3, 1, '$2a$04$33X714FkR6Ddmfh8zlZYLuEu5caLY2glCFmoF3dyes74.f0Ff/Okq');