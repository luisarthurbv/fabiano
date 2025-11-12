import asyncio
from decimal import Decimal
import os
import re
import sys
import pytest
from playwright.async_api import async_playwright

# Ensure project root is importable
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from model import Oferta
import caixa


@pytest.mark.asyncio
async def test_parse_ofertas_from_static_html():
    html_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources", "caixa.html")
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # Load the static HTML content
        await page.set_content(html, wait_until="domcontentloaded")

        ofertas = await caixa._parse_ofertas_from_page("SP", "RIBEIRAO PRETO", page)

        # Count result items via DOM
        total_items = await page.locator("li.group-block-item").count()

        # We should parse at least one item and match the number of items present
        assert isinstance(ofertas, list)
        assert len(ofertas) > 0
        assert len(ofertas) == total_items
        assert all(isinstance(o, Oferta) for o in ofertas)

        # Validate the first item matches the provided example
        first = ofertas[0]
        assert first.title == "RIBEIRAO PRETO - LAR GRECIA"
        assert first.avaliacao == Decimal("190000.00")
        assert first.valor == Decimal("114838.57")
        assert first.descricao.startswith("Apartamento - 95,08 m2, 2 quarto(s), 1 vaga(s) na garagem - Venda Direta Online")
        assert first.numero == "8787711568638"
        def _norm(s: str) -> str:
            import re as _re
            return _re.sub(r"\s+", " ", s).strip()
        assert _norm(first.endereco).startswith(_norm("RUA ALFREDO PUCCI,N. 80 Apto. 22 BL A TORRE 2,  , BONFIM PAULISTA"))

        await context.close()
        await browser.close()


@pytest.mark.asyncio
async def test_parse_all_items_have_minimum_fields():
    html_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources", "caixa.html")
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        await page.set_content(html, wait_until="domcontentloaded")
        ofertas = await caixa._parse_ofertas_from_page("SP", "RIBEIRAO PRETO", page)

        # Count result items via DOM
        total_items = await page.locator("li.group-block-item").count()
        assert len(ofertas) == total_items

        # All items should have non-empty title and descricao; other fields may occasionally be blank
        for o in ofertas:
            assert o.title != ""
            assert o.descricao != ""

        await context.close()
        await browser.close()
