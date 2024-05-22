from build123d import *
from ocp_vscode import show

import build123d as bd

with bd.BuildPart() as bp:
    bd.Box(3, 3, 3)
    with bd.BuildSketch(*bp.faces()):
        bd.Rectangle(1, 2, rotation=45)
    bd.extrude(amount=0.1)
show(bp)
