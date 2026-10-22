"""Treina o classificador e exporta o modelo em JSON, sem o notebook.

Uso:  python treinar.py dados/rotulos_exemplo.csv

O CSV precisa das colunas `pergunta`, `rotulo` e `origem` (separador ;).
A prova segue a mesma regra do notebook: as cegas + 20% do gabarito.
"""
import json
import sys

import pandas as pd
import sklearn
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline


def novo_modelo():
    return make_pipeline(
        TfidfVectorizer(strip_accents='unicode', lowercase=True, analyzer='char_wb',
                        ngram_range=(2, 5), sublinear_tf=True, min_df=2),
        LogisticRegression(max_iter=3000, C=10, class_weight='balanced'),
    )


def curto(v):
    return float(f'{v:.6g}')


def main(caminho):
    dados = pd.read_csv(caminho, sep=';', dtype=str, encoding='utf-8-sig').fillna('')

    # A prova: só rótulos confiáveis.
    gab = dados[dados['origem'] == 'gabarito']
    _, gab_prova = train_test_split(gab, test_size=0.2, stratify=gab['rotulo'], random_state=42)
    prova = pd.concat([gab_prova, dados[dados['origem'] == 'cega_consenso']])
    treino = dados.drop(prova.index)

    chute = novo_modelo().fit(treino['pergunta'], treino['rotulo']).predict(prova['pergunta'])
    nota = {'acerto': round(accuracy_score(prova['rotulo'], chute), 4),
            'recall_medio': round(recall_score(prova['rotulo'], chute, average='macro'), 4)}
    print(f'treino {len(treino)} | prova {len(prova)} | {nota}')

    # O modelo final usa tudo; a nota que vale para ele é a de cima.
    final = novo_modelo().fit(dados['pergunta'], dados['rotulo'])
    vet, reg = final[0], final[1]
    nomes, idf, pesos = vet.get_feature_names_out(), vet.idf_, reg.coef_
    modelo = {
        'versao': pd.Timestamp.now().strftime('%Y-%m-%d'),
        'sklearn': sklearn.__version__,
        'treinado_com': len(dados),
        'nota_na_prova': nota,
        'ngram': list(vet.ngram_range),
        'etiquetas': reg.classes_.tolist(),
        'base': [curto(b) for b in reg.intercept_],
        'pedacos': {n: [curto(idf[i])] + [curto(w) for w in pesos[:, i]] for i, n in enumerate(nomes)},
    }
    with open('modelo_perguntas.json', 'w', encoding='utf-8') as f:
        json.dump(modelo, f, ensure_ascii=False, separators=(',', ':'))
    print(f'modelo_perguntas.json: {len(nomes)} pedaços')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
