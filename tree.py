from pathlib import Path

def tree(path: Path, prefix="", file=None):
  contents = sorted(path.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))
  for i, p in enumerate(contents):
    connector = "└── " if i == len(contents) - 1 else "├── "
    print(prefix + connector + p.name, file=file)
    if p.is_dir():
      extension = "    " if i == len(contents) - 1 else "│   "
      tree(p, prefix + extension, file=file)

with open("tree_output.txt", "w") as f:
  tree(Path("."), file=f)