# Artefatos de evidência

- `gate-report.json`: resultados locais de compileall e pytest e SHA-256 dos fontes. Automático.
- `desktop-preview.png` e `mobile-preview.png`: screenshots *visuais* com dados simulados no browser, **não** end-to-end HTTP.
- `preview-notes.md`: metodologia e limites das capturas.
- `independent-review-template.md`: formulário NÃO EXECUTADO para validação independente no Antigravity.

Há três classes de evidência deliberadamente distintas: **executado e aprovado localmente**, **inspecionado visualmente com mock**, e **não executado/pendente**. Não agregar as três em um único PASS.
