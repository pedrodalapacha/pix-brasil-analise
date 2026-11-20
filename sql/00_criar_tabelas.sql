-- Cria as tabelas no DuckDB a partir dos CSVs brutos.
-- all_varchar evita que o texto "NA" (uma categoria da base) vire NULL.
CREATE OR REPLACE TABLE transacoes AS
SELECT CAST(AnoMes AS INTEGER) AS ano_mes, PAG_PFPJ AS pag_tipo, REC_PFPJ AS rec_tipo,
       PAG_REGIAO AS pag_regiao, REC_REGIAO AS rec_regiao, PAG_IDADE AS pag_idade,
       REC_IDADE AS rec_idade, FORMAINICIACAO AS forma_iniciacao, NATUREZA AS natureza,
       FINALIDADE AS finalidade, CAST(VALOR AS DOUBLE) AS valor, CAST(QUANTIDADE AS DOUBLE) AS quantidade
FROM read_csv('data/raw/pix_transacoes.csv', all_varchar = true);

CREATE OR REPLACE TABLE municipios AS
SELECT CAST(AnoMes AS INTEGER) AS ano_mes, Municipio_Ibge AS cod_ibge, Municipio AS municipio,
       Estado AS estado, Regiao AS regiao,
       CAST(QT_PagadorPF AS DOUBLE) AS qt_pagador_pf, CAST(VL_PagadorPF AS DOUBLE) AS vl_pagador_pf,
       CAST(QT_PES_PagadorPF AS DOUBLE) AS pessoas_pagadoras_pf,
       CAST(QT_RecebedorPJ AS DOUBLE) AS qt_recebedor_pj, CAST(VL_RecebedorPJ AS DOUBLE) AS vl_recebedor_pj
FROM read_csv('data/raw/pix_municipios.csv', all_varchar = true)
WHERE CAST(AnoMes AS INTEGER) <= 202610;          -- 11/2026 veio incompleto

CREATE OR REPLACE TABLE meios_trimestral AS
SELECT * FROM read_csv('data/processed/meios_pagamento_trimestral.csv');

CREATE OR REPLACE TABLE chaves AS
SELECT CAST("Data" AS DATE) AS data, ISPB AS ispb, Nome AS instituicao, Segmento AS segmento,
       TipoChave AS tipo_chave, NaturezaUsuario AS natureza_usuario, CAST(qtdChaves AS BIGINT) AS chaves
FROM read_csv('data/raw/pix_chaves.csv', all_varchar = true);

CREATE OR REPLACE TABLE fraudes AS
SELECT * FROM read_csv('data/raw/pix_fraudes_med.csv');
