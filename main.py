#!/usr/bin/env python3
"""
Script to connect to www.google.com using the Playwright MCP server.
"""

from caixa import process_imoveis
from model import Oferta
from typing import List

def run():
    resultados = process_imoveis('SP', 'RIBEIRAO PRETO')
    export_to_csv(resultados)

def export_to_csv(resultados: List[Oferta]):
    with open("resultados.csv", "w") as f:
        f.write("uf;cidade;title;avaliacao;valor;desconto;descricao;numero;endereco;endereco_normalizado;link\n")
        for resultado in resultados:
            f.write(f"{resultado.uf};{resultado.cidade};{resultado.title};{resultado.avaliacao};{resultado.valor};{resultado.desconto};{resultado.descricao};{resultado.numero};{resultado.endereco};{resultado.endereco_normalizado};{resultado.link}\n")
    

if __name__ == "__main__":
    print("Starting Caixa crawler...")
    run()
    print("\nDone!")