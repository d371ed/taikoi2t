# taikoi2t

ゲーム「ブルーアーカイブ」 (日本語版) 戦術対抗戦リザルトのスクリーンショットから, 編成データを画像認識で抽出します.

```sh
> poetry run taikoi2t -d .\students.csv .\Screenshot_2025.04.01_00.00.00.000.png .\Screenshot_2025.04.01_01.00.00.000.png
TRUE	ホシノ	バネル	マリナ	アジュリ	水シロコ	ヒビキ	水ハナコ	マリナ	シロコ＊	ホシノ	水シロコ	ヒビキ
FALSE	イオリ	ホシノ	シロコ＊	シュン	水シロコ	佐天涙子	ホシノ	シロコ＊	マリナ	レイサ	水シロコ	ヒビキ
```

出力は Google スプレッドシートへ貼り付けることを想定し, デフォルトでは TSV になります.

- 動画のフレーム保存など多少画質の低い画像へ対応
  - 生徒名辞書から生徒名を構成する文字のみを認識対象に
  - 編集距離 (Levenshtein) による生徒名のマッチングで誤検出を補正
  - 取りこぼしやすい濁点を濁点除去したスコアでの比較で補正
- 外部 CSV ファイルによる追加生徒対応
- 生徒名の別名 (略称) 変換
- スペシャルの左右を辞書順に統一
- 勝敗の取得
- 対戦相手名の取得 (`--opponent`)
- 出力列のカスタマイズ (`--columns`)
- 出力形式は TSV, CSV, JSON

**※注意** [PyTorch](https://pytorch.org/) のインストールにより, これだけで 4.7GB 以上のストレージ容量が必要になるはずです. CPU 版に変更することで省容量化は可能ですが, 実行速度が大きく低下します.
また GPU とドライバが CUDA 12.6 をサポートしていない場合もおそらく実行速度が低下する (あるいは実行自体が不能) と予想されます.

これについては [PyTorch バージョンについて](#pytorch-バージョンについて) をご覧ください.

**※注意** 該当ゲーム画面の UI が変更された場合抽出が不能になります. 2025年4月時点の UI に基づいて設計されています.


## インストール

事前に [Python](https://www.python.org/) 3.13 と [Poetry](https://python-poetry.org/) のインストールが必要です.

また, ご使用の GPU が CUDA 12.6 非対応の場合は事前に [PyTorch バージョンについて](#pytorch-バージョンについて) の手順が必要です.

```sh
cd path\to\taikoi2t\
poetry install
```

CUDA 版 [PyTorch](https://pytorch.org/) を利用しているため, かなり容量の大きいダウンロードが発生するはずです.

`poetry run taikoi2t --help` でヘルプが表示されれば成功です. (初回実行時はやや時間がかかると思います.)


## 使い方

`poetry run taikoi2t -d (生徒辞書 CSV へのパス)` に続き抽出対象の画像ファイル (PNG, JPEG 等) のパスを渡してください.

```sh
poetry run taikoi2t -d .\students.csv .\Screenshot_2025.04.01_00.00.00.000.png .\videoframe_100000.jpg
```

以下のようにすると出力される情報と順序をカスタマイズできます. 詳しくは [`specification.md`](./specification.md) をご覧ください.

```sh
poetry run -- taikoi2t -d .\students.csv --column PNAME PWOL PTEAM ONAME OWOL OTEAM -- .\Screenshot_2025.04.01_00.00.00.000.png
```

```tsv:output
プレイヤー	Win	ホシノ	バネル	マリナ	アジュリ	水シロコ	ヒビキ	対戦相手	Lose	水ハナコ	マリナ	シロコ＊	ホシノ	水シロコ	ヒビキ
```

例えば出力の TSV をクリップボードにコピーするには, PowerShell であれば `Set-Clipboard` にリダイレクトします.

```powershell
poetry run taikoi2t -d .\students.csv .\videoframe_100000.jpg | Set-Clipboard
```

新規生徒追加時や, 出力される別名を変更したい場合は辞書 [`students.csv`](./students.csv) の編集が必要になります. [生徒名辞書](./specification.md#生徒名辞書) をご覧ください.


## 利用例

[`frontend`](./frontend/) ディレクトリ下に Windows 環境での利用例となるスクリプトがあります.
バッチファイル (.bat) をダブルクリックで起動することを想定しています.


## PyTorch バージョンについて

OCR の動作に [PyTorch](https://pytorch.org/) を利用しています.

デフォルトでは CUDA 12.6 対応の PyTorch をインストールしますが, お使いの GPU に適合しない場合はインストール前に [`pyproject.toml`](./pyproject.toml) を書き換えることで構成をカスタマイズする必要があります.

CUDA 11.8 へ変更する例:

```toml:pyproject.toml
[[tool.poetry.source]]
name = "torch_source"
url = "https://download.pytorch.org/whl/cu118" # 該当バージョン取得先へ変更
priority = "explicit"

[tool.poetry.dependencies]
torch = {source = "torch_source"}
torchvision = {source = "torch_source"}
```

書き換え後, 以下のコマンドでインストールを進行します.

```sh
poetry update torch torchvision
poetry install
```

グラフィックボードを搭載していない PC など, CPU で実行する場合は上記コードを削除してください.
これにより大幅にストレージ容量を節約することが可能です. (ただし実行速度は CUDA 版よりかなり低下します.)


## アンインストール

`taikoi2t` ディレクトリごと削除してください. 依存パッケージは仮想環境にインストールしています.

不要であれば同時に導入した Python と Poetry もアンインストールしてください.

容量が大きいため, Windows でゴミ箱移動した場合はすぐ空にすることをお勧めします.


## できないこと

- 各生徒のダメージ数値の抽出
- アイコンによる攻撃側/防御側の判定
- `ホシノ（臨戦）` のタイプ判定
- 大きくアスペクト比の狂った画像からの抽出
- サーバとしての動作


## 制作者の実行環境

- Windows 11 Pro 24H2
- Python 3.13.5
- AMD Ryzen 7 7700
- RAM 32GB
- NVIDIA GeForce RTX 5060 Ti 16GB
- NVIDIA Driver Version: 576.52, CUDA Version: 12.8

(過去の開発機)

- Windows 11 Home 24H2
- Python 3.13.2
- Intel Core i5-9600K
- RAM 16GB
- NVIDIA GeForce GTX 1060 6GB
- NVIDIA Driver Version: 560.94, CUDA Version: 12.6


## 免責等

特に CUDA 周りなどすべての環境での快適な動作を保証することはできません.

本ソフトウェアはゲーム「ブルーアーカイブ」の開発元の Nexon Games 社および日本語版パブリッシャーの Yostar 社とは無関係です.

本ソフトウェアは直接ゲームプレイへ何も作用しないものではありますが, 利用規約 (特に 第11条 (13) 項) へ抵触すると権利者さまが判断された場合, 即時公開を停止いたします.
