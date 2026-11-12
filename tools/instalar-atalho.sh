#!/bin/bash
# Instala (uma vez):
#   - define a pasta de destino dos projetos (padrão: iCloud Drive › Documentos › 3D)
#   - coloca o botão "↻ Atualizar 3D" na Mesa
#   - remove a antiga pasta "Impressão 3D" da Mesa (só se tiver apenas atalhos criados por nós)
# Uso:  bash tools/instalar-atalho.sh  [caminho/da/pasta/destino]
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
CONFIG="$HOME/.print3d-destino"
ICLOUD="$HOME/Library/Mobile Documents/com~apple~CloudDocs"

if [ $# -ge 1 ]; then
  DEST="$1"
else
  DEST=""
  for d in "$ICLOUD/Documentos/3D" "$HOME/Documents/3D" "$ICLOUD/Documents/3D"; do
    if [ -d "$d" ]; then DEST="$d"; break; fi
  done
  DEST="${DEST:-$HOME/Documents/3D}"
fi
mkdir -p "$DEST"
echo "$DEST" > "$CONFIG"
echo "Pasta dos projetos: $DEST"

# Botão na Mesa
mkdir -p "$HOME/Desktop"
BTN="$HOME/Desktop/↻ Atualizar 3D.command"
cat > "$BTN" <<CMD
#!/bin/bash
"$REPO/tools/atualizar-mesa.sh"
CMD
chmod +x "$BTN" "$REPO/tools/atualizar-mesa.sh"

# Limpa a versão antiga (pasta de atalhos na Mesa), sem tocar em arquivos reais
OLD="$HOME/Desktop/Impressão 3D"
if [ -d "$OLD" ]; then
  find "$OLD" -maxdepth 1 -type l -delete
  rm -f "$OLD/↻ Atualizar.command"
  rmdir "$OLD" 2>/dev/null && echo "Pasta antiga 'Impressão 3D' removida da Mesa." \
    || echo "Pasta antiga 'Impressão 3D' mantida (tem arquivos seus dentro)."
fi

"$REPO/tools/atualizar-mesa.sh"
