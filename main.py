#!/usr/bin/env python3
"""
Script to connect to www.google.com using the Playwright MCP server.
"""

import asyncio
from playwright.async_api import async_playwright
from caixa import process_imoveis
from model import Oferta
from typing import List

def run():
    resultados = process_imoveis('SP', 'RIBEIRAO PRETO')
    export_to_csv(resultados)

def export_to_csv(resultados: List[Oferta]):
    with open("resultados.csv", "w") as f:
        f.write("title;avaliacao;valor;descricao;numero;endereco\n")
        for resultado in resultados:
            f.write(f"{resultado.title};{resultado.avaliacao};{resultado.valor};{resultado.descricao};{resultado.numero};{resultado.endereco}\n")
    

if __name__ == "__main__":
    print("Starting Caixa crawler...")
    run()
    print("\nDone!")