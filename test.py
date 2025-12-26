import os
import argparse
import tkinter as tk
from tkinter import filedialog

INPUT_PATH = os.getcwd()
OUTPUT_PATH = os.path.join(os.getcwd(), "summary.txt")

DEFAULT_IGNORE_DIRS = {'.git', '_pycache_', 'venv', '.vscode', '.idea', 'node_modules', 'build', 'dist'}
DEFAULT_IGNORE_FILES = {'.DS_Store'}
DEFAULT_IGNORE_EXTENSIONS = {'.pyc', '.log', '.tmp', '.bak', '.swp'}

def generate_project_summary(input_path=INPUT_PATH, output_path=OUTPUT_PATH):
    if not input_path or not os.path.isdir(input_path):
        print(f"Error: Invalid path '{input_path}'")
        return

    project_structure = []
    python_files_content = []
    yaml_files_content = []

    abs_project_path = os.path.abspath(input_path)
    project_root_name = os.path.basename(abs_project_path)

    for dirpath, dirnames, filenames in os.walk(abs_project_path, topdown=True):
        dirnames[:] = [d for d in dirnames if d not in DEFAULT_IGNORE_DIRS]

        relative_dir = os.path.relpath(dirpath, abs_project_path)
        level = relative_dir.count(os.sep) if relative_dir != '.' else 0
        indent = '    ' * level + '|-- '

        if relative_dir == '.':
            project_structure.append(f"{project_root_name}/")
        else:
            if not any(ignored in relative_dir.split(os.sep) for ignored in DEFAULT_IGNORE_DIRS):
                project_structure.append(f"{indent}{os.path.basename(dirpath)}/")

        sub_indent = '    ' * (level + 1) + '|-- '
        dirnames.sort()
        filenames.sort()

        for filename in filenames:
            if filename in DEFAULT_IGNORE_FILES:
                continue
            if os.path.splitext(filename)[1] in DEFAULT_IGNORE_EXTENSIONS:
                continue

            if not any(ignored in os.path.join(relative_dir, filename).split(os.sep) for ignored in DEFAULT_IGNORE_DIRS):
                project_structure.append(f"{sub_indent}{filename}")

            if filename.endswith(('.py', '.yaml')):
                file_path = os.path.join(dirpath, filename)
                relative_file_path = os.path.relpath(file_path, abs_project_path)

                if not any(ignored in relative_file_path.split(os.sep) for ignored in DEFAULT_IGNORE_DIRS):
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()

                        if filename.endswith('.py'):
                            python_files_content.append((relative_file_path, content))
                        elif filename.endswith('.yaml'):
                            yaml_files_content.append((relative_file_path, content))

                    except Exception as e:
                        if filename.endswith('.py'):
                            python_files_content.append((relative_file_path, f"Error reading file: {e}"))
                        elif filename.endswith('.yaml'):
                            yaml_files_content.append((relative_file_path, f"Error reading file: {e}"))

    try:
        with open(output_path, 'w', encoding='utf-8') as outfile:
            outfile.write("=========================================\n")
            outfile.write(" PROJECT DIRECTORY STRUCTURE\n")
            outfile.write("=========================================\n\n")
            outfile.write(f"Root directory: {abs_project_path}\n\n")
            outfile.write('\n'.join(project_structure))
            outfile.write("\n\n=========================================\n")
            outfile.write(" PYTHON FILES CONTENT (.py)\n")
            outfile.write("=========================================\n\n")

            python_files_content.sort(key=lambda item: item[0])

            for rel_path, content in python_files_content:
                outfile.write(f"--- File: {rel_path} ---\n")
                outfile.write(content)
                outfile.write("\n\n----------------------------------------\n\n")

            if yaml_files_content:
                outfile.write("\n\n=========================================\n")
                outfile.write(" YAML FILES CONTENT (.yaml)\n")
                outfile.write("=========================================\n\n")

                yaml_files_content.sort(key=lambda item: item[0])
                for rel_path, content in yaml_files_content:
                    outfile.write(f"--- File: {rel_path} ---\n")
                    outfile.write(content)
                    outfile.write("\n\n----------------------------------------\n\n")

    except Exception as e:
        print(f"Error writing output file: {e}")

if __name__ == "__main__":
    generate_project_summary()