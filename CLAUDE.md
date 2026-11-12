# print3d — regras do projeto

- Impressoras: Bambu Lab A1 (256³) e A2L (330×320×325), bico 0.4. Material padrão: PLA Bambu Basic.
- Todo projeto vive em `projects/NNN-nome/` com: `model.py` (fonte paramétrica, build123d),
  `README.md` (objetivo, orientação, suportes, folgas, histórico de impressões) e `out/` (STEP/STL/3MF/PNG gerados).
- Parâmetros no topo do `model.py`; folgas e limites vêm de `config/materials.yaml` (nunca números mágicos).
- Sempre gerar com `lib.export.build()` — valida malha fechada e se cabe em cada impressora.
- Regras de projeto PLA: parede ≥1.2 mm, overhang ≤50°, ponte ≤30 mm, chanfro 0.4 mm na base.
- Encaixes: usar `clearance` de `config/materials.yaml` (medido: .05 pressão forte, .10 pressão, .15 folgado).
- Após cada impressão real, registrar o resultado no README do projeto e, se for o caso, ajustar `config/`.
