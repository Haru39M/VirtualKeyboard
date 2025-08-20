#!/bin/bash

# Python仮想環境を有効にする
source venv/bin/activate

# lsusbの実行結果に"Anker PowerConf"が含まれているか確認
if lsusb | grep -q "Anker PowerConf"; then
    # 含まれている場合、Pythonスクリプトを実行
    echo "Anker PowerConf found. Starting the program..."
    python test_webcam3.py
else
    # 含まれていない場合、指定されたメッセージを表示
    echo "Anker PowerConf not found."
    echo "Please connect the device."
    echo "If you are using WSL, you may need to attach the device."
    echo "e.g., run the following commands in PowerShell:"
    echo "usbipd list"
    echo "usbipd attach --wsl --busid 1-5"
fi