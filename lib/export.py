"""Exporta STEP/STL/3MF + prévia + relatório para out/ do projeto."""
from pathlib import Path
from build123d import Mesher, export_step, export_stl
from .spec import PLA, PRINTERS, fits
from .render import render_preview


def build(part, project_dir: str | Path, name: str, infill: float = 0.15) -> dict:
    out = Path(project_dir) / "out"
    out.mkdir(exist_ok=True)
    export_step(part, str(out / f"{name}.step"))
    export_stl(part, str(out / f"{name}.stl"))
    m = Mesher(); m.add_shape(part); m.write(str(out / f"{name}.3mf"))

    bb = part.bounding_box()
    size = (bb.size.X, bb.size.Y, bb.size.Z)
    # estimativa grosseira: casca sólida ~35% + infill no resto
    grams = part.volume / 1000 * PLA["density_g_cm3"] * (0.35 + 0.65 * infill)
    report = {
        "name": name,
        "size_mm": [round(v, 1) for v in size],
        "grams_est": round(grams, 1),
        "fits": {p: fits(size, p) for p in PRINTERS},
    }
    render_preview(out / f"{name}.stl", out / f"{name}.png", report)
    print(report)
    return report
