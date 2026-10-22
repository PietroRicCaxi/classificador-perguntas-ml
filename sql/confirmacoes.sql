-- ---------------------------------------------------------------------------
-- CONFIRMAÇÕES DAS ETIQUETAS (PostgreSQL)
-- ---------------------------------------------------------------------------
-- O classificador sugere uma etiqueta para cada pergunta, e quem atende
-- confirma ou corrige. Cada confirmação é um exemplo novo para o próximo
-- treino, e as CORREÇÕES valem mais que as confirmações: são exatamente os
-- casos em que o modelo erra. Por isso a sugestão e a confiança ficam
-- guardadas ao lado da etiqueta confirmada — sem elas não dá para separar uma
-- da outra depois.
--
-- UMA LINHA POR PERGUNTA: confirmar de novo sobrescreve (vale a última
-- palavra de quem atendeu).
--
-- PRIVACIDADE: o TEXTO da pergunta não é gravado. Pergunta é texto livre do
-- comprador e às vezes traz CEP, telefone ou placa. Para retreinar, o texto é
-- lido de novo no Mercado Livre pelo id. Também não há coluna para quem
-- perguntou.
--
-- Versão adaptada para o portfólio: no sistema real a tabela também tem as
-- chaves para as contas e os usuários, e segurança por linha (RLS).
-- ---------------------------------------------------------------------------

BEGIN;

CREATE TABLE IF NOT EXISTS perguntas_rotulos (
  pergunta_id       TEXT PRIMARY KEY CHECK (pergunta_id ~ '^[0-9]{1,30}$'),
  etiqueta          TEXT NOT NULL CHECK (etiqueta IN ('compat', 'lado', 'conteudo', 'medida', 'outra_peca', 'pedido', 'preco_envio', 'outros')),
  etiqueta_sugerida TEXT CHECK (etiqueta_sugerida IN ('compat', 'lado', 'conteudo', 'medida', 'outra_peca', 'pedido', 'preco_envio', 'outros')),
  confianca         NUMERIC CHECK (confianca BETWEEN 0 AND 1),
  versao_modelo     TEXT,
  como              TEXT NOT NULL CHECK (como IN ('confirmou', 'corrigiu', 'copiou_resposta')),
  confirmado_em     TIMESTAMPTZ NOT NULL DEFAULT now()
);

COMMENT ON TABLE perguntas_rotulos IS
  'Etiqueta confirmada por uma pessoa para uma pergunta, ao lado da sugestao do modelo. Base do proximo treino. Sem o texto da pergunta: ele e relido no Mercado Livre pelo id.';
COMMENT ON COLUMN perguntas_rotulos.etiqueta IS
  'A etiqueta que a pessoa confirmou ou escolheu. E o y do proximo treino.';
COMMENT ON COLUMN perguntas_rotulos.etiqueta_sugerida IS
  'O que o modelo sugeriu na hora. NULL quando o modelo nao estava disponivel. etiqueta <> etiqueta_sugerida e uma CORRECAO: o caso que mais ensina.';
COMMENT ON COLUMN perguntas_rotulos.versao_modelo IS
  'A versao do modelo que sugeriu. Sem ela, correcoes de modelos diferentes se misturam na conta de quanto ele erra.';
COMMENT ON COLUMN perguntas_rotulos.como IS
  'confirmou = clicou no visto; corrigiu = escolheu outra etiqueta; copiou_resposta = copiou uma resposta pronta da etiqueta, o que tambem a confirma.';

COMMIT;


-- ---------------------------------------------------------------------------
-- PARA QUE ELA SERVE: quanto o modelo erra em produção, por versão e por
-- faixa de confiança. É a mesma tabela do Passo 14 do notebook, só que medida
-- nas perguntas novas, que o modelo nunca viu.
-- ---------------------------------------------------------------------------
SELECT
  versao_modelo,
  CASE
    WHEN confianca > 0.9 THEN 'acima de 90%'
    WHEN confianca > 0.7 THEN '70–90%'
    WHEN confianca > 0.5 THEN '50–70%'
    ELSE 'até 50%'
  END                                                        AS faixa,
  count(*)                                                   AS perguntas,
  round(avg((etiqueta = etiqueta_sugerida)::int) * 100, 1)   AS acerto_pct
FROM perguntas_rotulos
WHERE etiqueta_sugerida IS NOT NULL
GROUP BY 1, 2
ORDER BY 1, min(confianca);
