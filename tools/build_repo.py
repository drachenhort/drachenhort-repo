"""Build the Kodi addon repository under docs/ from the addons listed below.

Regenerates docs/addons.xml, docs/addons.xml.md5, and per-addon zips. Run
directly (`python tools/build_repo.py`) or import build_repo() for tests.
Deliberately free of xbmc* imports so it runs under plain Python/CI.
"""

import hashlib
import os
import shutil
import xml.etree.ElementTree as ET
import zipfile


def get_addon_version(source_dir):
    return ET.parse(os.path.join(source_dir, "addon.xml")).getroot().attrib["version"]


def iter_addon_files(source_dir, includes, addon_id):
    names = includes if includes is not None else sorted(os.listdir(source_dir))
    for name in names:
        full_path = os.path.join(source_dir, name)
        if os.path.isdir(full_path):
            for dirpath, dirnames, filenames in os.walk(full_path):
                dirnames[:] = [d for d in dirnames if d != "__pycache__"]
                for filename in filenames:
                    file_path = os.path.join(dirpath, filename)
                    arcname = os.path.join(addon_id, os.path.relpath(file_path, source_dir))
                    yield file_path, arcname
        else:
            yield full_path, os.path.join(addon_id, name)


def build_addon_zip(source_dir, includes, addon_id, version, output_dir):
    zip_path = os.path.join(output_dir, "{}-{}.zip".format(addon_id, version))
    os.makedirs(output_dir, exist_ok=True)
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path, arcname in iter_addon_files(source_dir, includes, addon_id):
            zf.write(file_path, arcname)
    return zip_path


def copy_icon(source_dir, output_dir):
    icon_path = os.path.join(source_dir, "icon.png")
    if os.path.isfile(icon_path):
        os.makedirs(output_dir, exist_ok=True)
        shutil.copyfile(icon_path, os.path.join(output_dir, "icon.png"))


def build_addons_xml(source_dirs, docs_dir):
    root = ET.Element("addons")
    for source_dir in source_dirs:
        addon_root = ET.parse(os.path.join(source_dir, "addon.xml")).getroot()
        root.append(addon_root)
    os.makedirs(docs_dir, exist_ok=True)
    addons_xml_path = os.path.join(docs_dir, "addons.xml")
    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ")
    tree.write(addons_xml_path, encoding="UTF-8", xml_declaration=True)
    return addons_xml_path


def write_addons_xml_md5(addons_xml_path):
    with open(addons_xml_path, "rb") as f:
        digest = hashlib.md5(f.read()).hexdigest()
    md5_path = addons_xml_path + ".md5"
    with open(md5_path, "w", encoding="utf-8") as f:
        f.write(digest)
    return md5_path


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS_DIR = os.path.join(REPO_ROOT, "docs")

ADDONS = [
    {
        "id": "script.twitch.center",
        "source_dir": os.path.join(REPO_ROOT, "addons", "twitch-center"),
        "includes": ["addon.xml", "addon.py", "icon.png", "lib", "resources"],
    },
    {
        "id": "script.jellyfin.plex",
        "source_dir": os.path.join(REPO_ROOT, "addons", "jellyfin-kodi-plex"),
        "includes": ["addon.xml", "default.py", "service.py", "icon.png", "lib", "resources"],
    },
    {
        "id": "repository.drachenhort",
        "source_dir": os.path.join(REPO_ROOT, "repository.drachenhort"),
        "includes": None,
    },
]


def build_repo(addons, docs_dir):
    for addon in addons:
        version = get_addon_version(addon["source_dir"])
        output_dir = os.path.join(docs_dir, addon["id"])
        build_addon_zip(
            addon["source_dir"], addon["includes"], addon["id"], version, output_dir
        )
        copy_icon(addon["source_dir"], output_dir)
    build_addons_xml([addon["source_dir"] for addon in addons], docs_dir)
    write_addons_xml_md5(os.path.join(docs_dir, "addons.xml"))


if __name__ == "__main__":
    build_repo(ADDONS, DOCS_DIR)
