-- Pergunta: como evoluíram as contestações por fraude (MED) e quanto se recupera?
-- Observação: 2026 vai até setembro.
SELECT AnoMes // 100                                    AS ano,
       COUNT(*)                                         AS meses,
       SUM(QtdePixcontestados)                          AS contestados,
       SUM(Qtdecontestacoesaceitas)                     AS aceitas,
       ROUND(100.0 * SUM(Qtdecontestacoesaceitas) / SUM(QtdePixcontestados), 1) AS taxa_aceitacao_pct,
       ROUND(SUM(ValorPixcontestadosaceitos) / 1e9, 2)  AS valor_aceito_bilhoes,
       ROUND(100.0 * (SUM(ValorPixdevolvidosintegralmente) + SUM(ValorPixdevolvidosparcialmente))
             / SUM(ValorPixcontestadosaceitos), 1)      AS valor_devolvido_pct,
       ROUND(AVG(Qtdecontestacoesaceitasacada100mil), 2) AS aceitas_por_100mil_media
FROM fraudes
GROUP BY ano
ORDER BY ano;
