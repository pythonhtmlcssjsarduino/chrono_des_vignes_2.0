from flask import flash, redirect, url_for, render_template, request
from flask_app import app, admin_required, db
from flask_app.forms import Edition_form, Parcours_name_form, Etape_modif_form, Stand_modif_form
from flask_login import login_required, current_user
from flask_app.models import Edition, Parcours, Inscription, Event, Stand, Trace
from datetime import datetime
from folium import Map, Marker, Icon, PolyLine, Popup
from shapely.geometry import MultiPoint
from jinja2 import Template


@app.route('/event/<event_name>')
@login_required
@admin_required
def home_event(event_name):
    #* page to access and modify an event
    event_data = Event.query.filter_by(name=event_name).first()
    user = current_user
    return render_template("1-home_event.html", user_data=user, event_data=event_data)


@app.route('/event/<event_name>/editions')
@login_required
@admin_required
def editions(event_name):
    # * page to access the differents editions of the event
    event_data = Event.query.filter_by(name=event_name).first()
    user = current_user
    return render_template("1.1-editions.html", user_data=user, event_data=event_data)

@app.route('/event/<event_name>/editions/<edition_name>', methods=['POST', 'GET'])
@login_required
@admin_required
def modify_edition(event_name, edition_name):
    event = Event.query.filter_by(name=event_name).first()
    edition= event.editions.filter_by(name=edition_name).first()
    user = current_user
    form = Edition_form(data={'name':edition.name,
                              'edition_date':edition.edition_date,
                              'first_inscription':edition.first_inscription,
                              'last_inscription':edition.last_inscription,
                              'rdv_lat':edition.rdv_lat,
                              'rdv_lng':edition.rdv_lng})


    #? desactiver le champs si dates deja passé
    form.edition_date.render_kw.pop("disabled", None)
    form.first_inscription.render_kw.pop("disabled", None)
    form.last_inscription.render_kw.pop("disabled", None)
    if edition.edition_date < datetime.now():
        form.edition_date.render_kw["disabled"]= "disabled"
    if edition.first_inscription < datetime.now():
        form.first_inscription.render_kw["disabled"]= "disabled"
    if edition.last_inscription < datetime.now():
        form.last_inscription.render_kw["disabled"]= "disabled"
    #? fin desactivation des champds


    if form.validate_on_submit():
        edition.name = form.name.data
        edition.edition_date = form.edition_date.data
        edition.first_inscription = form.first_inscription.data
        edition.last_inscription = form.last_inscription.data
        edition.rdv_lat = form.rdv_lat.data
        edition.rdv_lng = form.rdv_lng.data
        db.session.commit()
        flash('l\'edition a bien été mise a jour.', 'success')

    return render_template('1.1.1-modify_edition.html', user_data=user, event_data=event, edition_data=edition, form = form)


@app.route('/event/<event_name>/parcours')
@login_required
@admin_required
def parcours(event_name):
    # * page to access the differents parcours of the event
    event_data = Event.query.filter_by(name=event_name).first()
    user = current_user
    return render_template("1.2-parcours.html", user_data=user, event_data=event_data)


@app.route('/event/<event_name>/parcours/<parcours_name>', methods=['POST', 'GET'])
@login_required
@admin_required
def modify_parcours(event_name, parcours_name):
    event = Event.query.filter_by(name=event_name).first()
    parcours= event.parcours.filter_by(name=parcours_name).first()
    user = current_user
    modif = request.args.get('modif', 'map')

    #? formulaire pour le nom du parcours
    name_form= Parcours_name_form(data={'name':parcours.name})
    if name_form.validate_on_submit():
        flash('name saved')
        return redirect(request.path)

    #? formulaire modifications
    if request.args.get('marker'):
        stand= Stand.query.filter_by(id=request.args.get('marker')).first()
        modif_form= Stand_modif_form(data={'name':stand.name, 'lat':stand.lat, 'lng':stand.lng, 'color':stand.color, 'chrono':stand.chrono})
    elif request.args.get('trace'):
        trace = Trace.query.filter_by(id=request.args.get('trace')).first()
        modif_form = Etape_modif_form(data={'name':trace.name})
    else:
        modif_form=None
    

    #? create the map
    program_list=[]
    marker_coordonee = []
    stands=set()

    start = parcours.start_stand
    map = Map(max_zoom=22, location=(0,0), zoom_start=5)
    new_stand=start
    # si aucun depart alors ne mettre aucun stand
    if start:
        popup = Popup()
        popup._template = Template("""
            var {{this.get_name()}} = L.popup({{ this.options|tojson }});
            {{ this._parent.get_name() }}.on("click", function() {on_marker_click(%s)})
            """%start.id)
        last_m=Marker((start.lat, start.lng),
                tooltip=start.name,
                icon=Icon(icon_color=start.color.hex, icon='flag-checkered', prefix='fa', color='orange'),
                popup=popup).add_to(map)
        program_list.append({'type':'marker', 'lat':start.lat, 'lng':start.lng, 'name':start.name, 'id':start.id, 'color':start.color.hex})
        marker_coordonee.append((start.lat, start.lng))
        stands.add(start)
        turn_nb = 0
        while True:
            if new_stand == start:
                turn_nb +=1
            old_stand = new_stand
            # si l'ancien stand a une trace qui part d lui
            trace = old_stand.start_trace.filter_by(turn_nb=turn_nb).first()
            if trace :
                new_stand = trace.end
                if new_stand not in stands:
                    popup = Popup()
                    popup._template = Template("""
                            var {{this.get_name()}} = L.popup({{ this.options|tojson }});
                            {{ this._parent.get_name() }}.on("click", function() {on_marker_click(%s)})
                            """%new_stand.id)
                    last_m=Marker((new_stand.lat, new_stand.lng),
                        tooltip=new_stand.name,
                        icon=Icon(icon_color=new_stand.color.hex),
                        popup=popup).add_to(map)

                    # ajoute le stand a la liste de coordonee pour trouver le milieux
                    # plus pour savoir si le stand est deja sur la map et la mettre sur la liste des programme
                    marker_coordonee.append((new_stand.lat, new_stand.lng))
                    stands.add(new_stand)

                program_list.append({'type':'trace', 'dist':'bahbah', 'deni':'ahahah', 'name':trace.name, 'id':trace.id})
                program_list.append({'type':'marker', 'lat':new_stand.lat, 'lng':new_stand.lng, 'name':new_stand.name, 'id':new_stand.id, 'color':new_stand.color.hex})

                poly_points = [[old_stand.lat, old_stand.lng ],*eval(trace.trace),[new_stand.lat, new_stand.lng]]
                PolyLine(poly_points, tooltip=trace.name).add_to(map)
            else:
                last_m.icon.options['icon']='flag-checkered'
                last_m.icon.options['prefix']='fa'
                break
        point = MultiPoint(marker_coordonee).centroid
        map.location = (point.x, point.y)


    #? render the map
    map.get_root().width = '100%'
    map.get_root().height = '450px'
    map.get_root().render()

    header= map.get_root().header.render()
    body= map.get_root().html.render()
    script= map.get_root().script.render()

    folium_map={'header':header, 'body':body, 'script':script}

    return render_template('1.2.1-modify_parcours.html', user_data=user, event_data=event, parcours_data=parcours, name_form=name_form, folium_map=folium_map, map_name=map.get_name() , program_list=program_list, modif=modif, modif_form=modif_form)


@app.route('/event/<event_name>/coureurs')
@login_required
@admin_required
def coureurs(event_name):
    # * page to access the different runner that will or had participate to the event
    event_data = Event.query.filter_by(name=event_name).first()
    user = current_user
    return render_template("1.3-coureurs.html", user_data=user, event_data=event_data)
