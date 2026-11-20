-- Pergunta: como o Pix cresceu mês a mês e ano contra ano?
-- Técnicas: CTE, LAG (window function), média móvel.
WITH mensal AS (
    SELECT ano_mes, SUM(quantidade) AS quantidade, SUM(valor) AS valor
    FROM transacoes
    GROUP BY ano_mes
)
SELECT ano_mes,
       quantidade,
       valor,
       ROUND(valor / quantidade, 2)                                             AS ticket_medio,
       ROUND(100 * (quantidade / LAG(quantidade, 12) OVER (ORDER BY ano_mes) - 1), 1) AS cresc_anual_pct,
       ROUND(AVG(quantidade) OVER (ORDER BY ano_mes ROWS BETWEEN 2 PRECEDING AND CURRENT ROW)) AS media_movel_3m
FROM mensal
ORDER BY ano_mes;
