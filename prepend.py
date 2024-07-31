# prepend.py
import os

def clean_and_prepend_file_path(directory='.'):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py') and not file.startswith('__init__'):
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, directory)
                expected_first_line = f'# {relative_path}'

                with open(file_path, 'r') as f:
                    lines = f.readlines()

                # Remove any existing path comments at the beginning
                while lines and lines[0].strip().startswith('# ') and '/' in lines[0] or '\\' in lines[0]:
                    lines.pop(0)

                # Ensure the correct path line is at the beginning
                if not lines or lines[0].strip() != expected_first_line:
                    lines.insert(0, expected_first_line + '\n')
                    print(f"Updated {relative_path}")
                else:
                    print(f"Skipping {relative_path}: Already has correct path")

                # Write the cleaned and corrected content back to the file
                with open(file_path, 'w') as f:
                    f.writelines(lines)

if __name__ == '__main__':
    clean_and_prepend_file_path()
    print("File paths have been cleaned and prepended to all non-init .py files (where necessary).")