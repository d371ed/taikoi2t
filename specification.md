# 仕様

```
usage: taikoi2t
       [-h] [--version] -d DICTIONARY [--opponent | -c COLUMNS [COLUMNS ...]]
       [--csv | --json] [--no-alias] [--no-sp-sort] [-v]
       files [files ...]

positional arguments:
  files                 target images

options:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  -d, --dictionary DICTIONARY
                        student dictionary (CSV)
  --opponent            include the name of opponent
  -c, --columns COLUMNS [COLUMNS ...]
                        select columns in a row
  --csv                 change output to CSV (default: TSV)
  --json                change output to JSON (default: TSV)
  --no-alias            turn off alias mapping for student's name
  --no-sp-sort          turn off sorting specials
  -v, --verbose         print messages and show images for debug (default:
                        silent, -v: error, -vv: print, -vvv: image)
```

<!-- MARK for update_usage.py -->


## コマンドライン引数

### `-d, --dictionary`

必須.
生徒名と別名を記述した辞書ファイルを指定.

詳しくは [生徒名辞書](#生徒名辞書) をご覧ください.


### `--opponent`

任意.
対戦相手 (右側) の名前を検出し, 右側チームの前の列に挿入.

`--columns` と同時に指定はできません.
小書き文字 (っ, ゃ, ぃ 等) や濁音/半濁音 (が, ぱ 等), 日本語外の漢字は検出精度が低い傾向にあります.


### `-c, --columns`

任意.
出力列を後続の引数で設定.

`--opponent` と同時に指定はできません.

<details>
<summary>使用できる列の一覧 (クリックで展開)</summary>

- `IMAGE_PATH`: 画像のパス
- `IMAGE_NAME`, `INAME`: 画像パスのファイル名部分
- `IMAGE_WIDTH`: 画像の幅 (pixel)
- `IMAGE_HEIGHT`: 画像の高さ (pixel)
- `PLAYER_WINS`, `LEFT_WINS`, `PWIN`, `LWIN`: プレイヤー側勝利で `TRUE`, 敗北かエラー時 `FALSE`
- `PLAYER_WOL`, `LEFT_WOL`, `PWOL`, `LWOL`: プレイヤー側勝利で `Win`, 敗北かエラー時 `Lose`
- `PLAYER_NAME`, `PLAYER_OWNER`, `LEFT_OWNER`, `PNAME`, `POWN`, `LOWN`: プレイヤーの先生名
- `PLAYER_TEAM`, `LEFT_TEAM`, `PLAYER_MEMBERS`, `LEFT_MEMBERS`, `PTEAM`, `LTEAM`, `PMEMS`, `LMEMS`: プレイヤー側全員の生徒名 (6列)
- `PLAYER_STRIKERS`, `LEFT_STRIKERS`, `PSTS`, `LSTS`: プレイヤー側ストライカー (4列)
- `PLAYER_STRIKER_1`, `LEFT_STRIKER_1`, `PST1`, `LST1`, `P1`, `L1`: プレイヤー側ストライカーの1人目
- (上と同形式で 2～4 も有効)
- `PLAYER_SPECIALS`, `LEFT_SPECIALS`, `PSPS`, `LSPS`: プレイヤー側スペシャル (2列)
- `PLAYER_SPECIAL_1`, `LEFT_SPECIAL_1`, `PSP1`, `LSP1`, `P5`, `L5`: プレイヤー側スペシャルの1人目
- `PLAYER_SPECIAL_2`, `LEFT_SPECIAL_2`, `PSP2`, `LSP2`, `P6`, `L6`: プレイヤー側スペシャルの2人目
- `OPPONENT_WINS`, `RIGHT_WINS`, `OWIN`, `RWIN`: 相手側勝利で `TRUE`, 敗北かエラー時 `FALSE`
- `OPPONENT_WOL`, `RIGHT_WOL`, `OWOL`, `RWOL`: 相手側勝利で `Win`, 敗北かエラー時 `Lose`
- `OPPONENT_NAME`, `OPPONENT_OWNER`, `RIGHT_OWNER`, `ONAME`, `OOWN`, `ROWN`: 対戦相手の先生名
- `OPPONENT_TEAM`, `RIGHT_TEAM`, `OPPONENT_MEMBERS`, `RIGHT_MEMBERS`, `OTEAM`, `RTEAM`, `OMEMS`, `RMEMS`: 相手側全員の生徒名 (6列)
- `OPPONENT_STRIKERS`, `RIGHT_STRIKERS`, `OSTS`, `RSTS`: 相手側ストライカー (4列)
- `OPPONENT_STRIKER_1`, `RIGHT_STRIKER_1`, `OST1`, `RST1`, `O1`, `R1`: 相手側ストライカーの1人目
- (上と同形式で 2～4 も有効)
- `OPPONENT_SPECIALS`, `RIGHT_SPECIALS`, `OSPS`, `RSPS`: 相手側スペシャル (2列)
- `OPPONENT_SPECIAL_1`, `RIGHT_SPECIAL_1`, `OSP1`, `RSP1`, `O5`, `R5`: 相手側スペシャルの1人目
- `OPPONENT_SPECIAL_2`, `RIGHT_SPECIAL_2`, `OSP2`, `RSP2`, `O6`, `R6`: 相手側スペシャルの2人目
- `BLANK`, `BL`: 空の列
</details>

コマンドの途中で記述する場合, 入力画像パスと区別がつかなくなるため `--` を以下のように挿入してください.

```sh
poetry run -- taikoi2t -d .\students.csv -c PWIN PTEAM OWIN OTEAM -- .\image1.png .\image2.png
```

このとき `poetry run` の後ろにも `--` を入れるようにしてください. (Poetry 側の仕様です.)


### `--csv`

任意.
出力形式を CSV へ変更.

TSV と同様ヘッダ行はありません.
`--json` と同時に指定はできません.


### `--json`

任意.
出力形式を JSON へ変更.

`--csv` と同時に指定はできません.
`--columns` の指定は無効となり, 出力される要素が削られることはありません.


### `--no-alias`

任意.
別名への変換機能をオフ.

辞書での指定を無視し, ゲーム内の生徒名表記で出力します.


### `--no-sp-sort`

任意.
スペシャル生徒の左右調整機能をオフ.

辞書内の記載順を無視し, 入力画像の順番を維持します.


### `-v, --verbose`

任意.
デバッグ用の出力モードへ切り替え.


#### デフォルト (指定なし)

Silent. 通常の解析結果を返すモード.

致命的なエラーを除き stderr へも出力を行いません.

画像単位でエラーがあった場合, 実行を継続しつつ stdout へ文字列部分がすべて `Error` の行を出力します.


#### `-v` または `--verbose`

Error. エラーと警告を stderr へ出力するモード.

画像単位でエラーがあった場合に実行は継続されますが, stderr へエラーを出力します. Silent 時と同様に stdout へのエラー行出力もおこなわれます.


#### `-vv`

Print. stdout へデバッグ用の情報を詳細に出力するモード.

結果の出力形式は TSV / CSV ではなくなります.


#### `-vvv`

Image. Print の内容に加え `cv2.imshow` で画像解析の途中経過を表示するモード.


### `-h, --help`

上記ヘルプを表示.


### `--version`

バージョン情報を表示.


### `files`

1つ以上必須.
解析対象となる画像のパスを指定. ワイルドカードには非対応.

複数渡された場合, 左から順に解析し結果を1画像あたり1行ずつ出力します.
何らかのエラーで抽出が失敗した場合, 文字列部分がすべて `Error` の行が出力されます.


## TSV, CSV 出力

デフォルトでは以下の形式で出力されます. (区切り文字はスペースに置換してありますが実際はタブ文字 `\t` か `,` です.)

```
勝敗 L1 L2 L3 L4 LSP1 LSP2 (対戦相手) R1 R2 R3 R4 RSP1 RSP2
```

1行が1つの画像に対応します. 行の出力順は入力順と同じです.

5人以下のチームは該当の生徒名が空文字列になります.
現状スペシャル生徒の判定ができないため, ストライカーの枠に左詰めで入ることがあります.

抽出に失敗した場合は以下のようなエラー行が出力されます.

```
FALSE Error Error Error Error Error Error Error Error Error Error Error Error Error
```

出力形式をカスタマイズしたい場合は [`--columns` オプション](#-c---columns)を使用してください.


### 勝敗

`TRUE` or `FALSE`.
左側のチームが勝利の場合 `TRUE`. 解析にエラーのあった行の場合は `FALSE`.


### L1 ～ L4

`str`.
左側のチームのストライカー生徒名. 攻撃のログなら A1 ～ A4, 防御のログなら D1 ～ D4.

何らかのエラーがあり抽出に失敗した場合は `Error`. (他の文字列のカラムも同じです.)


### LSP1, LSP2

`str`.
左側のチームのスペシャル生徒名.

与えた辞書ファイルの記載順に左右が調整されます.
(ただし現状生徒名でのスペシャル判定ができないため, 5人以下の編成の場合は正常に機能しません. 右側チームも同様です.)


### (対戦相手)

`str`. (`--opponent` オプション指定時.)
対戦相手 (右側のチーム) の先生名.


### R1 ～ R4

`str`.
右側のチームのストライカー生徒名. 攻撃のログなら D1 ～ D4, 防御のログなら A1 ～ A4.


### RSP1, RSP2

`str`.
右側のチームのスペシャル生徒名.

与えた辞書ファイルの記載順に左右が調整されます.


## JSON 出力

以下のような形式で出力されます. (実際にはインデント無しで1行です.)

<details>
<summary>出力例 (クリックで展開)</summary>

```json
{
  "arguments": [
    "taikoi2t",
    "-d",
    ".\\students.csv",
    ".\\tests\\images\\0004.png",
    "--json"
  ],
  "starts_at": "2025-05-01T00:00:00.000000",
  "ends_at": "2025-05-01T00:00:05.000000",
  "matches": [
    {
      "image": {
        "path": "tests/images/0004.png",
        "name": "0004.png",
        "width": 2560,
        "height": 1080,
        "modal": {
          "left": 215,
          "top": 79,
          "right": 2346,
          "bottom": 998
        }
      },
      "player": {
        "wins": false,
        "owner": "プレイヤー",
        "strikers": {
          "striker1": {
            "index": 162,
            "name": "ホシノ",
            "alias": null
          },
          "striker2": {
            "index": 187,
            "name": "ミヤコ",
            "alias": null
          },
          "striker3": {
            "index": 90,
            "name": "シロコ＊テラー",
            "alias": "シロコ＊"
          },
          "striker4": {
            "index": 129,
            "name": "ノノミ",
            "alias": null
          }
        },
        "specials": {
          "special1": {
            "index": 0,
            "name": "シロコ（水着）",
            "alias": "水シロコ"
          },
          "special2": {
            "index": 18,
            "name": "アヤネ（水着）",
            "alias": "水アヤネ"
          }
        }
      },
      "opponent": {
        "wins": true,
        "owner": "対戦相手",
        "strikers": {
          "striker1": {
            "index": 162,
            "name": "ホシノ",
            "alias": null
          },
          "striker2": {
            "index": 84,
            "name": "シュン",
            "alias": null
          },
          "striker3": {
            "index": 90,
            "name": "シロコ＊テラー",
            "alias": "シロコ＊"
          },
          "striker4": {
            "index": 211,
            "name": "レイサ",
            "alias": null
          }
        },
        "specials": {
          "special1": {
            "index": 0,
            "name": "シロコ（水着）",
            "alias": "水シロコ"
          },
          "special2": {
            "index": 217,
            "name": "佐天涙子",
            "alias": null
          }
        }
      }
    }
  ]
}
```
</details>

生徒の `index` は与えられた辞書内での行位置 (行 - 1) を表します.


## 生徒名辞書

`-d, --dictionary` に与える生徒名辞書を [`students.csv`](./students.csv) として同梱しています.

ヘッダ行を含まない CSV で, `ゲーム中の生徒名表記,出力時変換したい別名` の2列で記述されている必要があります.

```csv
シロコ（水着）,水シロコ
アイリ,
アイリ（バンド）,バアイリ
アオバ,
...
```

別名が不要な場合は, 空文字列にすることでそのままの生徒名を出力します.

また, **並び順はスペシャル生徒のソートに利用** するため, 優先して左側に配置したい生徒はより先に記述してください.
(上の例では `シロコ（水着）` を常に左のデータへ正規化するため最初の行に記述しています.)

新たに生徒が追加された場合にはこのファイルに追加する必要があります.
精度向上のため, **この辞書に無い生徒名は検出が不可能** です.

(`students.csv` はスクレイピングにより自動生成していますが, 現在 Google スプレッドシートによって実装されているため同梱していません.)
