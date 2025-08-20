# Virtual Keyboard with Hand Tracking

<a href="ここにデモ動画やGIFへのリンクを貼る">
  <img src="ここにデモ動画やGIFの画像を貼る" alt="Project Demo">
</a>

<br>

Webカメラからの映像を元にハンドトラッキングを行い、空中でタイピングを実現する仮想キーボードです。

## 概要

このプロジェクトは、[OpenCV](https://opencv.org/) と [MediaPipe](https://ai.google.dev/edge/mediapipe/solutions/guide) を利用して、リアルタイムに手の動きを認識します。あらかじめXMLファイルで定義されたキーマップに基づき、指の動きを特定のキー入力に変換することで、物理的なキーボードなしでの文字入力を可能にします。

## ✨ 特徴

* **リアルタイム処理**: Webカメラからの映像を低遅延で処理し、スムーズな入力を実現します。
* **柔軟なキーマッピング**: XMLファイルを編集するだけで、キーボードのレイアウトや各キーの位置を自由にカスタマイズできます。
* **シンプルな構成**: Pythonと主要なライブラリのみで構成されており、セットアップが容易です。

## 🛠️ 技術スタック

* Python Python 3.10.12
* OpenCV-Python
* MediaPipe
* その他requirements.txtを参照

## 🚀 セットアップ方法

1.  **リポジトリをクローン**
    ```bash
    git clone <このリポジトリのURL>
    cd VirtualKeyboard
    ```

2.  **仮想環境の作成と有効化**
    * Windows
        ```bash
        python -m venv venv
        .\venv\Scripts\activate
        ```
    * macOS / Linux
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```

3.  **必要なライブラリをインストール**
    ```bash
    pip install -r requirements.txt
    ```

## 使い方

以下のコマンドでプログラムを実行します。

```bash
python src/main.py
```