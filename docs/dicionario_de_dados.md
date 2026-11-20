# Dicionário de dados

Estrutura conferida diretamente no `$metadata` da API do Banco Central em 11/11/2026.
As descrições de negócio marcadas com (*) são minha leitura do nome do campo e devem
ser confirmadas na documentação oficial antes de entrar no README final.

Fonte Pix: https://olinda.bcb.gov.br/olinda/servico/Pix_DadosAbertos/versao/v1/odata/
Fonte meios de pagamento: https://olinda.bcb.gov.br/olinda/servico/MPV_DadosAbertos/versao/v1/odata/

## Comportamento da API (testado)
- O parâmetro de data é a data **inicial**: `Database='202509'` devolve de 09/2025 em diante.
- Para um único mês, usar `$filter=AnoMes eq 202509`.
- Volume aproximado: transações ~15 mil linhas/mês; municípios ~5,6 mil linhas/mês;
  chaves ~6 mil linhas/mês; recebedor ~95 mil linhas no total; fraudes 57 meses (01/2022 a 09/2026);
  usuários DICT 72 meses (11/2020 a 10/2026).

## pix_transacoes.csv (EstatisticasTransacoesPix)
Uma linha por combinação de mês e perfil de pagador/recebedor.
| Campo | Tipo | Descrição |
|---|---|---|
| AnoMes | inteiro | Mês de referência (AAAAMM) |
| PAG_PFPJ, REC_PFPJ | texto | Pagador / recebedor é pessoa física (PF) ou jurídica (PJ) |
| PAG_REGIAO, REC_REGIAO | texto | Região do pagador / recebedor |
| PAG_IDADE, REC_IDADE | texto | Faixa etária do pagador / recebedor |
| FORMAINICIACAO | texto | Forma de iniciação: QRDN = QR Code dinâmico e QRES = QR Code estático (Informe SPI 013/2021); DICT = chave Pix; MANU = dados da conta digitados; INIC, APDN, APES, AUTO não interpretadas (*) |
| NATUREZA | texto | Natureza da transação, ex.: P2P, P2B (*) |
| FINALIDADE | texto | Finalidade (*); há "Nao disponivel" |
| VALOR | decimal | Valor total em R$ |
| QUANTIDADE | decimal | Número de transações |

## pix_municipios.csv (TransacoesPixPorMunicipio)
| Campo | Tipo | Descrição |
|---|---|---|
| AnoMes | inteiro | Mês de referência |
| Municipio_Ibge, Municipio | inteiro, texto | Código IBGE e nome do município |
| Estado_Ibge, Estado | inteiro, texto | Código IBGE e nome do estado |
| Sigla_Regiao, Regiao | texto | Região |
| VL_PagadorPF / VL_PagadorPJ | decimal | Valor pago por PF / PJ (R$) |
| QT_PagadorPF / QT_PagadorPJ | decimal | Quantidade de transações pagas por PF / PJ |
| VL_RecebedorPF / VL_RecebedorPJ | decimal | Valor recebido por PF / PJ (R$) |
| QT_RecebedorPF / QT_RecebedorPJ | decimal | Quantidade recebida por PF / PJ |
| QT_PES_PagadorPF / PJ, QT_PES_RecebedorPF / PJ | decimal | Número de pessoas distintas pagadoras / recebedoras (*) |

## pix_recebedor_cnae_porte.csv (CnaePorteRecebedor)
| Campo | Tipo | Descrição |
|---|---|---|
| AnoMes | inteiro | Mês de referência |
| tipopessoa | texto | PF ou PJ |
| formainic | texto | Forma de iniciação (*) |
| finalidade | texto | Finalidade (*) |
| porte | texto | Porte da empresa, ex.: Microempresa |
| mei | texto | S/N: é MEI |
| cnssecao | texto | Seção da CNAE (setor de atividade) |
| mesmatit | texto | S/N: transferência entre contas do mesmo titular. Excluir para analisar pagamentos (conferido com o RPM dez/2025 do BCB) |
| naturezarel | texto | Natureza, ex.: P2B |
| qtpagador, qtrecebedor | inteiro | Número de pagadores / recebedores (*) |
| qtlanliq, vllanliq | inteiro, decimal | Quantidade e valor liquidados (*) |
| vlcompra, vldinespec | decimal | Valor de compra e valor em espécie (Pix Saque/Troco) (*) |

## pix_fraudes_med.csv (EstatisticasFraudesPix)
Uma linha por mês. Principais campos:
| Campo | Descrição |
|---|---|
| AnoMes | Mês de referência |
| QtdePixcontestados | Pix contestados |
| Qtdecontestacoesaceitas / rejeitadas | Contestações aceitas / rejeitadas |
| Qtdecontestacoesaceitasacada100mil | Contestações aceitas a cada 100 mil transações |
| ValorPixcontestadosaceitos | Valor das contestações aceitas (R$) |
| Valor/Quantidade devolvida integral e parcialmente | Devoluções pelo MED |
| ValorPixresidualnaodevolvido | Valor não recuperado |
| ...naodevolvidos saldoinsuficiente / contaencerrada / motivosdiversos | Motivos da não devolução |
| PercentualdeDevolucao | % do valor devolvido |
| ...bloqueadoscautelarmente... | Bloqueios cautelares liberados / devolvidos |
| QtdeUsuarios / QtdeChavesPixcommarcacoesdefraude | Usuários e chaves com marcação de fraude |

## pix_chaves.csv (ChavesPix)
| Campo | Tipo | Descrição |
|---|---|---|
| Data | data | Último dia do mês |
| ISPB, Nome | texto | Identificador e nome da instituição |
| NaturezaUsuario | texto | PF ou PJ |
| TipoChave | texto | Celular, CPF, e-mail, aleatória etc. |
| qtdChaves | inteiro | Estoque de chaves |
| Segmento | texto | Tipo de instituição, ex.: Cooperativa de Crédito |

## pix_usuarios_dict.csv (PixUsuariosCadastradosDICT)
| Campo | Descrição |
|---|---|
| DataGraficosPix | Último dia do mês |
| qtdUsuariosPessoaFisica / PessoaJuridica / CadastradosDICTTotal | Usuários com chave cadastrada |

## meios_pagamento_mensal.csv e meios_pagamento_trimestral.csv
Quantidade em **milhares** e valor em **R$ milhões** (conferido: 09/2026 mostra
7.892.937 mil transações Pix e R$ 3.811.091 milhões, igual ao painel "Pix em números").
- Mensal: Pix, TED, TEC, cheque, boleto, DOC.
- Trimestral: os anteriores mais cartão de crédito, débito e pré-pago, transferência
  intrabancária, convênios, débito direto e saques.
