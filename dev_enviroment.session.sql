-- Sincroniza a sequência com o maior id existente
SELECT setval('levantamento_id_seq', (SELECT COALESCE(MAX(id), 1) FROM levantamento));

-- Insere os novos registros
INSERT INTO levantamento(id, numero_tombamento, data_levantamento, localidade_levantamento, responsavel_levantamento)
VALUES (NEXTVAL('levantamento_id_seq'),'2025000126', '2023-01-04', 'Local A', 'Responsável A'),
       (NEXTVAL('levantamento_id_seq'),'2025000127', '2023-01-05', 'Local B', 'Responsável B'),
       (NEXTVAL('levantamento_id_seq'),'2025000128', '2023-01-06', 'Local C', 'Responsável C');

