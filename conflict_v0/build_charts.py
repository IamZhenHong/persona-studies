"""Embed charts_data.json into charts_build.html -> persona/results/conflict_v0/conflict_charts.html (standalone), plus
conflict_charts_artifact.html (same page without doctype/html/head/body tags, which the Artifact publish adds).
  uv run python persona/conflict_v0/charts_data.py && uv run python persona/conflict_v0/build_charts.py"""
import re
from pathlib import Path
HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "results" / "conflict_v0"
html = (HERE / "charts_build.html").read_text().replace("/*__DATA__*/{}", (HERE / "charts_data.json").read_text())
(OUT / "conflict_charts.html").write_text(html)
art = re.sub(r"<!doctype html>\s*|<html[^>]*>\s*|</html>\s*|<head>\s*|</head>\s*|<body>\s*|</body>\s*|<meta [^>]*>\s*", "", html)
(OUT / "conflict_charts_artifact.html").write_text(art)
print(OUT / "conflict_charts.html", OUT / "conflict_charts_artifact.html")
