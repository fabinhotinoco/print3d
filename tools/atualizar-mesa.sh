#!/bin/bash
# Baixa as novidades do GitHub e COPIA os arquivos prontos para imprimir para a pasta 3D
# do iCloud Drive (iCloud Drive › Documentos › 3D), uma subpasta por projeto:
#     3D/001-dado-d10-cantores/dado-d10-cantores-2cores.3mf
# Seguro: nunca apaga nada da pasta 3D e não sobrescreve arquivos que você salvou depois.
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
CONFIG="$HOME/.print3d-destino"   # caminho da pasta de destino (gravado pelo instalador)

find_dest() {
  if [ -f "$CONFIG" ]; then cat "$CONFIG"; return; fi
  local icloud="$HOME/Library/Mobile Documents/com~apple~CloudDocs"
  for d in "$icloud/Documentos/3D" "$HOME/Documents/3D" "$icloud/Documents/3D"; do
    if [ -d "$d" ]; then echo "$d"; return; fi
  done
  echo "$HOME/Documents/3D"        # fallback: cria em Documentos
}

DEST="$(find_dest)"
mkdir -p "$DEST"

echo "→ Buscando novidades no GitHub…"
git -C "$REPO" pull --ff-only --quiet || echo "  (sem conexão ou alterações locais — usando a versão atual)"

copied=0
for f in "$REPO"/projects/*/out/*.3mf "$REPO"/projects/*/out/*.png; do
  [ -e "$f" ] || continue
  project="$(basename "$(dirname "$(dirname "$f")")")"   # ex.: 001-dado-d10-cantores
  mkdir -p "$DEST/$project"
  target="$DEST/$project/$(basename "$f")"
  # copia se não existe, ou se a versão do GitHub é mais nova (não sobrescreve
  # um arquivo que você salvou depois — ex.: projeto já fatiado no BambuStudio)
  if [ ! -e "$target" ] || { [ "$f" -nt "$target" ] && ! cmp -s "$f" "$target"; }; then
    cp "$f" "$target"
    echo "  ✓ $project/$(basename "$f")"
    copied=$((copied + 1))
  fi
done

echo "✓ $copied arquivo(s) novo(s)/atualizado(s) em: $DEST"
if [ "$(uname)" = "Darwin" ]; then open "$DEST"; fi
