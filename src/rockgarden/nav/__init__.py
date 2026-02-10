"""Navigation components: tree builder, breadcrumbs, folder indexes, TOC."""

from .breadcrumbs import Breadcrumb, build_breadcrumbs
from .folder_index import FolderChild, FolderIndex, generate_folder_indexes
from .labels import resolve_label
from .toc import TocEntry, extract_toc
from .tree import NavNode, build_nav_tree

__all__ = [
    "Breadcrumb",
    "FolderChild",
    "FolderIndex",
    "NavNode",
    "TocEntry",
    "build_breadcrumbs",
    "build_nav_tree",
    "extract_toc",
    "generate_folder_indexes",
    "resolve_label",
]
