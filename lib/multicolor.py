"""3MF multicor no formato do BambuStudio: 1 objeto com N partes, cada parte com seu filamento.

Estrutura (igual à que o BambuStudio grava):
  3D/3dmodel.model            → objeto "montagem" com <components> apontando para as malhas
  3D/Objects/object_1.model   → malhas de cada parte
  Metadata/model_settings.config → nome e filamento (extruder) de cada parte
Abrindo no BambuStudio, cada parte já vem com o filamento atribuído (slot 1, 2, ... do AMS).
"""
from __future__ import annotations

import uuid
import zipfile
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import trimesh

NS = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
NS_P = "http://schemas.microsoft.com/3dmanufacturing/production/2015/06"
NS_BBS = "http://schemas.bambulab.com/package/2021"
IDENTITY = "1 0 0 0 1 0 0 0 1 0 0 0"


@dataclass
class Part:
    name: str
    mesh: trimesh.Trimesh
    filament: int  # 1-based: slot do AMS / filamento no BambuStudio


def _mesh_xml(obj_id: int, m: trimesh.Trimesh) -> str:
    v = "\n".join(f'<vertex x="{x:.4f}" y="{y:.4f}" z="{z:.4f}"/>' for x, y, z in m.vertices)
    t = "\n".join(f'<triangle v1="{a}" v2="{b}" v3="{c}"/>' for a, b, c in m.faces)
    return (f'<object id="{obj_id}" p:UUID="{uuid.uuid4()}" type="model">'
            f"<mesh><vertices>\n{v}\n</vertices><triangles>\n{t}\n</triangles></mesh></object>")


def write_3mf(path: Path, name: str, parts: list[Part], bed_center=(128.0, 128.0)) -> None:
    """Grava um 3MF com um objeto multi-parte, centrado na mesa e apoiado em z=0."""
    lo = np.min([p.mesh.bounds[0] for p in parts], axis=0)
    hi = np.max([p.mesh.bounds[1] for p in parts], axis=0)
    # posiciona: centro XY na mesa, base em z=0
    tx, ty = bed_center[0] - (lo[0] + hi[0]) / 2, bed_center[1] - (lo[1] + hi[1]) / 2
    tz = -lo[2]
    asm_id = len(parts) + 1

    objects = "\n".join(_mesh_xml(i + 1, p.mesh) for i, p in enumerate(parts))
    sub_model = (f'<?xml version="1.0" encoding="UTF-8"?>\n'
                 f'<model unit="millimeter" xml:lang="en-US" xmlns="{NS}" xmlns:p="{NS_P}" requiredextensions="p">'
                 f"<resources>{objects}</resources><build/></model>")

    comps = "".join(f'<component p:path="/3D/Objects/object_1.model" objectid="{i + 1}" '
                    f'p:UUID="{uuid.uuid4()}" transform="{IDENTITY}"/>' for i in range(len(parts)))
    root_model = (f'<?xml version="1.0" encoding="UTF-8"?>\n'
                  f'<model unit="millimeter" xml:lang="en-US" xmlns="{NS}" xmlns:p="{NS_P}" '
                  f'xmlns:BambuStudio="{NS_BBS}" requiredextensions="p">'
                  f'<metadata name="BambuStudio:3mfVersion">1</metadata>'
                  f'<metadata name="Title">{name}</metadata>'
                  f'<resources><object id="{asm_id}" p:UUID="{uuid.uuid4()}" type="model">'
                  f"<components>{comps}</components></object></resources>"
                  f'<build p:UUID="{uuid.uuid4()}"><item objectid="{asm_id}" p:UUID="{uuid.uuid4()}" '
                  f'transform="1 0 0 0 1 0 0 0 1 {tx:.4f} {ty:.4f} {tz:.4f}" printable="1"/></build></model>')

    part_cfg = "".join(
        f'<part id="{i + 1}" subtype="normal_part">'
        f'<metadata key="name" value="{p.name}"/>'
        f'<metadata key="matrix" value="1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1"/>'
        f'<metadata key="extruder" value="{p.filament}"/></part>'
        for i, p in enumerate(parts))
    settings = (f'<?xml version="1.0" encoding="UTF-8"?>\n<config><object id="{asm_id}">'
                f'<metadata key="name" value="{name}"/><metadata key="extruder" value="{parts[0].filament}"/>'
                f"{part_cfg}</object></config>")

    content_types = ('<?xml version="1.0" encoding="UTF-8"?>\n'
                     '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                     '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
                     '<Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>'
                     '<Default Extension="config" ContentType="text/xml"/></Types>')
    rels = ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Target="/3D/3dmodel.model" Id="rel-1" '
            'Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
    model_rels = ('<?xml version="1.0" encoding="UTF-8"?>\n'
                  '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                  '<Relationship Target="/3D/Objects/object_1.model" Id="rel-1" '
                  'Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')

    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", content_types)
        z.writestr("_rels/.rels", rels)
        z.writestr("3D/3dmodel.model", root_model)
        z.writestr("3D/_rels/3dmodel.model.rels", model_rels)
        z.writestr("3D/Objects/object_1.model", sub_model)
        z.writestr("Metadata/model_settings.config", settings)
