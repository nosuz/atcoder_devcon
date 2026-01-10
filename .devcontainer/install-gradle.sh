#!/bin/bash
# .devcontainer/setup.sh

# チェック対象のディレクトリとマーカーファイル
MARKER_FILE="$HOME/.postCreateCommand-done"

# マーカーファイルがなければ初期化スクリプトを実行
if [ ! -f "$MARKER_FILE" ]; then
    export SDKMAN_DIR="$HOME/.sdkman"
    curl -s "https://get.sdkman.io" | bash
    source "$SDKMAN_DIR/bin/sdkman-init.sh"
    sdk install gradle 8.7

    # 初期化完了を示すマーカーファイルを作成
    touch "$MARKER_FILE"
fi
