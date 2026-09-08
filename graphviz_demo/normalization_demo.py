"""
正規化デモ: 「受注管理」テーブルを非正規形(UNF) -> 第1正規形(1NF)
-> 第2正規形(2NF) -> 第3正規形(3NF) まで段階的に正規化し、
各段階の ER 図を er_diagram.py（Graphviz ラッパー）で出力する。

題材: 受注明細（受注No, 受注日, 顧客CD, 顧客名, 顧客住所,
                商品CD, 商品名, 単価, 数量, 担当者CD, 担当者名）

関数従属性(FD):
  受注No                -> 受注日, 顧客CD, 顧客名, 顧客住所, 担当者CD, 担当者名
  商品CD                -> 商品名, 単価
  (受注No, 商品CD)      -> 数量                      ※複合キー全体に従属
  顧客CD                -> 顧客名, 顧客住所            ※推移的従属
  担当者CD              -> 担当者名                    ※推移的従属
"""

import os
from er_diagram import ERDiagram

OUT_DIR = os.path.join(os.path.dirname(__file__), "output")
os.makedirs(OUT_DIR, exist_ok=True)


def build_unf() -> ERDiagram:
    """非正規形 (UNF): 1件の受注の中に商品情報が繰り返し出現する"""
    d = ERDiagram(title="非正規形 (UNF) - 受注データ（繰り返し項目を含む）")
    t = d.entity("受注")
    t.pk("受注No")
    t.col("受注日")
    t.col("顧客CD")
    t.col("顧客名")
    t.col("顧客住所")
    t.col("商品CD・商品名・単価・数量", note="繰り返し項目（1受注に複数商品）")
    t.col("担当者CD")
    t.col("担当者名")
    return d


def build_1nf() -> ERDiagram:
    """第1正規形 (1NF): 繰り返し項目を排除し、行を商品明細単位に分解。
    ただしまだ1つのテーブルに全属性が同居しており、部分従属・推移従属が残る。
    """
    d = ERDiagram(title="第1正規形 (1NF) - 繰り返し項目を排除（複合キー化）")
    t = d.entity("受注明細_1NF")
    t.pk("受注No")
    t.pk("商品CD")
    t.col("受注日", "受注Noのみに従属＝部分従属")
    t.col("顧客CD", "受注Noのみに従属＝部分従属")
    t.col("顧客名", "顧客CD経由＝推移従属")
    t.col("顧客住所", "顧客CD経由＝推移従属")
    t.col("商品名", "商品CDのみに従属＝部分従属")
    t.col("単価", "商品CDのみに従属＝部分従属")
    t.col("数量", "(受注No,商品CD)に完全従属")
    t.col("担当者CD", "受注Noのみに従属＝部分従属")
    t.col("担当者名", "担当者CD経由＝推移従属")
    return d


def build_2nf() -> ERDiagram:
    """第2正規形 (2NF): 複合キーの一部にしか従属しない属性（部分従属）を
    別テーブルへ切り出す。ただし推移従属（非キー属性→非キー属性）は残る。
    """
    d = ERDiagram(title="第2正規形 (2NF) - 部分関数従属を排除", rankdir="LR")

    order = d.entity("受注")
    order.pk("受注No")
    order.col("受注日")
    order.col("顧客CD")
    order.col("顧客名", "顧客CD経由＝推移従属が残る")
    order.col("顧客住所", "顧客CD経由＝推移従属が残る")
    order.col("担当者CD")
    order.col("担当者名", "担当者CD経由＝推移従属が残る")

    product = d.entity("商品")
    product.pk("商品CD")
    product.col("商品名")
    product.col("単価")

    detail = d.entity("受注明細")
    detail.pk("受注No")
    detail.pk("商品CD")
    detail.col("数量")

    d.relate("受注", "受注明細", "1:N")
    d.relate("商品", "受注明細", "1:N")
    return d


def build_3nf() -> ERDiagram:
    """第3正規形 (3NF): 非キー属性間の推移従属（顧客CD→顧客名/住所、
    担当者CD→担当者名）も排除し、顧客・担当者テーブルへ切り出す。
    どの非キー属性も候補キーに対して完全かつ非推移的に従属する状態。
    """
    d = ERDiagram(title="第3正規形 (3NF) - 推移関数従属を排除（正規化完了）", rankdir="LR")

    customer = d.entity("顧客")
    customer.pk("顧客CD")
    customer.col("顧客名")
    customer.col("顧客住所")

    staff = d.entity("担当者")
    staff.pk("担当者CD")
    staff.col("担当者名")

    order = d.entity("受注")
    order.pk("受注No")
    order.col("受注日")
    order.fk("顧客CD")
    order.fk("担当者CD")

    product = d.entity("商品")
    product.pk("商品CD")
    product.col("商品名")
    product.col("単価")

    detail = d.entity("受注明細")
    detail.pk("受注No")
    detail.pk("商品CD")
    detail.col("数量")

    d.relate("顧客", "受注", "1:N")
    d.relate("担当者", "受注", "1:N")
    d.relate("受注", "受注明細", "1:N")
    d.relate("商品", "受注明細", "1:N")
    return d


def main():
    stages = [
        ("1_unf", build_unf()),
        ("2_1nf", build_1nf()),
        ("3_2nf", build_2nf()),
        ("4_3nf", build_3nf()),
    ]
    for filename, diagram in stages:
        path = diagram.render(os.path.join(OUT_DIR, filename), fmt="png")
        print(f"生成: {path}")


if __name__ == "__main__":
    main()
