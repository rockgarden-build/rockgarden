# Feature 06: Navigation ✅

Breadcrumbs, sidebar navigation with collapsible folder tree, and auto-generated folder index pages.

## Goal

```
uv run rockgarden build
```

Produces HTML pages with:
- Breadcrumbs showing path to current page
- Sidebar nav showing nested folder structure
- Collapsible folder headings
- Auto-generated index pages for folders

## Features

### Breadcrumbs

Path-based navigation showing current location in folder hierarchy:
- Displayed above page content
- Each segment links to its folder index
- Example: `Home > Characters > NPCs > Olvir`

### Sidebar Navigation

- Nested directory tree reflecting content structure
- All folder levels are collapsible
- Clicking folder name navigates to folder index page
- Clicking collapse toggle expands/collapses children

### Generated Folder Index Pages

Each folder automatically gets an index page listing its contents:
- Child pages shown with: title (linked), modified date, tags
- Child folders shown as links to their index pages
- If folder contains `index.md`:
  - Use its frontmatter for page title/metadata
  - Render its content after the generated listing
- If no `index.md`: use folder name as title

### Nav Label Resolution

Display name for folders in nav, resolved in order:
1. Config override (`[nav.labels]`)
2. Folder's `index.md` frontmatter `title`
3. Folder name (titlecased)

## Configuration

```toml
[nav]
default_state = "collapsed"  # or "expanded"
hide = ["/private", "/drafts", "/.obsidian"]

[nav.labels]
"/characters" = "Cast"
"/locations" = "Places"
```

**Options:**
- `default_state`: Initial collapse state for folders ("collapsed" or "expanded")
- `hide`: Paths to exclude from nav (also excludes from folder listings)
- `labels`: Override display names for specific paths

## Implementation Steps

### 1. Nav Tree Builder (`nav/tree.py`)

Build tree structure from content:

```python
@dataclass
class NavNode:
    name: str           # folder/file name
    path: str           # URL path
    label: str          # display name (resolved)
    is_folder: bool
    children: list[NavNode]

def build_nav_tree(pages: list[Page], config: NavConfig) -> NavNode:
    # Build tree from page paths
    # Apply hide filters
    # Resolve labels
    ...
```

### 2. Folder Index Generator (`content/folder_index.py`)

Generate index pages for folders:

```python
@dataclass
class FolderIndex:
    path: str
    title: str
    custom_content: str | None  # from index.md if exists
    children: list[FolderChild]

@dataclass
class FolderChild:
    title: str
    path: str
    modified: datetime
    tags: list[str]
    is_folder: bool

def generate_folder_indexes(pages: list[Page], config: Config) -> list[FolderIndex]:
    ...
```

### 3. Nav Templates (`templates/components/nav.html`)

```html
<nav class="sidebar">
  {% macro render_node(node, default_state) %}
  <li>
    {% if node.is_folder %}
    <details {{ 'open' if default_state == 'expanded' else '' }}>
      <summary>
        <a href="{{ node.path }}">{{ node.label }}</a>
      </summary>
      <ul>
        {% for child in node.children %}
          {{ render_node(child, default_state) }}
        {% endfor %}
      </ul>
    </details>
    {% else %}
    <a href="{{ node.path }}">{{ node.label }}</a>
    {% endif %}
  </li>
  {% endmacro %}

  <ul>
    {% for node in nav.children %}
      {{ render_node(node, nav_config.default_state) }}
    {% endfor %}
  </ul>
</nav>
```

### 4. Folder Index Template (`templates/folder_index.html`)

```html
{% extends "base.html" %}
{% block content %}
<article>
  <h1>{{ folder.title }}</h1>

  <table class="folder-listing">
    <thead>
      <tr>
        <th>Title</th>
        <th>Modified</th>
        <th>Tags</th>
      </tr>
    </thead>
    <tbody>
      {% for child in folder.children %}
      <tr>
        <td><a href="{{ child.path }}">{{ child.title }}</a></td>
        <td>{{ child.modified | date }}</td>
        <td>{{ child.tags | join(', ') }}</td>
      </tr>
      {% endfor %}
    </tbody>
  </table>

  {% if folder.custom_content %}
  <div class="folder-content">
    {{ folder.custom_content | safe }}
  </div>
  {% endif %}
</article>
{% endblock %}
```

### 5. Integrate with Build (`output/builder.py`)

- Build nav tree before rendering pages
- Pass nav tree to all page templates
- Generate folder index pages

### 6. Breadcrumb Generator (`nav/breadcrumbs.py`)

```python
@dataclass
class Breadcrumb:
    label: str
    path: str

def build_breadcrumbs(page_path: str, nav_tree: NavNode) -> list[Breadcrumb]:
    # Split path into segments
    # Resolve labels from nav tree
    # Return list from root to current page
    ...
```

### 7. Breadcrumb Template (`templates/components/breadcrumbs.html`)

```html
<nav class="breadcrumbs" aria-label="Breadcrumb">
  <ol>
    {% for crumb in breadcrumbs %}
    <li>
      {% if not loop.last %}
      <a href="{{ crumb.path }}">{{ crumb.label }}</a>
      {% else %}
      <span aria-current="page">{{ crumb.label }}</span>
      {% endif %}
    </li>
    {% endfor %}
  </ol>
</nav>
```

### 8. Update Base Template

Add nav and breadcrumb components to `base.html` layout.

## Test Plan

1. **Nav tree building:** Verify tree structure from test content
2. **Label resolution:** Config override > frontmatter > folder name
3. **Hide paths:** Excluded paths not in nav or listings
4. **Folder indexes:** Generated with correct children
5. **Custom index content:** Renders after listing when index.md exists
6. **Breadcrumbs:** Correct path segments with resolved labels
7. **Integration:** Build test vault, verify nav, breadcrumbs, and folder pages

## Out of Scope

- Per-page TOC
- Search integration in nav
- Drag-and-drop reordering
- Saved collapse state (localStorage)

## Success Criteria

Building a test vault produces:
- Breadcrumbs on all pages showing path hierarchy
- Sidebar nav on all pages with collapsible folder tree
- Folder index pages with child listings
- Config overrides for labels and hidden paths work
- Folder index.md content appears after generated listing
