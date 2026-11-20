-- Pergunta: o mercado de chaves Pix é concentrado? Quem lidera?
-- Técnicas: CTE, participação acumulada, ROW_NUMBER.
WITH inst AS (
    SELECT instituicao, segmento, SUM(chaves) AS chaves
    FROM chaves
    WHERE data = (SELECT MAX(data) FROM chaves)
    GROUP BY instituicao, segmento
)
SELECT ROW_NUMBER() OVER (ORDER BY chaves DESC)                         AS posicao,
       instituicao, segmento, chaves,
       ROUND(100 * chaves / SUM(chaves) OVER (), 1)                     AS participacao_pct,
       ROUND(100 * SUM(chaves) OVER (ORDER BY chaves DESC) / SUM(chaves) OVER (), 1) AS acumulado_pct
FROM inst
ORDER BY chaves DESC
LIMIT 15;
