# Proveniência das capturas visuais

As imagens `desktop-preview.png` e `mobile-preview.png` foram geradas em 03/11/2026 com Chromium headless, carregando os arquivos HTML, CSS e JS **reais do projeto**, mas substituindo as respostas HTTP por um catálogo estático de teste no navegador. O ambiente não permitiu navegação local ao servidor HTTP via Chromium (`ERR_BLOCKED_BY_ADMINISTRATOR`), razão pela qual **não se trata de um teste end-to-end de rede**. As interações básicas de catálogo e carrinho foram verificadas no navegador mockado; a API e as transações reais foram testadas separadamente via `pytest/TestClient`.

Para reproduzir as imagens em um ambiente com Playwright e Chromium instalados:

```bash
python scripts/render_offline_preview.py
```

O teste de navegação E2E com servidor real, acessibilidade automatizada e auditoria DAST continuam pendentes.
