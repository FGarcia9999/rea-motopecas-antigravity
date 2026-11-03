"""Catálogo fictício e compatibilidades ilustrativas — NÃO validadas por fabricante."""

BIKES = [
    {"id": "honda-cg-160", "name": "Honda CG 160", "years": [2018, 2024]},
    {"id": "honda-biz-125", "name": "Honda Biz 125", "years": [2018, 2024]},
    {"id": "honda-bros-160", "name": "Honda NXR Bros 160", "years": [2018, 2024]},
    {"id": "yamaha-fazer-250", "name": "Yamaha Fazer 250", "years": [2018, 2024]},
    {"id": "yamaha-factor-150", "name": "Yamaha Factor 150", "years": [2018, 2024]},
    {"id": "honda-pcx-150", "name": "Honda PCX 150", "years": [2018, 2020]},
]

# Os valores e a aplicação dos produtos são exclusivamente demonstrativos.
PRODUCTS = [
    ("R2-FR-001", "Pastilha de freio dianteira", "Freios", "freio", 4590, 20, "Conjunto de pastilhas para manutenção preventiva.", ["honda-cg-160", "honda-bros-160"]),
    ("R2-FR-002", "Lona de freio traseira", "Freios", "freio", 2990, 18, "Jogo de lonas de freio para uso urbano.", ["honda-biz-125", "yamaha-factor-150"]),
    ("R2-TR-003", "Kit transmissão 428H", "Transmissão", "transmissao", 14990, 14, "Kit com corrente, coroa e pinhão.", ["honda-cg-160", "yamaha-factor-150"]),
    ("R2-TR-004", "Corrente de transmissão reforçada", "Transmissão", "transmissao", 8990, 10, "Corrente para reposição no conjunto de tração.", ["honda-bros-160", "yamaha-fazer-250"]),
    ("R2-FI-005", "Filtro de ar para revisão", "Filtros", "filtro", 3490, 28, "Elemento filtrante de ar para rotina de manutenção.", ["honda-cg-160", "honda-bros-160"]),
    ("R2-FI-006", "Filtro de óleo cartucho", "Filtros", "filtro", 2490, 22, "Filtro de óleo de reposição para motores compatíveis.", ["yamaha-fazer-250", "honda-pcx-150"]),
    ("R2-MO-007", "Óleo para motor 4T 10W-30", "Lubrificantes", "oleo", 4990, 32, "Frasco demonstrativo 1 L; consulte o manual da moto.", ["honda-cg-160", "honda-biz-125", "honda-bros-160"]),
    ("R2-MO-008", "Óleo para motor 4T 20W-50", "Lubrificantes", "oleo", 4290, 24, "Frasco demonstrativo 1 L; especificação a confirmar.", ["yamaha-factor-150", "yamaha-fazer-250"]),
    ("R2-EL-009", "Vela de ignição padrão", "Elétrica", "vela", 1990, 40, "Vela de ignição para manutenção programada.", ["honda-cg-160", "honda-biz-125", "yamaha-factor-150"]),
    ("R2-EL-010", "Lâmpada de farol H4", "Elétrica", "lampada", 3990, 16, "Lâmpada de reposição para o sistema de iluminação.", ["honda-bros-160", "yamaha-fazer-250"]),
    ("R2-SU-011", "Retentor de suspensão dianteira", "Suspensão", "suspensao", 5490, 15, "Par de retentores para manutenção da suspensão.", ["honda-cg-160", "honda-bros-160"]),
    ("R2-SU-012", "Amortecedor traseiro", "Suspensão", "suspensao", 25990, 8, "Unidade de amortecimento de reposição.", ["honda-biz-125", "honda-pcx-150"]),
]
