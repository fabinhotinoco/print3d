"""Prévia estática em 3 vistas (perspectiva / frontal / topo)."""
import numpy as np, trimesh, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

COLOR = np.array([0.13, 0.42, 0.95])


def render_preview(stl_path, png_path, report=None):
    m = trimesh.load(stl_path)
    light = np.array([0.4, -0.6, 0.8]); light /= np.linalg.norm(light)
    shade = 0.35 + 0.65 * np.clip(m.face_normals @ light, 0, 1)
    colors = np.c_[np.outer(shade, COLOR), np.ones(len(shade))]
    fig = plt.figure(figsize=(12, 5), dpi=160, facecolor="#f5f5f7")
    b = m.bounds; c = b.mean(0); r = (b[1] - b[0]).max() / 2
    for k, (el, az, title) in enumerate([(28, -55, "Perspectiva"), (0, -90, "Frontal"), (90, -90, "Topo")]):
        ax = fig.add_subplot(1, 3, k + 1, projection="3d"); ax.set_facecolor("#f5f5f7")
        ax.add_collection3d(Poly3DCollection(m.triangles, facecolors=colors, edgecolor="none"))
        ax.set_xlim(c[0]-r, c[0]+r); ax.set_ylim(c[1]-r, c[1]+r); ax.set_zlim(c[2]-r, c[2]+r)
        ax.view_init(el, az); ax.set_box_aspect((1, 1, 1)); ax.axis("off"); ax.set_title(title, color="#333")
    s = report["size_mm"] if report else (b[1] - b[0]).round(1).tolist()
    sub = f"{s[0]:g} × {s[1]:g} × {s[2]:g} mm · fechada={m.is_watertight}"
    if report:
        sub += f" · ~{report['grams_est']} g PLA · " + " ".join(f"{p}:{'ok' if v else 'NÃO CABE'}" for p, v in report["fits"].items())
    fig.suptitle(sub, color="#555")
    plt.tight_layout(); plt.savefig(png_path, facecolor=fig.get_facecolor()); plt.close(fig)
