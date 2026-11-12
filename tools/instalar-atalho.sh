#!/bin/bash
# Instala (uma única vez) a pasta "Impressão 3D" na Mesa, com um botão "↻ Atualizar".
# Uso:  bash ~/print3d/tools/instalar-atalho.sh
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
DEST="$HOME/Desktop/Impressão 3D"
mkdir -p "$DEST"

# Botão de duplo clique: só chama o script do repositório, então melhorias chegam via git pull
cat > "$DEST/↻ Atualizar.command" <<CMD
#!/bin/bash
"$REPO/tools/atualizar-mesa.sh"
CMD
chmod +x "$DEST/↻ Atualizar.command" "$REPO/tools/atualizar-mesa.sh"

"$REPO/tools/atualizar-mesa.sh"
