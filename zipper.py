import os, zipfile, fnmatch

def match_any(path: str, patterns:list[str]):
    for pattern in patterns:
        if fnmatch.fnmatch(path, pattern):# path.startswith(pattern) or pattern in path:
            return True
    return False

def should_include(path: str, include_list:list[str], exclude_list:list[str], include_files:list[str], exclude_files:list[str]):
    if match_any(path, include_files) and not match_any(path, exclude_files):
        return True
    if match_any(path, include_list) and not match_any(path, exclude_list):
        return True
    return False

def zip_release(zip_filename:str, include_paths:list[str], exclude_paths:list[str], include_files:list[str], exclude_files:list[str]):
    include_paths = [ f'*{f}*' for f in include_paths ]
    exclude_paths = [ f'*{f}*' for f in exclude_paths ]
    include_files = [ f'*{f}' for f in include_files ]
    exclude_files = [ f'*{f}' for f in exclude_files ]
    with zipfile.ZipFile(os.path.abspath(zip_filename), 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk('.'):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, '.')

                if should_include(rel_path, include_paths, exclude_paths, include_files, exclude_files):
                    zipf.write(full_path, rel_path)
                    print(f"✔ Inclus : {rel_path}")
                #else:
                #    print(f"✘ Exclu : {rel_path}")

if __name__ == '__main__':
    # === À personnaliser selon ton projet ===
    nom_fichier_zip = "release.zip"

    # Dossiers/fichiers à inclure (chemins relatifs depuis la racine du projet)
    inclure_folders = [
        "chrono_des_vignes",
    ]

    include_files = [
        r'profil_pics\icone.png',
    ]

    # Dossiers/fichiers à exclure (tout ce qui correspond sera ignoré)
    exclure_folders = [
        "__pycache__",
        "dev",
        r"translations\ids",
        r"translations\pseudo",
        r"doc\docs",
        'profil_pics',
    ]

    exclude_files = [
        ".git",
        ".env",
        ".venv",
        "requirements.txt",
        "mkdocs.yml",
    ]

    # build the documentatio before zipping the release
    os.system(r'mkdocs build -f "chrono_des_vignes\templates\doc\mkdocs.yml"')

    zip_release(nom_fichier_zip, inclure_folders, exclure_folders, include_files, exclude_files)
