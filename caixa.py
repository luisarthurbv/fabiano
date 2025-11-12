from decimal import Decimal, ROUND_HALF_UP

from typing import List
import asyncio
import re
from playwright.async_api import async_playwright
from model import Oferta

LINK = "https://venda-imoveis.caixa.gov.br/sistema/detalhe-imovel.asp?hdnimovel="

# https://venda-imoveis.caixa.gov.br/sistema/busca-imovel.asp?sltTipoBusca=imoveis
async def _parse_ofertas_from_page(uf, cidade, page) -> List[Oferta]:
    lista_selector = "#listaimoveispaginacao ul.control-group.no-bullets"
    await page.locator(lista_selector).first.wait_for()

    itens = page.locator(f"{lista_selector} li.group-block-item")
    count = await itens.count()

    resultados: List[Oferta] = []

    for i in range(count):
        item = itens.nth(i)
        dados = item.locator("div.dadosimovel-col2 ul.form-set.inside-set.no-bullets > li")
        li0 = dados.nth(0)
        title = (await li0.locator("a").first.inner_text()).strip()
        li0_text = (await li0.inner_text()).strip()
        li0_lines = [l.strip() for l in li0_text.split("\n") if l.strip()]
        if li0_lines and li0_lines[0] == title:
            li0_lines = li0_lines[1:]
        avaliacao = li0_lines[0] if len(li0_lines) > 0 else ""
        if not avaliacao:
            raise Exception("Invalid avaliacao text: " + li0_text)
        avaliacao_normalized = extrair_valor(avaliacao) if avaliacao else ""

        valor = li0_lines[1] if len(li0_lines) > 1 else ""
        if not valor:
            raise Exception("Invalid valor text: " + li0_text)
        valor_normalized = extrair_valor(valor)

        li1 = dados.nth(1)
        li1_text = (await li1.inner_text()).strip()
        li1_lines = [l.strip() for l in li1_text.split("\n") if l.strip()]
        descricao = li1_lines[0] if len(li1_lines) > 0 else ""
        numero_raw = li1_lines[1] if len(li1_lines) > 1 else ""
        endereco = li1_lines[2] if len(li1_lines) > 2 else ""

        numero = numero_raw
        if ":" in numero_raw:
            numero = numero_raw.split(":", 1)[1].strip()
            numero = numero.replace("-", "")

        resultados.append(
            Oferta(
                uf=uf,
                cidade=cidade,
                title=title,
                avaliacao=avaliacao_normalized,
                valor=valor_normalized,
                desconto=calcular_desconto(avaliacao_normalized, valor_normalized),
                descricao=descricao,
                numero=numero,
                endereco=endereco,
                endereco_normalizado=f"{endereco} , {cidade} - {uf}",
                link=LINK + numero,
            )
        )

    return resultados

def calcular_desconto(avaliacao: Decimal, valor: Decimal):
    rate = (avaliacao-valor) / avaliacao
    return (100 * rate).quantize(Decimal("0.00"), rounding=ROUND_HALF_UP)

def extrair_valor(text) -> Decimal:
    regex = r"(\d{1,3}(?:\.\d{3})*(?:,\d{2}))"

    # re.search() finds the first match in the string
    match = re.search(regex, text)
    if not match:
        raise Exception("Invalid text: " + text)

    number_string = match.group(1)
    valor = number_string.replace('.', '').replace(',', '.')
    return Decimal(valor)


def process_imoveis(estado: str, cidade: str) -> List[Oferta]:
    ofertas: List[Oferta] = []

    async def _run() -> List[Oferta]:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context()
            page = await context.new_page()

            await page.goto(
                "https://venda-imoveis.caixa.gov.br/sistema/busca-imovel.asp?sltTipoBusca=imoveis",
                wait_until="domcontentloaded",
            )
            await page.wait_for_timeout(5000)

            await page.select_option("#cmb_estado", value=estado)
            await page.wait_for_timeout(5000)
            await page.select_option("#cmb_cidade", value=cidade)
            await page.wait_for_timeout(5000)
            await page.select_option("#cmb_modalidade", value="Venda Direta Online")
            await page.wait_for_timeout(5000)

            await page.get_by_role("button", name=re.compile("Pr[oó]ximo", re.IGNORECASE)).click()
            await page.wait_for_load_state("domcontentloaded")
            await page.wait_for_timeout(5000)

            await page.get_by_text(re.compile(r"Dados do im[óo]vel", re.IGNORECASE)).wait_for()
            await page.get_by_role("button", name=re.compile("Pr[oó]ximo", re.IGNORECASE)).click()
            await page.wait_for_load_state("domcontentloaded")

            ofertas = await _parse_ofertas_from_page(estado, cidade, page)
            # Determine total number of pages from hidden input or pagination links
            total_paginas = 1
            try:
                if await page.locator("#hdnQtdPag").count() > 0:
                    qtd_raw = await page.locator("#hdnQtdPag").first.input_value()
                    total_paginas = int(qtd_raw.strip()) if qtd_raw and qtd_raw.strip().isdigit() else 1
            except Exception:
                total_paginas = 1

            # Iterate remaining pages
            for pag in range(2, total_paginas + 1):
                try:
                    # Click on the page number inside the pagination container
                    await page.locator("#paginacao").get_by_text(str(pag), exact=True).click()
                    # Wait a bit for the list to refresh
                    await page.wait_for_timeout(4000)
                    # Ensure list container has content
                    await page.locator("#listaimoveispaginacao ul.control-group.no-bullets").first.wait_for()
                    resultados_pag = await _parse_ofertas_from_page(estado, cidade, page)
                    ofertas.extend(resultados_pag)
                except Exception:
                    # If any page fails, continue to the next
                    print(f"Failed to parse page {pag}. Continuing...")
                    continue

            await context.close()
            await browser.close()

            return ofertas

    ofertas = asyncio.run(_run())
    return ofertas