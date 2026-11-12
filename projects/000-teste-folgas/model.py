"""000 — Teste de folgas (PLA Bambu Basic, bico 0.4).

Imprima nas DUAS impressoras. Encaixe o pino em cada furo e anote:
  - menor folga em que o pino ENTRA com pressão  -> press_fit
  - menor folga em que GIRA livre sem jogo         -> slip_fit
Depois atualizamos config/materials.yaml com os valores reais.
"""
import sys; from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from build123d import *
from lib.export import build

PIN_D = 8.0
CLEARANCES = [0.00, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40]  # folga radial por lado
PITCH, T = 13.0, 6.0
L, W = PITCH * len(CLEARANCES) + 4, 24.0

with BuildPart() as plate:
    Box(L, W, T, align=(Align.CENTER, Align.CENTER, Align.MIN))
    fillet(plate.edges().filter_by(Axis.Z), 3)
    chamfer(plate.edges().group_by(Axis.Z)[0], 0.4)
    for i, c in enumerate(CLEARANCES):
        x = (i - (len(CLEARANCES) - 1) / 2) * PITCH
        with Locations(Pos(x, -3, 0)):
            Cylinder((PIN_D + 2 * c) / 2, T, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)
        with BuildSketch(Plane.XY.offset(T)) as s:
            with Locations((x, 7.5)):
                Text(f"{c:.2f}".lstrip("0"), font_size=3.6, align=(Align.CENTER, Align.CENTER))
        extrude(amount=-0.6, mode=Mode.SUBTRACT)

with BuildPart() as pin:
    Cylinder(PIN_D / 2, 12, align=(Align.CENTER, Align.CENTER, Align.MIN))
    chamfer(pin.edges().group_by(Axis.Z)[-1], 0.6)      # entrada
    chamfer(pin.edges().group_by(Axis.Z)[0], 0.3)       # anti pé-de-elefante
    with Locations(Pos(0, 0, 0)):
        Box(18, 5, 2.4, align=(Align.CENTER, Align.CENTER, Align.MIN))  # aba de pegada/estabilidade

here = Path(__file__).parent
build(Compound([plate.part, pin.part.moved(Location((0, 22, 0)))]), here, "teste-folgas")
