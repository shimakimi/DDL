# DDL / ER図生成 比較プロジェクト

「受注管理」スキーマ（顧客・担当者・受注・商品・受注明細、第3正規形）を題材に、
ER図を生成する2つのアプローチを比較する。

- `graphviz_demo/` — Graphviz を直接ラップした自作ライブラリで、正規化の各段階
  （UNF → 1NF → 2NF → 3NF）をクロウズフット記法で描画する
- `sqlalchemy_schemadisplay_demo/` — 同じ3NFスキーマを SQLAlchemy の宣言的モデルで
  定義し、`sqlalchemy_schemadisplay` で MetaData から自動的にER図を生成する

## フォルダ構成

```
DDL/
├── requirements.txt              # 両デモ共通の依存ライブラリ
├── graphviz_demo/
│   ├── er_diagram.py             # Graphviz ラッパー（Entity/Attribute/ERDiagram）
│   ├── normalization_demo.py     # 正規化デモ本体（UNF〜3NFを4枚生成）
│   └── output/
│       ├── 1_unf.png
│       ├── 2_1nf.png
│       ├── 3_2nf.png
│       └── 4_3nf.png
└── sqlalchemy_schemadisplay_demo/
    ├── model.py                  # 3NFスキーマをSQLAlchemyモデルで再現
    ├── generate_diagram.py       # create_schema_graph() でER図を自動生成
    └── output/
        └── schema_er.png
```

## セットアップ

前提として Graphviz 本体（`dot.exe`）がインストール済みであること
（`C:\Program Files\Graphviz\bin` にインストール済み。未インストールなら
https://graphviz.org/download/ から導入し、PATH に追加する）。

```powershell
# 仮想環境の作成・有効化
python -m venv .venv
.venv\Scripts\Activate.ps1

# 依存ライブラリのインストール
pip install -r requirements.txt
```

`requirements.txt` の内容:

```
graphviz==0.21
sqlalchemy==2.0.52
sqlalchemy_schemadisplay==2.0
pydot==4.0.1
```

## 実行方法

### 1. 自作 Graphviz ラッパー版（正規化ステップの可視化）

```powershell
cd graphviz_demo
python normalization_demo.py
```

`output/` に `1_unf.png` 〜 `4_3nf.png` が生成される。

### 2. sqlalchemy_schemadisplay 版（ORMモデルからの自動生成）

```powershell
cd sqlalchemy_schemadisplay_demo
$env:PYTHONUTF8 = "1"
python generate_diagram.py
```

`output/schema_er.png` が生成される。

> **注意（Windows + 日本語ラベル）**: `PYTHONUTF8=1` を設定しないと、
> `sqlalchemy_schemadisplay`（内部で使う `pydot`）が一時DOTファイルを
> Windows既定のcp932で書き出してしまい、Graphviz の `dot` コマンドが
> 日本語ラベルを解釈できずに `AssertionError: "dot" ... returned code: 1`
> で失敗する。環境変数で Python の I/O を UTF-8 に強制することで解消する。

## 比較結果

同一の3NFスキーマ（顧客 1:N 受注 1:N 受注明細 N:1 商品、担当者 1:N 受注）を
2通りの方法で描画した結果の比較。

| 観点 | 自作 `er_diagram.py`（`graphviz_demo`） | `sqlalchemy_schemadisplay` |
|---|---|---|
| 入力 | 手書きの Entity/Attribute 定義 | 既存の SQLAlchemy ORM モデル（`Base.metadata`）から自動抽出 |
| 記法 | クロウズフット記法（1:N 等のカーディナリティを明示） | UML風の単純な矢印（カーディナリティ表現なし） |
| PK/FK表示 | `[PK]`/`[FK]` タグ＋下線、任意の補足コメント欄あり | `(PK)`/`(FK)` 表記、カラム型も自動表示 |
| 日本語対応 | Meiryo フォント指定で問題なし | デフォルトフォント（Bitstream Vera Sans）が非対応。`PYTHONUTF8=1` の設定も必須 |
| 用途 | 概念設計の説明・教材向け。正規化ステップごとの注釈やレイアウトを自由に制御できる | 実装済みの ORM モデルから「今のDB構造」を機械的に可視化する用途向き |

自作版は正規化ステップを教材として説明する用途に強く、`sqlalchemy_schemadisplay` は
実装コード（SQLAlchemyモデル）と図を同期させる「生きたドキュメント」用途に向いている。
日本語環境で `sqlalchemy_schemadisplay` を使う場合は、`create_schema_graph()` の
`font` 引数に IPAexGothic 等の和文フォントを指定するとさらに見た目が改善する。
