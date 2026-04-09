"""
Metadata and ZIP packaging for AEF export.
"""

import json
import os
import hashlib
import zipfile
from datetime import datetime
from .constants import APP_VERSION


def create_metadata(metadata_file_path, data_file_path, attached_entity, mode):
    """Create metadata.json with checksum and info."""
    sha256 = hashlib.sha256()
    with open(data_file_path, 'rb') as f:
        sha256.update(f.read())

    metadata = {
        'version': APP_VERSION,
        'checksum': sha256.hexdigest(),
        'date': datetime.now().isoformat(),
        'producer': 'Archimista Python Exporter',
        'attached_entity': attached_entity,
        'mode': mode,
    }

    with open(metadata_file_path, 'w', encoding='utf-8') as f:
        # Ruby reads metadata line-by-line (NDJSON), must be single line
        json.dump(metadata, f, ensure_ascii=False, separators=(',', ':'))


def create_zip(zip_file_path, data_file_path, metadata_file_path):
    """Create the .aef ZIP package with data.json and metadata.json."""
    with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.write(data_file_path, 'data.json')
        zf.write(metadata_file_path, 'metadata.json')


def add_files_to_zip(zf, data_file_path, metadata_file_path, extra_files=None):
    """Add files to an existing ZIP handle."""
    zf.write(data_file_path, 'data.json')
    zf.write(metadata_file_path, 'metadata.json')
    if extra_files:
        for arc_name, file_path in extra_files:
            zf.write(file_path, arc_name)
