from flask_app import db, app
from datetime import datetime
from flask_app.models import User, Event, Edition, Parcours, Inscription, Stand, Trace
with app.app_context():
    db.drop_all()
    db.create_all()

    # users
    user = User(name='romain', lastname='Maurer', password='12345', username='romain.maurer', phone='0774428642', datenaiss=datetime(year=2007,month=7, day=28), creation_date=datetime(year=2023,month=9, day=21), admin=True)
    moi = User(name='moi', lastname='je', password='moije', username='moi.je', datenaiss=datetime(year=2007,month=7, day=28))
    toi = User(name='toi', lastname='tu', password='toitu', username='toi.tu', datenaiss=datetime(year=2007,month=7, day=28))
    lui = User(name='lui', lastname='il', password='luiil', username='lui.il', datenaiss=datetime(year=2007,month=7, day=28))
    eux = User(name='eux', lastname='ils', password='euxils', username='eux.ils', datenaiss=datetime(year=2007,month=7, day=28), email='eux.ils@text.ch')
    db.session.add_all([user, moi, toi, lui, eux])
    db.session.commit()

    # events
    cdv = Event(creation_date=datetime(day=23, month=4, year=2022), name='course des vignes', createur=user)
    db.session.add_all([cdv])

    db.session.commit()
    # editions
    e2020= Edition(name='2020',edition_date= datetime(year=2024,month=10, day=28), first_inscription=datetime(year=2020,month=8, day=28), last_inscription=datetime(year=2020,month=9, day=28) , event=cdv)
    e2021= Edition(name='2021',edition_date= datetime(year=2025,month=10, day=28), first_inscription=datetime(year=2021,month=8, day=28), last_inscription=datetime(year=2021,month=9, day=28), event=cdv)
    e2022= Edition(name='2022',edition_date= datetime(year=2026,month=10, day=28), first_inscription=datetime(year=2022,month=8, day=28), last_inscription=datetime(year=2022,month=9, day=28), event=cdv)
    e2023= Edition(name='2023',edition_date= datetime(year=2027,month=10, day=28), first_inscription=datetime(year=2023,month=8, day=28), last_inscription=datetime(year=2023,month=9, day=28), event=cdv)
    db.session.add_all([e2020, e2021, e2022, e2023])

    db.session.commit()
    # parcours
    a=Parcours(name='A', event=cdv)
    b=Parcours(name='B', event=cdv)
    c=Parcours(name='C', event=cdv)
    w=Parcours(name='W', event=cdv)
    q=Parcours(name='Q', event=cdv)
    db.session.add_all([a,b,c,w, q])

    db.session.commit()
    # coureurs
    '''a = Inscription(inscrit=moi, event=cdv, parcours=a, edition=e2020)
    b = Inscription(inscrit=toi, event=cdv, parcours=b, edition=e2020)
    c = Inscription(inscrit=lui, event=cdv, parcours=c, edition=e2020)
    d = Inscription(inscrit=eux, event=cdv, parcours=w, edition=e2020)
    e = Inscription(inscrit=toi, event=cdv, parcours=a, edition=e2023)
    '''
    a = Inscription(inscrit=moi, event=cdv, edition=e2020, parcours_id=1)
    b = Inscription(inscrit=toi, event=cdv, edition=e2020, parcours_id=2)
    c = Inscription(inscrit=lui, event=cdv, edition=e2020, parcours_id=3)
    d = Inscription(inscrit=eux, event=cdv, edition=e2020, parcours_id=4)
    e = Inscription(inscrit=toi, event=cdv, edition=e2023, parcours_id=1)
    f = Inscription(inscrit=moi, event=cdv, edition=e2023, parcours_id=2)
    g = Inscription(inscrit=moi, event=cdv, edition=e2022, parcours_id=2)
    
    db.session.add_all([a,b,c,d,e, f,g])

    stand = Stand(name='start', parcours_id=1, lat=46.54542398593088, lng=6.447682455182076, chrono=1, start_stand=1, elevation=534)
    stand2 = Stand(name='vignes', parcours_id=1, lat=46.54542882844609, lng=6.446514353156091, elevation=534)
    stand3 = Stand(name='reverolle', parcours_id=1, lat=46.54074614505775, lng=6.444050073623658, elevation=544)
    stand4 = Stand(name='end', parcours_id=1, lat=46.5402207996225, lng=6.444866806268693, chrono=1, end_stand=1, elevation=544)
    db.session.add_all([stand, stand2, stand3, stand4])

    trace = Trace(name='1', parcours_id=1, start_id = 1, end_id = 2, turn_nb=1)
    trace2 =  Trace(name='2', parcours_id=1, start_id = 2, end_id = 3, turn_nb=1)
    trace3 =  Trace(name='3', parcours_id=1, start_id = 3, end_id = 4, turn_nb=1)
    trace4 =  Trace(name='4', parcours_id=1, start_id = 4, end_id = 1, trace=str([[46.54115202742685, 6.446485519409181, 516.0]]), turn_nb=1)
    trace5 =  Trace(name='5', parcours_id=1, start_id = 1, end_id = 4, turn_nb=2)
    #trace6 =  Trace(name='6', parcours_id=1, start_id = 4, end_id = 2, turn_nb=2)

    db.session.add_all([trace, trace2, trace3,trace4, trace5])#, trace5, trace6

    db.session.commit()

'''
parcours = [Parcours(name='A'), Parcours(name='B'), Parcours(name='C'), Parcours(name='W')]
coureurs = [Inscription(name='moi'), Inscription(name='toi'), Inscription(name='il'), Inscription(name='ils')]
editions = [Edition(name='2020', inscriptions=coureurs), Edition(name='2021', inscriptions=coureurs), Edition(name='2022', inscriptions=coureurs), Edition(name='2023', inscriptions=coureurs)]
events = {'course des vignes':Event(id=0, creation_date=datetime(day=23, month=4, year=2022), name='course des vignes', rdv_lat=0.0, rdv_lng=0.0, parcours=parcours, editions=editions, inscrits=coureurs)}

users={'romain.maurer':User(name='romain', lastname='Maurer', password='12345', username='romain.maurer', phone='0774428642', datenaiss=datetime(year=2007,month=7, day=28), id=0, creation_date=datetime(year=2023,month=9, day=21), admin=True, creations=[events['course des vignes']])}
'''
