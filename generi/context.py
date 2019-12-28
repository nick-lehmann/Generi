import tarfile
import tempfile
import os
from pathlib import Path
from typing import BinaryIO, Dict


build_contexts: Dict[Path, BinaryIO] = dict()


def create_tar(path: Path) -> BinaryIO:
    if path in build_contexts:
        return build_contexts[path]

    f = tempfile.NamedTemporaryFile()
    with tarfile.open(mode="w:gz", fileobj=f) as tar:
        tar.add(path, arcname=os.path.sep)

    f.seek(0)

    build_contexts[path] = f
    return f
