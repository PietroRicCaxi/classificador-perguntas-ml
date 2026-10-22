"""Gera os dados de EXEMPLO do repositório de portfólio.

Tudo aqui é inventado a partir de modelos de frase escritos à mão: nenhuma
pergunta, anúncio, conta ou resposta real entra. Serve só para o notebook
rodar de ponta a ponta com o mesmo formato dos dados reais.
"""
import csv, random, sys, os

saida = sys.argv[1]
os.makedirs(saida, exist_ok=True)
rnd = random.Random(7)

CARROS = ['Gol', 'Onix', 'HB20', 'Corolla', 'Civic', 'Hilux', 'Fiesta', 'Palio', 'Uno', 'Sandero',
          'Kwid', 'Ka', 'Fox', 'Polo', 'Strada', 'Toro', 'Compass', 'Renegade', 'Tracker', 'Creta']
PECAS = ['Parabarro Dianteiro', 'Presilha do Parachoque', 'Manopla de Câmbio', 'Spoiler Traseiro',
         'Grade do Radiador', 'Moldura do Paralama', 'Guia do Parachoque', 'Protetor de Cárter']

MODELOS = {
    'compat': ['serve no {c} {a}?', 'Serve no meu {c} {a}', 'da certo no {c} {a}?', 'é compatível com {c} {a}?',
               'cabe no {c} {a} completo?', 'boa tarde, serve pro {c} {a}??', 'funciona no {c} versão {a}?',
               'SERVE NO {C} {a}?'],
    'lado': ['é o lado do motorista?', 'tem o lado direito?', 'qual lado é esse?', 'preciso do esquerdo',
             'esse é o do passageiro?', 'vende só o lado direito?', 'é o dianteiro ou traseiro?',
             'vem o esquerdo ou o direito?'],
    'conteudo': ['vem com as presilhas?', 'acompanha os parafusos?', 'é o par ou só uma?', 'quantas peças vem no kit?',
                 'vem com a braçadeira?', 'já vem montado?', 'vem com manual?', 'o kit vem completo?'],
    'medida': ['qual o diâmetro do furo?', 'é de plástico ou de metal?', 'é original ou paralela?',
               'qual o tamanho em cm?', 'é de rosca ou de encaixe?', 'qual a cor exata?', 'é fácil de instalar?',
               'qual o material?'],
    'outra_peca': ['tem para o {c} {a}?', 'vocês tem na cor preta?', 'vende só a presilha?', 'tem o traseiro também?',
                   'teria a moldura do {c}?', 'tem esse modelo para {c}?', 'vende a peça avulsa?',
                   'tem em outra cor?'],
    'pedido': ['meu pedido não chegou', 'comprei e veio o lado errado', 'quero devolver a peça',
               'quando vão despachar minha compra?', 'veio faltando uma peça', 'quero cancelar a compra',
               'o produto chegou quebrado', 'comprei ontem, já foi enviado?'],
    'preco_envio': ['faz por 50 no pix?', 'qual o valor do frete?', 'emite nota fiscal?', 'tem desconto no par?',
                    'chega até sexta?', 'envia hoje?', 'aceita oferta?', 'parcela sem juros?'],
    'outros': ['boa tarde', 'obrigado!', 'ok vou comprar', 'valeu', 'bom dia', 'certo, obrigado', 'perfeito', '??'],
}
ETIQUETAS = list(MODELOS)


def uma(etiqueta):
    c, a = rnd.choice(CARROS), rnd.randint(2008, 2025)
    return rnd.choice(MODELOS[etiqueta]).format(c=c, C=c.upper(), a=a)


def digitar_errado(t):
    # Tira ou troca uma letra, como no celular.
    if len(t) < 4:
        return t
    i = rnd.randrange(1, len(t) - 1)
    return t[:i] + (rnd.choice('aeiosrn') if rnd.random() < 0.5 else '') + t[i + 1:]


def pergunta(etiqueta):
    t = uma(etiqueta)
    # Dois assuntos na mesma pergunta: a etiqueta é a do primeiro, e o modelo pode se confundir.
    if rnd.random() < 0.25:
        t = t.rstrip('?') + ' e ' + uma(rnd.choice(ETIQUETAS))
    if rnd.random() < 0.3:
        t = digitar_errado(t)
    return t


def titulo():
    return f'{rnd.choice(PECAS)} {rnd.choice(CARROS)} {rnd.randint(2008, 2018)}/{rnd.randint(2019, 2025)}'


# Mesma proporção aproximada dos dados reais: metade compatibilidade.
PESOS = {'compat': 12, 'lado': 3, 'conteudo': 3, 'medida': 3, 'outra_peca': 4, 'pedido': 3, 'preco_envio': 3, 'outros': 3}

linhas, n = [], 0
for origem, quantas in [('gabarito', 250), ('cega_consenso', 60), ('claude', 690)]:
    # O sorteio estratificado precisa de alguns exemplos de cada etiqueta em cada origem.
    base = [e for e in ETIQUETAS for _ in range(4 if origem != 'cega_consenso' else 2)]
    resto = rnd.choices(ETIQUETAS, weights=[PESOS[e] for e in ETIQUETAS], k=quantas - len(base))
    for e in base + resto:
        n += 1
        cego_p = cego_c = ''
        if origem == 'cega_consenso':
            # Dois rotuladores que discordam em parte das perguntas, como nos dados reais.
            cego_p = e if rnd.random() > 0.16 else rnd.choice(ETIQUETAS)
            cego_c = e if rnd.random() > 0.08 else rnd.choice(ETIQUETAS)
        texto = pergunta(e)
        rotulo = e
        # Rótulo errado de vez em quando no que não foi revisado à mão, como acontece de verdade.
        if origem == 'claude' and rnd.random() < 0.08:
            rotulo = rnd.choice(ETIQUETAS)
        linhas.append({'id_pergunta': f'EX{n:05d}', 'conta': rnd.choice(['LOJA_A', 'LOJA_B', 'LOJA_C']),
                       'titulo_anuncio': titulo(), 'pergunta': texto, 'rotulo': rotulo, 'origem': origem,
                       'duvida': '', 'cego_pietro': cego_p, 'cego_claude': cego_c})

with open(os.path.join(saida, 'rotulos_exemplo.csv'), 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.DictWriter(f, fieldnames=list(linhas[0]), delimiter=';')
    w.writeheader(); w.writerows(linhas)

todas = []
for i in range(1, 301):
    e = rnd.choices(ETIQUETAS, weights=[PESOS[x] for x in ETIQUETAS])[0]
    todas.append({'conta': rnd.choice(['LOJA_A', 'LOJA_B', 'LOJA_C']), 'id_pergunta': f'NV{i:05d}',
                  'anuncio': f'ANUNCIO-{rnd.randint(1, 40):03d}', 'titulo_anuncio': titulo(), 'pergunta': pergunta(e)})
with open(os.path.join(saida, 'perguntas_exemplo.csv'), 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.DictWriter(f, fieldnames=list(todas[0]), delimiter=';')
    w.writeheader(); w.writerows(todas)
print(len(linhas), 'rotuladas;', len(todas), 'sem rótulo')
