# Chrono des Vignes
Chrono des Vignes is a timing system for sports events. It allows event organizers to manage events, editions, courses, and runners, and track times and results.

## Features
* Event management: create and manage events, editions, and courses
* Runner management: track runner information and results
* Time tracking: track times and results for each runner
* Multilingual support: supports French, English and German languages

## Getting Started
To get started with Chrono des Vignes, please follow these steps:

1. Rebuild the virtual environment from the `requirements.txt` file
2. Open a terminal with the virtual environment
3. Launch the server with the following command:
    ```shell
    $env:FLASK_DEBUG = 1;$env:FLASK_APP = "chrono_des_vignes";flask run --extra-files flask-app/templates/:flask_app/translations/```

## Live Demo
Experience Chrono des Vignes in action by visiting our [Deployed version](https://chronodesvignes.eu.pythonanywhere.com/).

## Documentation
For detailed usage instructions, please refer to our [Documentation](chrono_des_vignes/templates/doc).
