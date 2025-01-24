from flask import Blueprint, flash, redirect, render_template, request, abort
from flask_app import admin_required, db, set_route, lang_url_for as url_for
from flask_app.admin.parcours.forms import  Parcours_name_form, Etape_modif_form, Stand_modif_form, New_parcours_form
from flask_login import login_required, current_user
from flask_app.models import Event, Stand, Trace, Parcours
from folium import Map, Marker, Icon, PolyLine, Popup, LayerControl, TileLayer
from jinja2 import Template
from colour import Color
from flask_app.lib import get_points_elevation, calc_points_dist, midpoint

parcours_bp = Blueprint('parcours', __name__, template_folder='templates')

@set_route(parcours_bp, '/event/<event_name>/parcours/<parcours_name>/delete')
@login_required
@admin_required
def delete_parcours_page(event_name, parcours_name):
    event = Event.query.filter_by(name=event_name).first_or_404()
    parcours:Parcours= event.parcours.filter_by(name=parcours_name).first_or_404()
    if parcours.editions.count()>0:
        flash('action impossible le parcours est déjà utilisé dans une edition.', 'danger')
        return redirect(url_for('admin.parcours.modify_parcours', event_name=event.name, parcours_name=parcours.name))
    for e in tuple(parcours):
        db.session.delete(e)
    db.session.delete(parcours)
    db.session.commit()
    flash('parcours supprimé!', 'success')

    return redirect(url_for('admin.parcours.parcours_page', event_name=event.name))

@set_route(parcours_bp, '/event/<event_name>/parcours/<parcours_name>/copy')
@login_required
@admin_required
def copy_parcours(event_name, parcours_name):
    event = Event.query.filter_by(name=event_name).first_or_404()
    parcours:Parcours= event.parcours.filter_by(name=parcours_name).first_or_404()

    p = Parcours(name=f'{parcours.name} copy', event=event, description=parcours.description, chronos_list=parcours.chronos_list)
    db.session.add(p)
    db.session.commit()
    db.session.refresh(p)
    old_stands = Stand.query.filter_by(parcours_id=parcours.id).all()
    old_to_new_id = {}
    for old_stand in old_stands:
        new_stand = Stand(name=old_stand.name, lat=old_stand.lat, lng=old_stand.lng, elevation=old_stand.elevation, parcours_id=p.id, start_stand=p.id if old_stand.start_stand else None, end_stand=p.id if old_stand.end_stand else None, color=old_stand.color, chrono=old_stand.chrono)
        db.session.add(new_stand)
        db.session.commit()
        db.session.refresh(new_stand)
        old_to_new_id[old_stand.id] = new_stand.id
    
    old_traces:list[Trace] = Trace.query.filter_by(parcours_id=parcours.id).all()
    for old_trace in old_traces:
        new_trace = Trace(name=old_trace.name, parcours_id=p.id, start_id=old_to_new_id[old_trace.start_id], end_id=old_to_new_id[old_trace.end_id], trace=old_trace.trace, turn_nb=old_trace.turn_nb)
        db.session.add(new_trace)
        db.session.commit()

    return redirect(url_for('admin.parcours.modify_parcours', event_name=event.name, parcours_name=f'{parcours.name} copy'))

@set_route(parcours_bp, '/event/<event_name>/parcours/<parcours_name>/archive')
@login_required
@admin_required
def archive_parcours_page(event_name, parcours_name):
    event = Event.query.filter_by(name=event_name).first_or_404()
    parcours= event.parcours.filter_by(name=parcours_name).first_or_404()
    parcours.archived =True
    db.session.commit()
    return redirect(url_for('admin.parcours.parcours_page', event_name=event.name))

@set_route(parcours_bp, '/event/<event_name>/parcours/<parcours_name>/unarchive')
@login_required
@admin_required
def unarchive_parcours_page(event_name, parcours_name):
    event = Event.query.filter_by(name=event_name).first_or_404()
    parcours= event.parcours.filter_by(name=parcours_name).first_or_404()
    parcours.archived =False
    db.session.commit()
    return redirect(url_for('admin.parcours.parcours_page', event_name=event.name))

@set_route(parcours_bp, '/event/<event_name>/parcours', methods=['POST', 'GET'])
@login_required
@admin_required
def parcours_page(event_name):
    # * page to access the differents parcours of the event
    event = Event.query.filter_by(name=event_name).first()
    user = current_user

    form = New_parcours_form()
    if form.validate_on_submit():
        if not event.parcours.filter_by(name=form.name.data).first():
            #ok nom pas utilisé

            p = Parcours(name=form.name.data, event=event)
            db.session.add(p)
            db.session.commit()
            p=Parcours.query.filter_by(name=form.name.data).first()
            s= Stand(name=f'debut-{form.name.data}'[:36], parcours_id=p.id, lat=form.start_lat.data, lng=form.start_lng.data, chrono=1, start_stand=p.id)
            db.session.add(s)
            db.session.commit()

            return redirect(url_for('admin.parcours.modify_parcours', event_name=event.name, parcours_name=form.name.data))
        else:
            form.name.errors = list(form.name.errors)+['vous utiliser deja ce nom.']
    active_parcours = event.parcours.filter_by(archived=False).all()
    archived_parcours = event.parcours.filter_by(archived=True).all()
    
    return render_template("parcours.html", user_data=user, event_data=event, archived_parcours=archived_parcours, active_parcours=active_parcours, event_modif=True, form=form)

'''
def get_graph_data(data):
    points = []
    to_request=[]
    last_point=None
    tot_dist = 0
    for e in data:
        if isinstance(e, Stand):
            tot_dist = dist = tot_dist + (calc_points_dist(e.lat, e.lng, last_point[0], last_point[1]) if last_point else 0)
            last_point = e.lat, e.lng
            if e.elevation:
                points.append({'x':dist, 'y':e.elevation, 'label':e.name})
            else:
                to_request.append(e)
                points.append({'x':dist, 'y':None, 'label':e.name})
        elif isinstance(e, Trace):
            trace = eval(e.trace)
            if len(trace):
                if trace[0][2]: # si il y a l'altitude
                    for t in trace:
                        tot_dist = dist = tot_dist + calc_points_dist(t[0], t[1], last_point[0], last_point[1])
                        last_point = t[0], t[1]
                        points.append({'x':dist, 'y':t[2], 'label':e.name})
                else:
                    response = get_points_elevation([(lat, lng) for lat, lng, _ in trace] )
                    trace = [(p['latitude'], p['longitude'], p['elevation']) for p in response]
                    e.trace = str(trace)
                    db.session.commit()
                    for t in trace:
                        tot_dist = dist = tot_dist + calc_points_dist(t[0], t[1], last_point[0], last_point[1])
                        last_point = t[0], t[1]
                        points.append({'x':dist, 'y':t[2], 'label':e.name})

    response = get_points_elevation([(req.lat, req.lng) for req in to_request])

    if len(to_request) > 0:
        for index, point in enumerate(points):
            if point['y'] is None:
                ele = response.pop(0)['elevation']
                to_request.pop(0).elevation = ele
                points[index]['y'] = ele
        db.session.commit()

    return points
'''
def build_alt_graph(graph_data):
    points = []
    to_request=[]
    last_point=None
    dist = 0
    for e in graph_data:
        if isinstance(e, Stand):
            dist += calc_points_dist(e.lat, e.lng, last_point[0], last_point[1]) if last_point else 0
            last_point = e.lat, e.lng
            if e.elevation:
                points.append({'x':dist, 'y':e.elevation, 'label':e.name, 'type':'stand'})
            else:
                to_request.append(e)
                points.append({'x':dist, 'y':None, 'label':e.name, 'type':'stand'})
        elif isinstance(e, Trace):
            trace = e
            if len(trace):
                if trace.has_alt(): # si il y a l'altitude
                    for point in trace:
                        dist += calc_points_dist(point.lat, point.lng, last_point[0], last_point[1])
                        last_point = point.lat, point.lng
                        points.append({'x':dist, 'y':point.alt, 'label':e.name, 'type':'trace'})
                else:
                    response = get_points_elevation([(lat, lng) for lat, lng, _ in trace] )
                    e.set_trace([(p['latitude'], p['longitude'], p['elevation']) for p in response])
                    db.session.commit()
                    for point in trace:
                        dist += calc_points_dist(point.lat, point.lng, last_point[0], last_point[1])
                        last_point = point.lat, point.lng
                        points.append({'x':dist, 'y':point.alt, 'label':e.name, 'type':'trace'})

    response = get_points_elevation([(req.lat, req.lng) for req in to_request])

    if len(to_request) > 0:
        for index, point in enumerate(points):
            if point['y'] is None:
                ele = response.pop(0)['elevation']
                to_request.pop(0).elevation = ele
                points[index]['y'] = ele
        db.session.commit()

    return points


def create_map_and_alt_graph(parcours:Parcours, modif= False, rdv=None):
     #! create the map
    map_style = 'satelite'
    map_styles={'map':{'tiles':'OpenStreetMap',
                        'attr':None,
                        'name':None,
                        'max_zoom':20},
                'satelite':{'tiles':'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
                            'attr':'Esri',
                            'name':'Satellite',
                            'max_zoom':20},
                'topographie':{'tiles':'https://tile.opentopomap.org/{z}/{x}/{y}.png',
                        'attr':'opentopomap',
                        'name':'topographie',
                        'max_zoom':17}}

    program_list=[]
    part_list = []
    marker_coordonee = []
    stands=set()
    next_path_name =[]
    last_path_name = []
    markers_name = []
    chrono_list = []
    start = parcours.start_stand
    map = Map(max_zoom=22,
            location=(0,0),
            zoom_start=1,
            tiles = None,
            attr = map_styles[map_style]['attr'],
            name = map_styles[map_style]['name'])
    new_stand=start
    # si aucun depart alors ne mettre aucun stand
    if start:
        if modif:
            popup = Popup()
            popup._template = Template("""
                var {{this.get_name()}} = L.popup({{ this.options|tojson }});
                {{ this._parent.get_name() }}.on("click", function() {on_marker_click(%s)})
                """%start.id)
        last_m=Marker((start.lat, start.lng),
                tooltip=start.name,
                icon=Icon(icon_color=start.color.hex, icon='flag-checkered', prefix='fa', color='orange' if str(new_stand.id) != request.args.get('marker') else 'green'),
                popup=popup if modif else None).add_to(map)
        element_name = last_m.get_name()
        part_list.append(start)
        program_list.append({'type':'marker', 'lat':start.lat, 'lng':start.lng, 'name':start.name, 'id':start.id, 'color':start.color.hex, 'step':0})
        stands.add(start)
        chrono_list.append(start.id)
        turn_nb = 0
        step =0
        while True:
            if new_stand == start:
                turn_nb +=1
            step += 1
            old_stand = new_stand
            # si l'ancien stand a une trace qui part de lui
            trace = old_stand.start_trace.filter_by(turn_nb=turn_nb).first()
            if trace is not None :
                new_stand = trace.end
                if new_stand.chrono : chrono_list.append(new_stand.id)
                if new_stand not in stands:
                    if modif:
                        popup = Popup()
                        popup._template = Template("""
                                var {{this.get_name()}} = L.popup({{ this.options|tojson }});
                                {{ this._parent.get_name() }}.on("click", function() {on_marker_click(%s)})
                                """%new_stand.id)
                    last_m=Marker((new_stand.lat, new_stand.lng),
                        tooltip=new_stand.name,
                        icon=Icon(icon_color=new_stand.color.hex),
                        popup=popup if modif else None).add_to(map)
                    if request.args.get('marker') != None and str(new_stand.id) == request.args.get('marker') :
                        last_m.icon.options['markerColor']='green'
                        element_name = last_m.get_name()

                    # plus pour savoir si le stand est deja sur la map et la mettre sur la liste des programme
                    stands.add(new_stand)

                part_list.append(trace)
                part_list.append(new_stand)

                program_list.append({'type':'trace', 'name':trace.name, 'id':trace.id, 'trace':eval(trace.trace)})
                program_list.append({'type':'marker', 'lat':new_stand.lat, 'lng':new_stand.lng, 'name':new_stand.name, 'id':new_stand.id, 'color':new_stand.color.hex, 'step':step})

                poly_points = [[old_stand.lat, old_stand.lng ],*([lat, lng] for lat, lng, _ in eval(trace.trace)),[new_stand.lat, new_stand.lng]]
                marker_coordonee += poly_points
                if modif:
                    popup = Popup()
                    popup._template = Template("""
                                var {{this.get_name()}} = L.popup({{ this.options|tojson }});
                                {{ this._parent.get_name() }}.on("click", function() {on_trace_click(%s)})
                                """%trace.id)
                if str(trace.id)!=request.args.get('trace'):
                    poly = PolyLine(poly_points, tooltip=trace.name, popup=popup if modif else None).add_to(map)
                if request.args.get('marker') != None and str(new_stand.id) == request.args.get('marker') :
                    last_path_name.append(poly.get_name())
                elif request.args.get('marker') != None and str(old_stand.id) == request.args.get('marker') :
                    next_path_name.append(poly.get_name())
            else:
                last_m.icon.options['icon']='flag-checkered'
                last_m.icon.options['prefix']='fa'
                break
    else:
        element_name=None

    parcours.chronos_list = str(chrono_list)
    db.session.commit()
    
    graph = build_alt_graph(part_list)

    # afficher le trace pour les modifications
    if request.args.get('trace') != None and modif:
        trace = Trace.query.filter_by(id=request.args.get('trace')).first()
        if trace is None or trace.parcours != parcours:
            abort(400)
        poly_points = [[trace.start.lat, trace.start.lng ],*[[lat, lng] for lat, lng, _ in eval(trace.trace)],[trace.end.lat, trace.end.lng]]
        marker_coordonee += poly_points
        popup = Popup()
        popup._template = Template("""
                    var {{this.get_name()}} = L.popup({{ this.options|tojson }});
                    {{ this._parent.get_name() }}.on("click", function() {on_trace_click(%s)})
                    """%trace.id)
        line = PolyLine(poly_points, dash_array='5', tooltip=trace.name, popup=popup).add_to(map)
        element_name= line.get_name()
        last_point = tuple(poly_points[0])
        i=-1
        for i,( lat, lng) in enumerate(poly_points[1:-1]): # affiche chaque marker d'angle et les signes plus pour ajouter un point
            popup = Popup()
            popup._template = Template("""
                        var {{this.get_name()}} = L.popup({{ this.options|tojson }});
                        {{ this._parent.get_name() }}.on("click", function() {trace_point_modif(%s)})
                        """%f'{lat}, {lng}')
            # place le marker a l'angle
            marker = Marker((lat, lng),
                    icon=Icon(icon='flag', prefix='fa', color='green'),
                    popup=popup).add_to(map)

            # affiche le plus pour ajouter un point sur
            # le point central entre les deux points
            midlatlng = midpoint(last_point, (lat,lng))
            popup = Popup()
            popup._template = Template("""
                    var {{this.get_name()}} = L.popup({{ this.options|tojson }});
                    {{ this._parent.get_name() }}.on("click", function() {trace_point_add(%s)})
                    """%f'{midlatlng[0]}, {midlatlng[1]}, {i}')
            mid_marker = Marker((midlatlng[0], midlatlng[1]),
                                popup=popup,
                                icon=Icon(icon='circle-plus', prefix='fa', color='lightgreen')).add_to(map)
            ####
            markers_name.append({'lat':lat, 'lng':lng, 'name':marker.get_name()})
            last_point = (lat, lng)
        # affiche le dernier point d'ajout
        midlatlng = midpoint(last_point, poly_points[-1])
        popup = Popup()
        popup._template = Template("""
                var {{this.get_name()}} = L.popup({{ this.options|tojson }});
                {{ this._parent.get_name() }}.on("click", function() {trace_point_add(%s)})
                """%f'{midlatlng[0]}, {midlatlng[1]}, {i+1}')
        mid_marker = Marker((midlatlng[0], midlatlng[1]),
                            popup=popup,
                            icon=Icon(icon='circle-plus', prefix='fa', color='lightgreen')).add_to(map)

    # trouver et centre la map sur le parcours
    lats, lngs = set([i[0] for i in marker_coordonee]), set([i[1] for i in marker_coordonee])
    marker_coordonee = [[la, lo] for la, lo in marker_coordonee]
    if len(lats)!=0 or len(lngs)!=0:
        map.fit_bounds([min(marker_coordonee), max(marker_coordonee)])
    #? ajout different layer
    #TileLayer('OpenStreetMap', max_zoom=20).add_to(map)
    #TileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', attr='Esri', name='satelite', max_zoom=20).add_to(map)
    for name, data in map_styles.items():
        TileLayer(**data).add_to(map)
    LayerControl().add_to(map)

    if rdv:
        lat, lng = rdv
        Marker((lat, lng),
                tooltip='rendez-vous',
                icon=Icon(icon_color='#0f0', prefix='fa', icon='arrows-to-circle', color='red')).add_to(map)
        map.fit_bounds([(lat,lng), (lat, lng)], max_zoom=15)

    return element_name, last_path_name, next_path_name, markers_name, program_list, map, graph


@set_route(parcours_bp, '/event/<event_name>/parcours/<parcours_name>', methods=['POST', 'GET'])
@login_required
@admin_required
def modify_parcours(event_name, parcours_name):
    event = Event.query.filter_by(name=event_name).first_or_404()
    parcours:Parcours= event.parcours.filter_by(name=parcours_name).first_or_404()
    user = current_user
    already_use = bool(parcours.editions.count())
    if (already_use and len(request.args)) and request.args.get('modif', 'map') !='form':
        return redirect(url_for('admin.parcours.modify_parcours', event_name=event_name, parcours_name=parcours_name))
    #? formulaire pour le nom du parcours
    name_form= Parcours_name_form(data={'name':parcours.name, 'description':parcours.description})
    if request.args.get('modif', 'map')=='form' and name_form.validate_on_submit() :
        if name_form.name.data == parcours.name or not event.parcours.filter_by(name=name_form.name.data).first():
            # le nom peut etre utilisé
            parcours.name=name_form.name.data
            parcours.description=name_form.description.data
            db.session.commit()
            flash('name saved', 'success')
            return redirect(url_for('admin.parcours.modify_parcours', event_name=event.name, parcours_name=parcours.name))
        else:
            name_form.name.errors = list(name_form.name.errors)+['vous utiliser deja ce nom.']


    #? formulaire + actions modifications
    if request.args.get('marker') and not already_use:#? modif d'un marker
        modif_form_type='marker'
        stand= Stand.query.filter_by(id=request.args.get('marker')).first()
        if stand is None or stand.parcours != parcours:
            return redirect(request.path)
        first_or_last = parcours.end_stand==stand or parcours.start_stand==stand
        modif_form= Stand_modif_form(data={'name':stand.name, 'lat':stand.lat, 'lng':stand.lng, 'color':stand.color.hex_l, 'chrono':stand.chrono})
        if first_or_last:
            modif_form.chrono.render_kw = {'disabled':''}

        if modif_form.validate_on_submit():
            if stand.name == modif_form.name.data or not parcours.stands.filter_by(name=modif_form.name.data).first():
                # name
                stand.name = modif_form.name.data
                if stand.lat != modif_form.lat.data or stand.lng != modif_form.lng.data:
                    # lat
                    stand.lat = modif_form.lat.data
                    # lng
                    stand.lng = modif_form.lng.data
                    # elevation
                    ele = get_points_elevation([(modif_form.lat.data, modif_form.lng.data)])[0]['elevation']
                    stand.elevation = ele
                # color
                stand.color = Color(modif_form.color.data)
                # chrono
                stand.chrono = bool(modif_form.chrono.data)
                db.session.commit()
                return redirect(request.path)
            else:
                modif_form.name.errors = list(name_form.name.errors)+['vous utiliser deja ce nom.']
    elif request.args.get('trace') and not already_use:#? modif d'une trace
        modif_form_type = 'trace'
        trace = Trace.query.filter_by(id=request.args.get('trace')).first()
        if trace is None or trace.parcours != parcours:
            return redirect(request.path)
        #! suppression de l'etape
        if request.args.get('delete')=='':
            nb_etape_end = trace.end.end_trace.count()
            if trace.end == parcours.start_stand:
                # si le stand d'arrivée est le debut du parcour la var turn_nb doit etre incrementée
                next_trace = trace.end.start_trace.filter_by(turn_nb=trace.turn_nb + 1).first()
            else:
                next_trace = trace.end.start_trace.filter_by(turn_nb=trace.turn_nb).first()
            # ! eviter les boucles hors du depart
            if trace.end == parcours.start_stand and not (trace.end == parcours.end_stand and trace.end.end_trace.filter_by(turn_nb=trace.turn_nb+1).count()==0):
                # trouver tous les stands que passe depuis le dernier passage par le start
                before = []
                stand=trace.start
                while True:
                    if stand == parcours.start_stand:
                        break
                    else:
                        before.append(stand)
                    stand = stand.end_trace.filter_by(turn_nb = trace.turn_nb).first().start
                after = []
                stand = trace.end.start_trace.filter_by(turn_nb = trace.turn_nb+1).first().end
                while True:
                    if stand == parcours.start_stand:
                        break
                    else:
                        after.append(stand)
                    if stand==parcours.end_stand:
                        after.append(stand)
                        break
                    stand = stand.start_trace.filter_by(turn_nb = trace.turn_nb+1).first().end
                if not any([e in after[1:] for e in before[1:]]) and trace.end == parcours.start_stand and trace.start == trace.end.start_trace.filter_by(turn_nb = trace.turn_nb+1).first().end:
                    # si apres la suppression on passe d'un stand au même
                    db.session.delete(trace.end.start_trace.filter_by(turn_nb = trace.turn_nb+1).first())
                    loop=False
                elif any([e in after for e in before]):
                    flash('action impossible vous allez faire une boucle hors du depart', 'danger')
                    loop=True
                else:
                    loop=False
            else:
                loop= False
            if not loop:
                if trace.end == parcours.end_stand and len(trace.end.end_trace.filter_by(turn_nb=trace.turn_nb+1).all())==0:
                    # c'est la fin du parcours il faut donc
                    # changer le stand final du parcours
                    parcours.end_stand = trace.start
                    parcours.end_stand.chrono = 1
                else:
                    # ce n'est pas la fin donc on doit coller les 2 etapes
                    next_trace.path = str(eval(trace.trace) + eval(next_trace.trace))
                    next_trace.start = trace.start
                    next_trace.turn_nb = trace.turn_nb

                if nb_etape_end == 1 and trace.end != parcours.start_stand:
                    db.session.delete(trace.end)# alors on peut le supprimer
                # supprimer l'etape
                db.session.delete(trace)
                db.session.commit()

            return redirect(request.path)
        #! creation du formulaire de modification
        modif_form = Etape_modif_form(data={'name':trace.name, 'path':str([[lat, lng] for lat, lng, _ in eval(trace.trace)])})
        if modif_form.validate_on_submit():
            if trace.name == modif_form.name.data or not parcours.traces.filter_by(name=modif_form.name.data).first():
                # name
                trace.name = modif_form.name.data
                try:
                    def float_int(value):
                        try:
                            str(value).index('.')
                            return float(value)
                        except:
                            return int(value)

                    new = [[float_int(lat),float_int(lng)] for lat,lng in list(eval(modif_form.path.data))]
                    elevation = get_points_elevation(new)
                    new = str([[float_int(lat),float_int(lng), float_int(ele['elevation'])] for (lat,lng), ele in zip(list(eval(modif_form.path.data)), elevation)])
                except:
                    return redirect(request.path)
                else:
                    trace.trace = new
                db.session.commit()
                #return redirect(request.path)
            else:
                modif_form.name.errors = list(name_form.name.errors)+['vous utiliser deja ce nom.']
    elif request.args.get('new') and not already_use: #? ajout de nouvelles trace et marker si besoin
        modif_form_type = 'new'

        try:
            last_marker = int(request.args.get('new'))
        except:
            return redirect(request.path)

        # trouve le marker qui est le debut de la traces
        turn_nb = 1
        stand : Stand = parcours.start_stand
        for i in range(last_marker):
            stand = stand.start_trace.filter_by(turn_nb=turn_nb).first().end
            if stand == parcours.start_stand:
                turn_nb += 1
        ic(stand, turn_nb)

        # ! creer le modif_form
        modif_form= Stand_modif_form()
        if last_marker == -1 or not stand.start_trace.filter_by(turn_nb=turn_nb).first():
            modif_form.chrono.data=1
            modif_form.chrono.render_kw  = {'disabled':''}

        # ! efectue les actions si le form est submit
        if modif_form.validate_on_submit():

            if last_marker == -1: # il sera le premier
                return redirect(request.path)
            elif not stand.start_trace.filter_by(turn_nb=turn_nb).first(): # il sera le dernier
                stand.end_stand=None
                args = {'name':modif_form.name.data,
                        'lat':modif_form.lat.data,
                        'lng':modif_form.lng.data,
                        'elevation':get_points_elevation([(modif_form.lat.data, modif_form.lng.data)])[0]['elevation'],
                        'parcours_id':parcours.id,
                        'color':modif_form.color.data,
                        'chrono':modif_form.chrono.data,
                        'end_stand':parcours.id
                        }
            else:
                args = {'name':modif_form.name.data,
                        'lat':modif_form.lat.data,
                        'lng':modif_form.lng.data,
                        'elevation':get_points_elevation([(modif_form.lat.data, modif_form.lng.data)])[0]['elevation'],
                        'parcours_id':parcours.id,
                        'color':modif_form.color.data,
                        'chrono':modif_form.chrono.data,
                        }

            trace_start = stand
            trace_end = Stand(**args )
            db.session.add(trace_end)
            db.session.commit()
            db.session.refresh(trace_end)

            nb_name = Trace.query.filter(Trace.name.contains(f'{trace_start.name} - {trace_end.name}'[:36])).count()
            old_trace = Trace.query.filter_by(start_id = trace_start.id, turn_nb=turn_nb).first()
            name = f"{trace_start.name} - {trace_end.name} {'(' if nb_name else ''}{nb_name if nb_name else ''}{')' if nb_name else ''}"
            new_trace = Trace(name=name, parcours_id=parcours.id, start_id = trace_start.id, end_id = trace_end.id, turn_nb=turn_nb)

            ic(trace_start, trace_end, new_trace, old_trace)

            if old_trace:
                ic(old_trace, 'ok change start_id')
                old_trace.start_id = trace_end.id

            #if not trace_end.start_trace.filter_by(turn_nb=turn_nb).first():
            #    parcours.end_stand=trace_end
            db.session.add(new_trace)
            db.session.commit()

            return redirect(request.path)

        if request.args.get('stand'): # creer la trace en direction d'un stand
            try:
                end_stand_id = int(request.args.get('stand'))
            except:
                redirect(request.path)

            trace_start = stand
            trace_end = Stand.query.filter_by(id = end_stand_id).first()
            nb_name = len(Trace.query.filter(Trace.name.contains(f'{trace_start.name} - {trace_end.name}')).all())
            old_trace = Trace.query.filter_by(start_id = trace_start.id, turn_nb=turn_nb).first()
            name = f"{trace_start.name} - {trace_end.name} {'(' if nb_name else ''}{nb_name if nb_name else ''}{')' if nb_name else ''}"
            new_trace = Trace(name=name, parcours_id=parcours.id, start_id = trace_start.id, end_id = trace_end.id, turn_nb=turn_nb)

            all_stands = set()
            for t in Trace.query.filter_by(turn_nb=turn_nb, parcours_id=parcours.id).all():
                all_stands.add(t.start)
                all_stands.add(t.end)
            if trace_end in all_stands and trace_end != parcours.start_stand:
                ic(trace_end, all_stands)
                flash('action pas possible', 'danger')
                return redirect(request.path)

            if old_trace:
                old_trace.start = trace_end

            if not stand.start_trace.filter_by(turn_nb=turn_nb).first():
                parcours.end_stand=trace_end
            db.session.add(new_trace)
            db.session.commit()
            return redirect(request.path)
    else: #? simple affichage
        modif_form_type = None
        modif_form=None

    map_data = create_map_and_alt_graph(parcours, modif=not already_use)
    element_name, last_path_name, next_path_name, markers_name, program_list, map, graph = map_data


    #? render the map
    map.get_root().width = '100%'
    map.get_root().height = '450px'
    map.get_root().render()

    header= map.get_root().header.render()
    body= map.get_root().html.render()
    script= map.get_root().script.render()

    folium_map={'header':header, 'body':body, 'script':script}
    modif = request.args.get('modif', 'map') if request.args.get('modif', 'map')=='form' or not already_use else None
    return render_template('modify_parcours.html', user_data=user, event_data=event, parcours_data=parcours, name_form=name_form, folium_map=folium_map,
                           map_name=map.get_name(), element_name=element_name, path_names={'last':last_path_name, 'next':next_path_name} if last_path_name else markers_name,
                           program_list=program_list, modif=modif, modif_form=modif_form, modif_form_type=modif_form_type, graph=graph, event_modif=True)
