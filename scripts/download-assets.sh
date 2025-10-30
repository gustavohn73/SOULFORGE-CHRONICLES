#!/bin/bash

set -e  # Exit on error

echo "🎨 =========================================="
echo "   SOULFORGE CHRONICLES - ASSET DOWNLOADER"
echo "=========================================="
echo ""

# Verificar dependências
command -v wget >/dev/null 2>&1 || command -v curl >/dev/null 2>&1 || {
    echo "❌ Erro: wget ou curl não encontrado"
    echo "   Instale com: sudo apt install wget  (Linux)"
    echo "   ou: brew install wget  (Mac)"
    exit 1
}

command -v unzip >/dev/null 2>&1 || {
    echo "❌ Erro: unzip não encontrado"
    echo "   Instale com: sudo apt install unzip  (Linux)"
    echo "   ou: brew install unzip  (Mac)"
    exit 1
}

# Diretórios
ASSETS_DIR="client/assets"
TEMP_DIR="/tmp/soulforge-assets"
SPRITES_DIR="$ASSETS_DIR/sprites"
TILESETS_DIR="$ASSETS_DIR/tilesets"
UI_DIR="$ASSETS_DIR/ui"

# Criar diretórios
echo "📁 Criando estrutura de diretórios..."
mkdir -p "$SPRITES_DIR"/{characters,enemies,items}
mkdir -p "$TILESETS_DIR"
mkdir -p "$UI_DIR"
mkdir -p "$TEMP_DIR"

# Função para download
download_file() {
    local url=$1
    local output=$2

    echo "   Baixando: $(basename $output)"

    if command -v wget >/dev/null 2>&1; then
        wget -q --show-progress "$url" -O "$output"
    else
        curl -L --progress-bar "$url" -o "$output"
    fi
}

echo ""
echo "📥 Baixando assets do Kenney.nl..."
echo "   (Assets gratuitos CC0 - domínio público)"
echo ""

# 1. MICRO ROGUELIKE (Tiles 16x16)
echo "1️⃣  Micro Roguelike Pack..."
download_file \
    "https://kenney.nl/content/3-assets/50-micro-roguelike/microroguelike.zip" \
    "$TEMP_DIR/microroguelike.zip"

echo "   Extraindo tiles..."
unzip -q "$TEMP_DIR/microroguelike.zip" -d "$TEMP_DIR/tiles"
cp "$TEMP_DIR/tiles/Tilemap/colored_packed.png" "$TILESETS_DIR/dungeon_colored.png" 2>/dev/null || \
cp "$TEMP_DIR/tiles/Tilemap/"*.png "$TILESETS_DIR/" 2>/dev/null || true

# Copiar sprites individuais
if [ -d "$TEMP_DIR/tiles/Tiles" ]; then
    cp "$TEMP_DIR/tiles/Tiles/"*.png "$SPRITES_DIR/" 2>/dev/null || true
fi

echo "   ✅ Tiles de dungeon instalados"

# 2. 1-BIT PACK (Minimalista, perfeito para placeholder)
echo ""
echo "2️⃣  1-Bit Pack..."
download_file \
    "https://kenney.nl/content/3-assets/46-bit-pack/bitpack.zip" \
    "$TEMP_DIR/bitpack.zip"

echo "   Extraindo sprites..."
unzip -q "$TEMP_DIR/bitpack.zip" -d "$TEMP_DIR/bitpack"
cp "$TEMP_DIR/bitpack/Colored (64x64)/"*.png "$SPRITES_DIR/characters/" 2>/dev/null || \
cp "$TEMP_DIR/bitpack/"*/*.png "$SPRITES_DIR/characters/" 2>/dev/null || true

echo "   ✅ Sprites de personagens instalados"

# 3. UI PACK
echo ""
echo "3️⃣  UI Pack..."
download_file \
    "https://kenney.nl/content/3-assets/14-ui-pack/uipack.zip" \
    "$TEMP_DIR/uipack.zip"

echo "   Extraindo UI..."
unzip -q "$TEMP_DIR/uipack.zip" -d "$TEMP_DIR/uipack"
cp "$TEMP_DIR/uipack/PNG/"*.png "$UI_DIR/" 2>/dev/null || \
cp "$TEMP_DIR/uipack/"*/*.png "$UI_DIR/" 2>/dev/null || true

echo "   ✅ Elementos de UI instalados"

# 4. GAME ICONS (criar placeholders simples)
echo ""
echo "4️⃣  Criando placeholders de ícones..."

# Criar pixel branco 1x1 (para particles) usando Python se disponível
if command -v python3 >/dev/null 2>&1; then
    python3 - <<EOF
from PIL import Image
img = Image.new('RGB', (1, 1), color='white')
img.save('$SPRITES_DIR/white-pixel.png')
EOF
    echo "   ✅ Pixel branco criado (via Python)"
elif command -v convert >/dev/null 2>&1; then
    convert -size 1x1 xc:white "$SPRITES_DIR/white-pixel.png"
    echo "   ✅ Pixel branco criado (via ImageMagick)"
else
    echo "   ⚠️  PIL/ImageMagick não encontrado, pulando criação de pixel branco"
fi

# 5. ORGANIZAR ASSETS
echo ""
echo "📦 Organizando assets..."

# Criar sprite sheet de player (placeholder)
if [ -f "$SPRITES_DIR/tile_0000.png" ]; then
    cp "$SPRITES_DIR/tile_0000.png" "$SPRITES_DIR/player.png"
fi

# Criar sprite de enemy (placeholder)
if [ -f "$SPRITES_DIR/tile_0001.png" ]; then
    cp "$SPRITES_DIR/tile_0001.png" "$SPRITES_DIR/enemies/goblin.png"
fi

# Limpeza
echo ""
echo "🧹 Limpando arquivos temporários..."
rm -rf "$TEMP_DIR"

# Resumo
echo ""
echo "✅ =========================================="
echo "   DOWNLOAD COMPLETO!"
echo "=========================================="
echo ""
echo "📊 Assets instalados:"
echo "   - Tilesets: $(find $TILESETS_DIR -type f 2>/dev/null | wc -l) arquivos"
echo "   - Sprites: $(find $SPRITES_DIR -type f 2>/dev/null | wc -l) arquivos"
echo "   - UI: $(find $UI_DIR -type f 2>/dev/null | wc -l) arquivos"
echo ""
echo "📁 Localização: $ASSETS_DIR"
echo ""
echo "🎮 Próximo passo: Reinicie o cliente para carregar os assets"
echo "   cd client && npm run dev"
echo ""
echo "   Ou com Docker:"
echo "   docker-compose restart client"
echo ""
