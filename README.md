# chrono des vignes
chrono des vignes est une web app codée en python avec le framework [Flask](https://pypi.org/project/Flask/) pour le back-end et html javascript pour le front-end

## lancer le serveur 
pour lancer le serveur flask il vous faut d'abord lancer l'environement virtuel(venv) 
```bash
.venv/Scripts/Activate.ps1
```

puis lancer le serveur
```bash
flask --app chrono_des_vignes run --debug --extra-files flask-app/templates/:chrono_des_vignes/translations/ 
```

## documentation mkdocs

### serveur de developpement
commencer par [ouvrire l'environement virtuel](#lancer-le-serveur)

puis rentrer dans le dossier de la documentation 
```bash
cd chrono_des_vignes/templates/doc
```
puis lancer le serveur
``` bash
mkdocs serve
```
### construire la documentation
[lancer l'environement](#lancer-le-serveur) et [rentrer dans le dossier de la documentation](#serveur-de-developpement)
puis construire la documentation
```bash
mkdocs build
```