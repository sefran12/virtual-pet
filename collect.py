import os

def collect_py_contents(root_dir):
    contents = []
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.py') and file != '__init__.py':
                file_path = os.path.join(root, file)
                with open(file_path, 'r') as f:
                    contents.append(f.read())
    return contents

def write_contents_to_file(contents, output_file):
    with open(output_file, 'w') as f:
        f.write('\n\n'.join(contents))

if __name__ == '__main__':
    script_dir = os.path.dirname(os.path.abspath(__file__))
    contents = collect_py_contents(script_dir)
    write_contents_to_file(contents, 'py_contents.txt')
    print(f"Contents of {len(contents)} Python files have been written to py_contents.txt")