"""
sqlalchemy_schemadisplay を使い、model.py の SQLAlchemy モデルから
自動で ER 図（PNG）を生成する。

自作の er_diagram.py（Graphviz を手組みで操作するクロウズフット記法）との
比較用。こちらは SQLAlchemy の MetaData を解析し、PK/FK やカラム型を
自動で抽出して描画する。
"""

import os

from sqlalchemy import create_engine
from sqlalchemy_schemadisplay import create_schema_graph

from model import Base

OUT_DIR = os.path.join(os.path.dirname(__file__), "output")
os.makedirs(OUT_DIR, exist_ok=True)


def main():
    engine = create_engine("sqlite:///:memory:")

    graph = create_schema_graph(
        engine=engine,
        metadata=Base.metadata,
        show_datatypes=True,
        show_indexes=False,
        show_column_keys=True,
        rankdir="LR",
        concentrate=False,
    )

    out_path = os.path.join(OUT_DIR, "schema_er.png")
    graph.write_png(out_path)
    print(f"生成: {out_path}")


if __name__ == "__main__":
    main()
