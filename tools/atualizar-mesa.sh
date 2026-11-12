#!/bin/bash
# Atualiza a pasta "Impressão 3D" da Mesa com os arquivos prontos para imprimir.
#  1. baixa as novidades do GitHub (git pull)
#  2. recria os atalhos para cada .3mf (e a prévia .png) de projects/*/out/
#  3. abre a pasta no Finder
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
DEST="$HOME/Desktop/Impressão 3D"
mkdir -p "$DEST"

echo "→ Buscando novidades no GitHub…"
git -C "$REPO" pull --ff-only --quiet || echo "  (sem conexão ou alterações locais — usando a versão atual)"

# Remove só atalhos antigos (nunca apaga arquivos reais que você colocou na pasta)
find "$DEST" -maxdepth 1 -type l -delete

count=0
for f in "$REPO"/projects/*/out/*.3mf "$REPO"/projects/*/out/*.png; do
  [ -e "$f" ] || continue
  project="$(basename "$(dirname "$(dirname "$f")")")"   # ex.: 000-teste-folgas
  ln -s "$f" "$DEST/$project — $(basename "$f")"
  if [[ "$f" == *.3mf ]]; then count=$((count + 1)); fi
done

echo "✓ $count arquivo(s) prontos para imprimir em: $DEST"
if [ "$(uname)" = "Darwin" ]; then open "$DEST"; fi
