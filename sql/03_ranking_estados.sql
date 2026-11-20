-- Pergunta: em quais estados cada pessoa usa mais o Pix?
-- Técnicas: JOIN de duas CTEs (mesmo mês em anos diferentes), RANK.
WITH uf AS (
    SELECT ano_mes, estado, regiao,
           SUM(qt_pagador_pf)        AS pix_pf,
           SUM(vl_pagador_pf)        AS valor_pf,
           SUM(pessoas_pagadoras_pf) AS pessoas
    FROM municipios
    WHERE estado <> 'NAO INFORMADO'
    GROUP BY ano_mes, estado, regiao
)
SELECT a.estado, a.regiao,
       ROUND(a.pix_pf / a.pessoas, 1)   AS pix_por_pagador_out2026,
       ROUND(b.pix_pf / b.pessoas, 1)   AS pix_por_pagador_out2022,
       ROUND(a.valor_pf / a.pix_pf, 2)  AS ticket_medio_out2026,
       RANK() OVER (ORDER BY a.pix_pf / a.pessoas DESC) AS posicao
FROM uf a
JOIN uf b ON a.estado = b.estado AND b.ano_mes = 202210
WHERE a.ano_mes = 202610
ORDER BY posicao;
