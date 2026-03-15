import os
import zipfile
from pathlib import Path

# 技能根目录
base = Path(r'C:/Users/wang20/.openclaw/workspace/skills/clawphone')

# 需要包含的文件/目录（clean 版本）
include = [
    'README.md',
    'CHANGELOG.md',
    'SKILL.md',
    'skill.yaml',
    'LICENSE',
    'adapter/',
    'core/',
    'examples/',
    'tests/',
    'migrate_phase2.py',
]

# 排除列表（临时文件、日志、数据库等）
exclude = [
    'phonebook.db',
    '__pycache__',
    '.git',
    'temp_',
    'logs/',
    'reports/',
]

# 创建 ZIP
zip_name = 'clawphone-v1.2.0-clean.zip'
zip_path = base / zip_name

with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
    for item in include:
        item_path = base / item
        if item_path.is_dir():
            for root, dirs, files in os.walk(item_path):
                # 排除指定目录
                dirs[:] = [d for d in dirs if not any(excl in d for excl in exclude)]
                for file in files:
                    if any(excl in file for excl in exclude):
                        continue
                    full_path = Path(root) / file
                    arc_name = full_path.relative_to(base)
                    zf.write(full_path, arc_name)
        elif item_path.is_file():
            zf.write(item_path, item)

print(f"[OK] 创建发布包: {zip_path}")
print(f"      大小: {zip_path.stat().st_size / 1024:.1f} KB")