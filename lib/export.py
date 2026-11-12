"""Exporta STEP/STL/3MF + prévia + relatório para out/ do projeto.

Fluxo: B-rep (STEP, fonte de verdade) → malha → reparo (solda microfuros da
triangulação) → validação (malha fechada é obrigatória) → STL/3MF → prévia.
"""
from pathlib import Path

import trimesh
from build123d import export_step, export_stl

from .render import render_preview
from .spec import PLA, PRINTERS, fits

# Tolerâncias de triangulação: 0.01 mm é bem abaixo da resolução da impressora
# e evita STLs gigantes (a padrão gera ~10× mais triângulos sem ganho visível).
LINEAR_TOL = 0.01
ANGULAR_TOL = 0.2


def mesh_of(part, stl_path: Path) -> trimesh.Trimesh:
    """Triangula, repara e valida. Levanta erro se a malha não fechar."""
    export_stl(part, str(stl_path), tolerance=LINEAR_TOL, angular_tolerance=ANGULAR_TOL)
    m = trimesh.load(stl_path)
    if not m.is_watertight:
        m.merge_vertices(digits_vertex=3)
        m.update_faces(m.nondegenerate_faces())
        trimesh.repair.fill_holes(m)
        trimesh.repair.fix_normals(m)
    if not m.is_watertight:
        raise RuntimeError(f"Malha não fechada após reparo: {stl_path.name}")
    m.export(stl_path)
    return m


def build(part, project_dir: str | Path, name: str, infill: float = 0.15) -> dict:
    out = Path(project_dir) / "out"
    out.mkdir(exist_ok=True)
    export_step(part, str(out / f"{name}.step"))
    m = mesh_of(part, out / f"{name}.stl")
    m.export(out / f"{name}.3mf")

    size = tuple(m.extents)
    # estimativa grosseira: casca sólida ~35% + infill no resto
    grams = m.volume / 1000 * PLA["density_g_cm3"] * (0.35 + 0.65 * infill)
    report = {
        "name": name,
        "size_mm": [round(float(v), 1) for v in size],
        "grams_est": round(float(grams), 1),
        "triangles": len(m.faces),
        "watertight": bool(m.is_watertight),
        "fits": {p: fits(size, p) for p in PRINTERS},
    }
    render_preview(out / f"{name}.stl", out / f"{name}.png", report)
    print(report)
    return report
