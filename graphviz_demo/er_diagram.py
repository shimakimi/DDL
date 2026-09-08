"""
Graphviz を利用した ER 図生成ライブラリ

エンティティ（テーブル）と主キー/外部キー、リレーションシップ（カーディナリティ）
を定義するだけで、鴉の足記法（クロウズフット記法）の ER 図を生成できる。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from graphviz import Digraph


@dataclass
class Attribute:
    """テーブルの属性（カラム）"""

    name: str
    is_pk: bool = False       # 主キーの一部か
    is_fk: bool = False       # 外部キーか
    note: str = ""            # 型・補足など（任意）

    def label_row(self) -> str:
        """HTML-like label 用の 1 行分の TR を生成する"""
        deco = []
        if self.is_pk:
            deco.append("PK")
        if self.is_fk:
            deco.append("FK")
        tag = ",".join(deco)
        name_html = f"<U>{self.name}</U>" if self.is_pk else self.name
        note_html = f' <FONT COLOR="gray40" POINT-SIZE="10">{self.note}</FONT>' if self.note else ""
        tag_html = f' <FONT COLOR="gray40" POINT-SIZE="10">[{tag}]</FONT>' if tag else ""
        align = "LEFT"
        return (
            f'<TR><TD ALIGN="{align}" PORT="{self.name}">{name_html}{note_html}{tag_html}</TD></TR>'
        )


@dataclass
class Entity:
    """テーブル（エンティティ）"""

    name: str
    attributes: list[Attribute] = field(default_factory=list)

    def pk(self, name: str, note: str = "") -> "Entity":
        self.attributes.append(Attribute(name, is_pk=True, note=note))
        return self

    def fk(self, name: str, note: str = "") -> "Entity":
        self.attributes.append(Attribute(name, is_fk=True, note=note))
        return self

    def col(self, name: str, note: str = "") -> "Entity":
        self.attributes.append(Attribute(name, note=note))
        return self

    def to_html_label(self) -> str:
        rows = "".join(a.label_row() for a in self.attributes)
        return (
            '<<TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0" CELLPADDING="6">'
            f'<TR><TD BGCOLOR="#4472C4"><FONT COLOR="white"><B>{self.name}</B></FONT></TD></TR>'
            f'<HR/>{rows}'
            "</TABLE>>"
        )


# カーディナリティ -> (tail矢印, head矢印) の対応（クロウズフット記法）
_CROWFOOT = {
    "1:1": ("tee", "tee"),
    "1:N": ("tee", "crow"),
    "N:1": ("crow", "tee"),
    "N:M": ("crow", "crow"),
}


@dataclass
class Relationship:
    parent: str          # "1" 側などリレーション元のエンティティ名
    child: str           # 関連先エンティティ名
    cardinality: str = "1:N"   # "1:1" | "1:N" | "N:1" | "N:M"
    label: str = ""


class ERDiagram:
    """複数の Entity / Relationship を保持し Graphviz で描画するビルダー"""

    def __init__(self, title: str = "ER Diagram", rankdir: str = "LR"):
        self.title = title
        self.entities: dict[str, Entity] = {}
        self.relationships: list[Relationship] = []
        self.rankdir = rankdir

    def add_entity(self, entity: Entity) -> Entity:
        self.entities[entity.name] = entity
        return entity

    def entity(self, name: str) -> Entity:
        """新規エンティティを作成して登録する（メソッドチェーン用）"""
        e = Entity(name)
        self.add_entity(e)
        return e

    def relate(self, parent: str, child: str, cardinality: str = "1:N", label: str = "") -> None:
        self.relationships.append(Relationship(parent, child, cardinality, label))

    def build(self) -> Digraph:
        g = Digraph("ER", graph_attr={
            "rankdir": self.rankdir,
            "label": self.title,
            "labelloc": "t",
            "fontsize": "20",
            "fontname": "Meiryo",
            "bgcolor": "white",
            "splines": "ortho",
        })
        g.attr("node", shape="plain", fontname="Meiryo")
        g.attr("edge", fontname="Meiryo", fontsize="11", color="gray30")

        for entity in self.entities.values():
            g.node(entity.name, label=entity.to_html_label())

        for rel in self.relationships:
            tail_arrow, head_arrow = _CROWFOOT.get(rel.cardinality, ("tee", "crow"))
            g.edge(
                rel.parent,
                rel.child,
                dir="both",
                arrowtail=tail_arrow,
                arrowhead=head_arrow,
                label=rel.label,
            )
        return g

    def render(self, filepath: str, fmt: str = "png", cleanup: bool = True) -> str:
        g = self.build()
        out = g.render(filepath, format=fmt, cleanup=cleanup)
        return out
