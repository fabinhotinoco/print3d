"""001 — Dado de 10 lados (trapezoedro pentagonal) com nomes gravados.

Geometria: 2 ápices + anel de 10 vértices em zigue-zague. Para as faces (pipas)
serem planas:  H = c·(1+cos36°)/(1−cos36°)  (H = altura do ápice, c = zigue-zague).
Texto: tangencial à face, topo das letras apontando para a borda (como nas referências).
"""
import sys
from math import cos, sin, radians, pi
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from build123d import *
from lib.export import build, mesh_of
from lib.multicolor import Part, write_3mf

# ───── Parâmetros ─────────────────────────────────────────────────────────────
NAMES_TOP = ["Oruam", "50 Cent", "Repetir\nBaseado", "Pausa p/\nbaseado", "Another\nJoint"]
NAMES_BOTTOM = ["TZ", "BTT", "LT", "MCJunin", "GELLATO"]
RADIUS = 21.0            # raio do anel (mm) → dado ~42 mm de largura
ZIGZAG = 2.2             # meia-altura do zigue-zague (mm)
ENGRAVE = 0.8            # profundidade do texto (mm)
MARGIN = 1.8             # distância mínima do texto às arestas (mm)
MAX_FONT = 8.0           # limite de tamanho da fonte (mm)
EDGE_FILLET = 0.8        # arredondamento das arestas (mm)
BED_FACE = 5             # índice da face apoiada na mesa (5 = "TZ"): sem suportes, overhang máx. 37°
FONT = str(ROOT / "assets/fonts/Inter-Bold.otf")
# ──────────────────────────────────────────────────────────────────────────────

C36 = cos(radians(36))
APEX = ZIGZAG * (1 + C36) / (1 - C36)


def ring(k: int) -> Vector:
    a = 2 * pi * k / 10
    return Vector(RADIUS * cos(a), RADIUS * sin(a), ZIGZAG if k % 2 == 0 else -ZIGZAG)


def kites():
    """10 faces: (vértices em ordem, ápice, vértice oposto ao ápice)."""
    top, bot = Vector(0, 0, APEX), Vector(0, 0, -APEX)
    out = []
    for i in range(5):
        k = 2 * i
        out.append(([top, ring(k), ring(k + 1), ring(k + 2)], top, ring(k + 1)))
    for i in range(5):
        k = 2 * i + 1
        out.append(([bot, ring(k + 2), ring(k + 1), ring(k)], bot, ring(k + 1)))
    return out


def body() -> Solid:
    faces = [Face(Wire.make_polygon(v, close=True)) for v, _, _ in kites()]
    solid = Solid(Shell(faces))
    try:
        return solid.fillet(EDGE_FILLET, solid.edges())
    except Exception:
        return solid


def text_on_face(label: str, verts, apex: Vector, foot: Vector):
    """Gera o sólido do texto (para subtrair) encaixado na pipa com margem."""
    center = sum(verts, Vector()) * 0.25
    normal = (verts[1] - verts[0]).cross(verts[3] - verts[0]).normalized()
    if normal.dot(center) < 0:
        normal = -normal
    up = (foot - apex)
    up = (up - normal * up.dot(normal)).normalized()          # topo das letras → borda (como nas referências)
    xdir = up.cross(normal).normalized()                     # leitura da esquerda p/ direita
    # polígono da face em coordenadas 2D (x = tangente, y = rumo ao ápice)
    poly = [((v - foot).dot(xdir), (v - foot).dot(up)) for v in verts]
    side_y = poly[1][1]                                       # linha mais larga (vértices laterais)

    def inside(px, py):
        # ponto dentro da pipa com margem: distância a cada aresta ≥ MARGIN
        n = len(poly)
        for i in range(n):
            (x1, y1), (x2, y2) = poly[i], poly[(i + 1) % n]
            ex, ey = x2 - x1, y2 - y1
            L = (ex * ex + ey * ey) ** 0.5
            cross = (ex * (py - y1) - ey * (px - x1)) / L
            if cross * orient < MARGIN:
                return False
        return True

    xs, ys = zip(*poly)
    orient = 1 if sum(xs[i] * ys[(i + 1) % 4] - xs[(i + 1) % 4] * ys[i] for i in range(4)) > 0 else -1

    best = None
    for size in [MAX_FONT - 0.25 * i for i in range(int((MAX_FONT - 2) / 0.25))]:
        sk = Text(label, font_size=size, font_path=FONT, align=(Align.CENTER, Align.CENTER))
        bb = sk.bounding_box()
        w, h = bb.size.X, bb.size.Y
        y_lo, y_hi = min(ys), max(ys)
        for cy in [y_lo + 0.25 * j for j in range(int((y_hi - y_lo) / 0.25))]:
            corners = [(sx * w / 2, cy + sy * h / 2) for sx in (-1, 1) for sy in (-1, 1)]
            if all(inside(px, py) for px, py in corners):
                best = (size, cy, sk)
                break
        if best:
            break
    if best is None:
        raise ValueError(f"Texto não cabe na face: {label!r}")
    size, cy, sk = best
    origin = foot + up * cy
    plane = Plane(origin=origin, x_dir=xdir, z_dir=normal)
    tool = extrude(plane * sk, amount=2.0, both=True)          # atravessa a superfície
    # mantém só a parte até ENGRAVE abaixo da face
    keep = Box(200, 200, ENGRAVE * 2)
    keep = plane * keep
    print(f"  {label!r:22} fonte {size:.2f} mm")
    return tool & keep


def make_die():
    """Retorna (dado gravado, texto) — o texto serve para prévia colorida / AMS."""
    die = body()
    labels = NAMES_TOP + NAMES_BOTTOM
    text = None
    for label, (verts, apex, foot) in zip(labels, kites()):
        t = text_on_face(label, verts, apex, foot) & die
        text = t if text is None else text + t
    return die - text, text


def lay_on_face(shapes, index: int):
    """Gira para a face `index` ficar na mesa (normal → −Z) e apoia em z = 0."""
    verts, _, _ = kites()[index]
    n = (verts[1] - verts[0]).cross(verts[3] - verts[0]).normalized()
    if n.dot(sum(verts, Vector())) < 0:
        n = -n
    plane = Plane(origin=(0, 0, 0), z_dir=-n)
    moved = [plane.to_local_coords(s) for s in shapes]
    z0 = moved[0].bounding_box().min.Z
    return [m.moved(Location((0, 0, -z0))) for m in moved]


if __name__ == "__main__":
    die, text = lay_on_face(make_die(), BED_FACE)
    here = Path(__file__).parent
    build(die, here, "dado-d10-cantores")                    # 1 cor (texto em baixo-relevo)
    out = here / "out"
    die_mesh = mesh_of(die, out / "dado-d10-cantores.stl")
    text_mesh = mesh_of(text, out / "texto.stl")
    write_3mf(out / "dado-d10-cantores-2cores.3mf", "dado-d10-cantores", [
        Part("dado", die_mesh, filament=1),                   # slot 1 do AMS: cor do dado
        Part("nomes", text_mesh, filament=2),                 # slot 2 do AMS: cor dos nomes
    ])
