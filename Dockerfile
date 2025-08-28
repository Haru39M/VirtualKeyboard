FROM python:3.10-slim

# ★★★ この行を追加 ★★★
# Qtプラグインのデバッグ情報を有効にする
# ENV QT_DEBUG_PLUGINS=1
ENV QT_QPA_PLATFORM=xcb

# 作業ディレクトリを設定
WORKDIR /app

# (以下、変更なし)
# GUI(OpenCV/Qt)に必要なシステムライブラリをインストール
RUN apt-get update && apt-get install -y --no-install-recommends \
    x11-apps \
    libopencv-dev \
    # # xcbプラグインの直接的な依存関係
    # libx11-xcb1 \
    # libxcb-icccm4 \
    # libxcb-image0 \
    # libxcb-keysyms1 \
    # libxcb-randr0 \
    # libxcb-render-util0 \
    # libxcb-xinerama0 \
    # libxcb-xfixes0 \
    # libxkbcommon-x11-0 \
    # # xcbがさらに依存する基本ライブラリ
    # libgl1 \
    # libglib2.0-0 \
    # libfontconfig1 \
    # libxrender1 \
    # libxext6 \
    # libsm6 \
    # libice6 \
    # libxt6 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# requirements.txt をコピーしてライブラリをインストール
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションに必要なファイルをすべてコピー
COPY src/ .
COPY configs/ ./configs/

# 実行コマンド
CMD ["python", "main.py"]