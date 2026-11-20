-- Pergunta: o Pix substituiu quais meios de pagamento?
-- Técnicas: window functions (FIRST_VALUE, participação sobre o total do trimestre).
WITH base AS (
    SELECT Trimestre AS trimestre, Meio AS meio, Quantidade AS quantidade,
           Quantidade / SUM(Quantidade) OVER (PARTITION BY Trimestre) AS participacao
    FROM meios_trimestral
),
comparado AS (
    SELECT *,
           FIRST_VALUE(quantidade) OVER (PARTITION BY meio ORDER BY trimestre) AS qtd_2019t1,
           MAX(trimestre) OVER () AS ultimo
    FROM base
)
SELECT meio,
       ROUND(qtd_2019t1 / 1e9, 2)                    AS bilhoes_2019t1,
       ROUND(quantidade / 1e9, 2)                    AS bilhoes_2026t2,
       ROUND(100 * (quantidade / NULLIF(qtd_2019t1, 0) - 1), 0) AS variacao_pct,
       ROUND(100 * participacao, 1)                  AS participacao_2026t2_pct
FROM comparado
WHERE trimestre = ultimo
ORDER BY quantidade DESC;
