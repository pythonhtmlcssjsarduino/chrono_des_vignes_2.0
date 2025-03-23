# chrono des vignes
chrono des vignes is a web app made in python and the [Flask](https://pypi.org/project/Flask/) framwork for the back-end and the html, javascript for the front-end

## build the app
to build the app you need to 
- rebuild the .venv from the requirement.txt
- open a terminal with the virtual environment
- launch the server with
    ```shell
    $env:FLASK_DEBUG = 1;$env:FLASK_APP = "chrono_des_vignes";flask run --extra-files flask-app/templates/:flask_app/translations/```