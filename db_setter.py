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
    eux = User(name='eux', lastname='ils', password='euxils', username='eux.ils', datenaiss=datetime(year=2007,month=7, day=28))
    db.session.add_all([user, moi, toi, lui, eux])
    db.session.commit()

    # events
    cdv = Event(creation_date=datetime(day=23, month=4, year=2022), name='course des vignes', createur=user)
    db.session.add_all([cdv])

    db.session.commit()
    # editions
    e2020= Edition(name='2020',edition_date= datetime(year=2020,month=10, day=28), first_inscription=datetime(year=2020,month=8, day=28), last_inscription=datetime(year=2020,month=9, day=28) , event=cdv)
    e2021= Edition(name='2021',edition_date= datetime(year=2021,month=10, day=28), first_inscription=datetime(year=2021,month=8, day=28), last_inscription=datetime(year=2021,month=9, day=28), event=cdv)
    e2022= Edition(name='2022',edition_date= datetime(year=2022,month=10, day=28), first_inscription=datetime(year=2022,month=8, day=28), last_inscription=datetime(year=2022,month=9, day=28), event=cdv)
    e2023= Edition(name='2023',edition_date= datetime(year=2023,month=10, day=28), first_inscription=datetime(year=2023,month=8, day=28), last_inscription=datetime(year=2023,month=9, day=28), event=cdv)
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
    
    db.session.add_all([a,b,c,d,e])

    stand = Stand(name='coucou', lat=46.58, lng=6.52, start_stand=1)
    stand2 = Stand(name='salut', lat=40.58, lng=3.52)
    stand3 = Stand(name='dafsd', lat=43.58, lng=0.52)
    stand4 = Stand(name='fdsgdsf', lat=45.58, lng=3.52)
    db.session.add_all([stand, stand2, stand3, stand4])

    trace = Trace(name='1', start_id = 1, end_id = 2, turn_nb=1)
    trace2 =  Trace(name='2', start_id = 2, end_id = 3, turn_nb=1)
    trace3 =  Trace(name='3', start_id = 3, end_id = 4, turn_nb=1)
    trace4 =  Trace(name='4', start_id = 4, end_id = 1, trace=str([[44, 7]]), turn_nb=1)
    trace5 =  Trace(name='5', start_id = 1, end_id = 4, turn_nb=2)

    db.session.add_all([trace, trace2, trace3,trace4, trace5])

    db.session.commit()

'''
parcours = [Parcours(name='A'), Parcours(name='B'), Parcours(name='C'), Parcours(name='W')]
coureurs = [Inscription(name='moi'), Inscription(name='toi'), Inscription(name='il'), Inscription(name='ils')]
editions = [Edition(name='2020', inscriptions=coureurs), Edition(name='2021', inscriptions=coureurs), Edition(name='2022', inscriptions=coureurs), Edition(name='2023', inscriptions=coureurs)]
events = {'course des vignes':Event(id=0, creation_date=datetime(day=23, month=4, year=2022), name='course des vignes', rdv_lat=0.0, rdv_lng=0.0, parcours=parcours, editions=editions, inscrits=coureurs)}

users={'romain.maurer':User(name='romain', lastname='Maurer', password='12345', username='romain.maurer', phone='0774428642', datenaiss=datetime(year=2007,month=7, day=28), id=0, creation_date=datetime(year=2023,month=9, day=21), admin=True, creations=[events['course des vignes']])}
'''
