#helpers.py
import os
import pandas as pd
from flask import abort, url_for

# -----------------
# Helper functions
# -----------------
def load_excel(file_path, sheets=None):
    """
    Load links from an Excel workbook.
    - If `sheets` is None: loads all sheets.
    - If `sheets` is a list: loads only those sheets.
    Returns: list of dicts with all link rows.
    """
    if not os.path.exists(file_path):
        abort(404, description=f"File not found: {file_path}")

    # Load workbook once
    xls = pd.ExcelFile(file_path)
    all_links = []

    # Decide which sheets to load
    if sheets is None:
        sheets = xls.sheet_names

    for sheet_name in sheets:
        if sheet_name not in xls.sheet_names:
            print(f"[WARN] Sheet '{sheet_name}' not found in workbook, skipping.")
            continue

        df = pd.read_excel(xls, sheet_name=sheet_name)
        df = df.fillna('')
        
        # ✅ Ensure a Team column exists (fallback to sheet name)
        if 'Team' not in df.columns:
            df['Team'] = sheet_name
        else:
            df['Team'] = df['Team'].replace('', sheet_name)

        all_links.extend(df.to_dict(orient='records'))

    return all_links


def _process_url(link):
    url = (link.get('URL') or '').strip()

    if not url:
        link['href'] = '#'
        link['target'] = '_self'
        return

    # If full protocol → external
    if url.startswith(('http://', 'https://')):
        link['href'] = url
        link['target'] = '_blank'
        return

    # If looks like a domain → assume https
    if '.' in url and ' ' not in url:
        link['href'] = 'https://' + url
        link['target'] = '_blank'
        return

    # Otherwise treat as internal team route
    link['href'] = url_for('team_page', team_name=url.strip('/'))
    link['target'] = '_self'


from flask import current_app

def _detect_icon(icon_name, logo_folder):
    if not icon_name:
        return url_for('static', filename='data/logo/default.png')

    # Get absolute static folder path
    static_path = current_app.static_folder
    base_path = os.path.join(static_path, "data", "logo", icon_name)

    for ext in ["png", "jpg", "jpeg", "svg", "webp"]:
        full_path = f"{base_path}.{ext}"
        if os.path.isfile(full_path):
            return url_for('static', filename=f"data/logo/{icon_name}.{ext}")

    return url_for('static', filename='data/logo/default.png')


def prepare_links(links):
    logo_folder = "static/data/logo"
    preview_folder = "static/data/app-screen"

    for link in links:
        _process_url(link)

        # ---- Logo ----
        icon_name = (link.get("Icon") or "").strip()
        link["logo"] = _detect_icon(icon_name, logo_folder)

        # ---- Title (normalized once) ----
        link["title"] = (link.get("Team / Title") or "").strip()

        # ---- Description ----
        link["description"] = (link.get("description") or "").strip()

        # ---- Preview image ----
        preview_name = (link.get("preview") or "").strip()
        link["preview_image"] = _detect_preview(
            preview_name,
            preview_folder
        )

        # ---- Public flag (boolean, not vibes) ----
        link["is_public"] = str(link.get("is_public", "")).lower() in {
            "1", "true", "yes", "y"
        }

    return links



def _detect_preview(preview_name, preview_folder):
    from flask import current_app

    if not preview_name:
        return url_for('static', filename='data/app-screen/default.png')

    static_path = current_app.static_folder
    base_path = os.path.join(static_path, "data", "app-screen", preview_name)

    if os.path.isfile(base_path):
        return url_for('static', filename=f"data/app-screen/{preview_name}")

    for ext in ["png", "jpg", "jpeg", "webp"]:
        full_path = f"{base_path}.{ext}"
        if os.path.isfile(full_path):
            return url_for('static', filename=f"data/app-screen/{preview_name}.{ext}")

    return url_for('static', filename='data/app-screen/default.png')
