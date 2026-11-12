"""Carrega impressoras/materiais e valida se a peça cabe."""
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
PRINTERS = yaml.safe_load((ROOT / "config/printers.yaml").read_text())
MATERIALS = yaml.safe_load((ROOT / "config/materials.yaml").read_text())
PLA = MATERIALS["PLA_BAMBU_BASIC"]


def fits(bbox_mm, printer: str) -> bool:
    """True se a caixa (x, y, z) cabe na impressora em alguma rotação no plano XY."""
    bx, by, bz = PRINTERS[printer]["build_volume"]
    x, y, z = bbox_mm
    return z <= bz and ((x <= bx and y <= by) or (y <= bx and x <= by))
