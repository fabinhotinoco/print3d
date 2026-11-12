# 001 — Dado d10 com nomes

Dado de 10 lados (trapezoedro pentagonal), ~41 mm, com os 10 textos das imagens de referência
gravados a 0.8 mm de profundidade. Textos editáveis em `NAMES_TOP` / `NAMES_BOTTOM` no `model.py`.

| Metade de cima | Metade de baixo |
|---|---|
| Oruam · 50 Cent · Repetir Baseado · Pausa p/ baseado · Another Joint | TZ · BTT · LT · MCJunin · GELLATO |

## Impressão
- O 3MF já vem **deitado sobre a face "TZ"** → **sem suportes** (overhang máx. 37°).
- PLA Bambu Basic, 0.20 mm (ou 0.12 mm para texto mais nítido), 3 paredes, **infill ≥ 30%** (peso e equilíbrio).
- ~10 g a 15% infill.
- **Contraste do texto**: impresso em uma cor, o texto fica só em baixo-relevo. Para o visual das
  referências (texto claro em dado preto): passe tinta acrílica clara e limpe o excesso com pano úmido,
  ou use `out/texto.stl` como peça de outra cor se tiver AMS.

## Duas cores (AMS)
`out/dado-d10-cantores-2cores.3mf` = 1 objeto com 2 partes: **dado → filamento 1**, **nomes → filamento 2**.
Os nomes preenchem o rebaixo de 0.8 mm e ficam rentes à face (incrustação).

Custo da troca de cor (estimativa, conferir no fatiamento): quase toda camada tem texto → ~2 trocas por camada,
~140 camadas a 0.20 mm. Com AMS lite isso significa **muito purga e várias horas**. Para amortizar:
- imprimir **vários dados no mesmo prato** (a purga por camada é a mesma para 1 ou 8 dados);
- ativar *Flush into objects' infill* e usar infill ≥ 30%;
- preferir texto escuro em dado claro, se a estética permitir (trocas claro→escuro purgam menos).

## Arquivos
- `out/dado-d10-cantores-2cores.3mf` — duas cores (AMS)
- `out/dado-d10-cantores.3mf` — uma cor (texto em baixo-relevo)
- `out/dado-d10-cantores-render.png` — prévia (topo, base, perspectiva)
- `out/texto.stl` — só as letras (para pintura por cor / AMS)

## Histórico de impressões
| Data | Impressora | Config | Resultado |
|---|---|---|---|
