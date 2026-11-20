-- Pergunta: quando os pagamentos a empresas (P2B) passaram as transferências entre pessoas (P2P)?
-- Técnicas: agregação condicional (FILTER), CTE, primeira ocorrência.
WITH mensal AS (
    SELECT ano_mes,
           SUM(quantidade) FILTER (WHERE natureza = 'P2P') AS p2p,
           SUM(quantidade) FILTER (WHERE natureza = 'P2B') AS p2b,
           SUM(quantidade)                                  AS total
    FROM transacoes
    GROUP BY ano_mes
)
SELECT ano_mes,
       ROUND(100 * p2p / total, 1) AS part_p2p_pct,
       ROUND(100 * p2b / total, 1) AS part_p2b_pct,
       p2b > p2p                   AS p2b_maior,
       ano_mes = MIN(ano_mes) FILTER (WHERE p2b > p2p) OVER () AS primeiro_mes_p2b_maior
FROM mensal
ORDER BY ano_mes;
