import os
import filecmp
import difflib
from datetime import datetime

def get_most_recent_backup_dir():
    backup_base_dir = "backup_web"
    backup_dirs = [os.path.join(backup_base_dir, d) for d in os.listdir(backup_base_dir) if os.path.isdir(os.path.join(backup_base_dir, d))]
    if not backup_dirs:
        print("No backup directories found.")
        return None
    most_recent_backup_dir = max(backup_dirs, key=os.path.getmtime)
    return most_recent_backup_dir

def compare_files(file1, file2):
    with open(file1, 'r') as f1, open(file2, 'r') as f2:
        f1_lines = f1.readlines()
        f2_lines = f2.readlines()
        diff = difflib.unified_diff(f1_lines, f2_lines, fromfile=file1, tofile=file2, lineterm='')
        for line in diff:
            print(line)

def compare_directories(dir1, dir2):
    comparison = filecmp.dircmp(dir1, dir2)
    print(f"Comparing {dir1} and {dir2}")
    comparison.report()
    if comparison.diff_files:
        print(f"Different files: {comparison.diff_files}")
        for diff_file in comparison.diff_files:
            compare_files(os.path.join(dir1, diff_file), os.path.join(dir2, diff_file))
    if comparison.left_only:
        print(f"Files only in {dir1}: {comparison.left_only}")
    if comparison.right_only:
        print(f"Files only in {dir2}: {comparison.right_only}")
    if comparison.common_dirs:
        for common_dir in comparison.common_dirs:
            compare_directories(os.path.join(dir1, common_dir), os.path.join(dir2, common_dir))

def main():
    most_recent_backup_dir = get_most_recent_backup_dir()
    if not most_recent_backup_dir:
        return

    backup_templates_dir = os.path.join(most_recent_backup_dir, "templates")
    backup_static_dir = os.path.join(most_recent_backup_dir, "static")

    if os.path.exists(backup_templates_dir) and os.path.exists("templates"):
        compare_directories(backup_templates_dir, "templates")
    else:
        print("Templates directory not found in backup or project root.")

    if os.path.exists(backup_static_dir) and os.path.exists("static"):
        compare_directories(backup_static_dir, "static")
    else:
        print("Static directory not found in backup or project root.")

if __name__ == "__main__":
    main()