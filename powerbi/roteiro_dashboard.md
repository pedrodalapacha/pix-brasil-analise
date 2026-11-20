# Roteiro do dashboard (Power BI)

O modelo de dados já está pronto: tabelas, relacionamentos e 36 medidas (na tabela `_Medidas`, organizadas em pastas). Este roteiro é para montar os visuais.

## Antes de começar
1. Salve o arquivo como `powerbi/analise-pix-brasil-power-bi.pbix`, dentro da pasta do projeto.
2. Abra a exibição de Modelo e organize as tabelas: `dCalendario` no centro, as tabelas `f...` (fatos) em volta, e as outras `d...` (dimensões) nas pontas. Tire um print para o README: é a prova do modelo em estrela.
3. Regra do modelo: use sempre colunas das tabelas `d...` nos eixos, legendas e filtros, e medidas da `_Medidas` nos valores. As colunas numéricas das tabelas `f...` estão ocultas de propósito.
4. Se mover o projeto de pasta: Transformar dados > Gerenciar parâmetros > `PastaDados`.

## Padrão visual
- Uma cor principal (azul) e uma de destaque (laranja). Sem 3D, sem pizza com mais de 3 fatias.
- O título de cada gráfico diz a conclusão, não só o tema.
- No máximo 4 a 5 visuais por página.
- Em toda página: segmentação de `dCalendario[Ano]` no topo.

## Página 1: Visão geral
| Visual | Campos |
|---|---|
| Cartão | `[Transações (bi)]` |
| Cartão | `[Valor (R$ tri)]` |
| Cartão | `[Usuários PF]` |
| Cartão | `[Ticket médio (R$)]` |
| Cartão | `[Crescimento anual %]` |
| Gráfico de linhas | Eixo X: `dCalendario[AnoMes]`; Y: `[Transações (bi)]` |
| Gráfico de colunas | Eixo X: `dCalendario[Ano]`; Y: `[Crescimento anual %]` |

Título sugerido da linha: "Pix passou de 7 bilhões de transações por mês em 2026".
Conferência: com Ano = 2025, os cartões devem mostrar 71,3 bi, R$ 29,61 tri e ticket de R$ 415,15.

## Página 2: Como o Pix é usado
| Visual | Campos |
|---|---|
| Gráfico de linhas | X: `dCalendario[AnoMes]`; Y: `[% P2P]` e `[% P2B]` |
| Colunas 100% empilhadas | X: `dCalendario[Ano]`; Legenda: `dFormaIniciacao[Forma]`; Y: `[Transações por forma]` |
| Gráfico de linhas | X: `dCalendario[AnoMes]`; Y: `[Transações por usuário (mês)]` |
| Matriz | Linhas: `dNatureza[NaturezaNome]`; Colunas: `dCalendario[Ano]`; Valores: `[% das transações]` |

Título sugerido: "Pagamentos a empresas passaram as transferências entre pessoas em set/2025".

## Página 3: Pix x outros meios de pagamento
| Visual | Campos |
|---|---|
| Gráfico de linhas | X: `dCalendario[Trimestre]`; Legenda: `dMeio[Meio]`; Y: `[Participação nas transações]`. Filtre o visual para Pix, cartão de crédito, cartão de débito, boleto e saques |
| Linhas em múltiplos pequenos | X: `dCalendario[Trimestre]`; Y: `[Transações (meios, bi)]`; Múltiplos pequenos: `dMeio[Meio]` (crédito, débito, boleto, saques, TED, cheque). Desative "eixo Y compartilhado" |
| Matriz | Linhas: `dMeio[Grupo]` e `dMeio[Meio]`; Colunas: `dCalendario[Ano]`; Valores: `[Transações (meios, bi)]` |

Nesta página, a segmentação de Ano começa em 2019.
Nota de rodapé obrigatória (caixa de texto): "Inclui o Pix liquidado fora do SPI; por isso os totais de Pix são maiores que nas outras páginas."
Conferência: no 2º tri/2026, a participação do Pix é 56,0%.

## Página 4: Onde o Pix é mais usado
| Visual | Campos |
|---|---|
| Barras horizontais | Y: `dEstado[UF]`; X: `[Pix por pagador PF (mês)]`; Legenda: `dEstado[Regiao]` |
| Mapa coroplético (opcional) | Local: `dEstado[UF]`; Saturação: `[Pix por pagador PF (mês)]` |
| Dispersão | X: `[Ticket médio PF (R$)]`; Y: `[Pix por pagador PF (mês)]`; Valores: `dEstado[UF]`; Legenda: `dEstado[Regiao]` |

Filtre a página para excluir `dEstado[UF]` = "Não Informado".
A dispersão mostra o achado: onde se usa mais, o ticket é menor.
Conferência: com Ano = 2026, Amazonas mostra 60,4 Pix por pagador ao mês (média de jan a out; em out/2026 isolado são 62,7).

## Página 5: Setores e fraudes
| Visual | Campos |
|---|---|
| Barras horizontais | Y: `dSetor[SetorNome]`; X: `[% das transações por setor]` (top 8) |
| Gráfico de linhas | X: `dCalendario[Ano]`; Legenda: `dSetor[SetorNome]` (comércio, atividades profissionais, recreação); Y: `[% das transações por setor]` |
| Gráfico de linhas | X: `dCalendario[AnoMes]`; Y: `[Aceitas por 100 mil Pix]` |
| Cartões | `[% do valor devolvido]`, `[% não devolvido por falta de saldo]`, `[Ticket médio da fraude (R$)]` |

Os dados de setor são anuais: use `dCalendario[Ano]`, não mês.
Notas de rodapé: "Setores excluem transferências entre contas do mesmo titular." e "Fraudes: dados de 01/2022 a 09/2026."
Não use `[Pix contestados]` em série histórica: o número muda de patamar em out/2025 por causa do autoatendimento do MED.

## Página 6: Conclusões
Caixa de texto com os 4 achados principais e as 4 recomendações do README, mais as limitações. Sem gráficos.

## Depois de montar
- Tire prints das páginas e salve em `docs/img/` (ex.: `pbi_01_visao_geral.png`).
- Adicione os prints ao README, na seção de resultados.
