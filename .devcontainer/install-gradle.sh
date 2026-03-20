#!/bin/bash
# .devcontainer/setup.sh

# チェック対象のディレクトリとマーカーファイル
MARKER_FILE="$HOME/.postCreateCommand-done"

if [ -f "$MARKER_FILE" ]; then
  # マーカーファイルがあれば終了
  exit 0
elif [ ! -w "$HOME" ]; then
  # ホームに書き込めない時は、異常終了
  echo "ホームディレクトリが書き込めません。"
  exit 1
fi

# Gradleをインストール
# $HOMEに書き込み権が必要
export SDKMAN_DIR="$HOME/.sdkman"
curl -s "https://get.sdkman.io" | bash
source "$SDKMAN_DIR/bin/sdkman-init.sh"
sdk install gradle 8.7

# 初期化完了を示すマーカーファイルを作成
touch "$MARKER_FILE"
