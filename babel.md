install
``` bash
pip install flask-babel
```
```python
from flask_babel import Babel

def get_locale():
    # if a user is logged in, use the locale from the user settings
    user = getattr(g, 'user', None)
    if user is not None:
        return user.locale
    # otherwise try to guess the language from the user accept
    # header the browser transmits.  We support de/fr/en in this
    # example.  The best match wins.
    return request.accept_languages.best_match(['de', 'fr', 'en'])

def get_timezone():
    user = getattr(g, 'user', None)
    if user is not None:
        return user.timezone

babel = Babel(app, locale_selector=get_locale, timezone_selector=get_timezone)
```

using translation 

```python
from flask_babel import gettext, ngettext, lazy_gettext

class MyForm(formlibrary.FormBase):
    success_message = lazy_gettext(u'The form was successfully saved.')

gettext(u'A simple string')
gettext(u'Value: %(value)s', value=42)
ngettext(u'%(num)s Apple', u'%(num)s Apples', number_of_apples)
```

create a 'babel.cfg' file
```cfg
[python: **.py]
[jinja2: **/templates/**.html]
```
files to compile

```bash
pybabel extract -F chrono_des_vignes/babel.cfg -k lazy_gettext -o chrono_des_vignes/messages.pot .
```

create a po file for each language (de in this example)
```bash
pybabel init -i chrono_des_vignes/messages.pot -d chrono_des_vignes/translations -l de
```

after editing this file compile the traslations
```bash
pybabel compile -d chrono_des_vignes/translations
```

when string change :

* update the cfg file
* create a new messages.pot
```bash
pybabel extract -F chrono_des_vignes/babel.cfg -k lazy_gettext -o chrono_des_vignes/messages.pot .
```
* uptadte all po files and copliled files
```bash
pybabel update -i chrono_des_vignes/messages.pot -d chrono_des_vignes/translations
```

after editing this file compile the traslations
```bash
pybabel compile -d chrono_des_vignes/translations
```


## dev must do 

* display all languages
* add language
* change translation
* updates cfg and pot and all translations
