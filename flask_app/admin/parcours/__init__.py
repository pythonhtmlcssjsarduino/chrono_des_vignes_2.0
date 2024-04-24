from flask import Blueprint, flash, redirect, render_template, request
from flask_app import admin_required, db
from flask_app.admin.parcours.forms import  Parcours_name_form, Etape_modif_form, Stand_modif_form
from flask_login import login_required, current_user
from flask_app.models import Event, Stand, Trace
from folium import Map, Marker, Icon, PolyLine, Popup, LayerControl, TileLayer
from jinja2 import Template
from colour import Color


parcours = Blueprint('parcours', __name__, template_folder='templates')


def midpoint(latlng1, latlng2):
    print(latlng1, latlng2)
    lat = (latlng1[0]+latlng2[0])/2
    lng = (latlng1[1]+latlng2[1])/2
    print(lat, lng)
    return (lat, lng)

@parcours.route('/event/<event_name>/parcours')
@login_required
@admin_required
def parcours_page(event_name):
    # * page to access the differents parcours of the event
    event_data = Event.query.filter_by(name=event_name).first()
    user = current_user
    return render_template("parcours.html", user_data=user, event_data=event_data)

def create_map(parcours):
    #! create the map
    program_list=[]
    marker_coordonee = []
    stands=set()
    next_path_name =[]
    last_path_name = []
    markers_name = []
    map_style = 'satelite'
    map_styles={'satelite':{'tiles':'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
                            'attr':'Esri',
                            'name':'Esri Satellite'},
                'map':{'tiles':'OpenStreetMap',
                        'attr':'',
                        'name':''}}

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
        popup = Popup()
        popup._template = Template("""
            var {{this.get_name()}} = L.popup({{ this.options|tojson }});
            {{ this._parent.get_name() }}.on("click", function() {on_marker_click(%s)})
            """%start.id)
        last_m=Marker((start.lat, start.lng),
                tooltip=start.name,
                icon=Icon(icon_color=start.color.hex, icon='flag-checkered', prefix='fa', color='orange' if str(new_stand.id) != request.args.get('marker') else 'green'),
                popup=popup).add_to(map)
        element_name = last_m.get_name()
        program_list.append({'type':'marker', 'lat':start.lat, 'lng':start.lng, 'name':start.name, 'id':start.id, 'color':start.color.hex, 'step':0})
        marker_coordonee.append((start.lat, start.lng))
        stands.add(start)
        turn_nb = 0
        step =0
        while True:
            #print('loop')
            if new_stand == start:
                turn_nb +=1
            step += 1
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
                    if request.args.get('marker') != None and str(new_stand.id) == request.args.get('marker') :
                        last_m.icon.options['markerColor']='green'
                        element_name = last_m.get_name()

                    # ajoute le stand a la liste de coordonee pour trouver le milieux
                    # plus pour savoir si le stand est deja sur la map et la mettre sur la liste des programme
                    marker_coordonee.append((new_stand.lat, new_stand.lng))
                    stands.add(new_stand)

                program_list.append({'type':'trace', 'dist':'bahbah', 'deni':'ahahah', 'name':trace.name, 'id':trace.id})
                program_list.append({'type':'marker', 'lat':new_stand.lat, 'lng':new_stand.lng, 'name':new_stand.name, 'id':new_stand.id, 'color':new_stand.color.hex, 'step':step})

                poly_points = [[old_stand.lat, old_stand.lng ],*eval(trace.trace),[new_stand.lat, new_stand.lng]]
                marker_coordonee += poly_points
                popup = Popup()
                popup._template = Template("""
                            var {{this.get_name()}} = L.popup({{ this.options|tojson }});
                            {{ this._parent.get_name() }}.on("click", function() {on_trace_click(%s)})
                            """%trace.id)
                if str(trace.id)!=request.args.get('trace'):
                    poly = PolyLine(poly_points, tooltip=trace.name, popup=popup).add_to(map)
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
    # afficher le trace pour les modifications
    if request.args.get('trace') != None:
        trace = Trace.query.filter_by(id=request.args.get('trace')).first()
        if not trace or trace.parcours != parcours:
            return redirect(request.path)
        poly_points = [[trace.start.lat, trace.start.lng ],*eval(trace.trace),[trace.end.lat, trace.end.lng]]
        marker_coordonee += poly_points
        popup = Popup()
        popup._template = Template("""
                    var {{this.get_name()}} = L.popup({{ this.options|tojson }});
                    {{ this._parent.get_name() }}.on("click", function() {on_trace_click(%s)})
                    """%trace.id)
        line = PolyLine(poly_points, dash_array='5', tooltip=trace.name, popup=popup).add_to(map)
        element_name= line.get_name()
        last_point = poly_points[0]
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
    marker_coordonee = [(la, lo) for la, lo in marker_coordonee]
    if len(lats)!=0 or len(lngs)!=0:
        map.fit_bounds([min(marker_coordonee), max(marker_coordonee)])
    #? ajout different layer
    TileLayer('OpenStreetMap', max_zoom=20).add_to(map)
    TileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', attr='Esri', name='satelite', max_zoom=20).add_to(map)
    LayerControl().add_to(map)

    return element_name, last_path_name, next_path_name, markers_name, program_list, map

@parcours.route('/event/<event_name>/parcours/<parcours_name>', methods=['POST', 'GET'])
@login_required
@admin_required
def modify_parcours(event_name, parcours_name):
    event = Event.query.filter_by(name=event_name).first()
    parcours= event.parcours.filter_by(name=parcours_name).first()
    user = current_user
    modif = request.args.get('modif', 'map')

    #? formulaire pour le nom du parcours
    name_form= Parcours_name_form(data={'name':parcours.name})
    if modif=='form' and name_form.validate_on_submit() :
        flash('name saved enfait non pas encore implementé')
        return redirect(request.path)
    

    #? formulaire + actions modifications
    if request.args.get('marker'):#? modif d'un marker
        modif_form_type='marker'
        stand= Stand.query.filter_by(id=request.args.get('marker')).first()
        if not stand or stand.parcours != parcours:
            return redirect(request.path)
        first_or_last = parcours.end_stand==stand or parcours.start_stand==stand
        print(stand.lat, stand.lng)
        modif_form= Stand_modif_form(data={'name':stand.name, 'lat':stand.lat, 'lng':stand.lng, 'color':stand.color.hex, 'chrono':stand.chrono})
        print(modif_form.lat.data)
        if first_or_last:
            modif_form.chrono.render_kw = {'disabled':''}

        if modif_form.validate_on_submit():
            # name
            stand.name = modif_form.name.data
            # lat
            stand.lat = modif_form.lat.data
            # lng
            stand.lng = modif_form.lng.data
            # color
            stand.color = Color(modif_form.color.data)
            # chrono
            stand.chrono = bool(modif_form.chrono.data)
            db.session.commit()
            return redirect(request.path)
    elif request.args.get('trace'):#? modif d'une trace
        modif_form_type = 'trace'
        trace = Trace.query.filter_by(id=request.args.get('trace')).first()
        if not trace or trace.parcours != parcours:
            return redirect(request.path)
        #! suppression de l'etape
        if request.args.get('delete')=='':
            nb_etape_end = len(trace.end.end_trace.all())
            print(nb_etape_end)
            print(trace.end.end_trace.all())
            if trace.end == parcours.start_stand:
                # si le stand d'arrivée est le debut du parcour la var turn_nb dout etre incrementée
                next_trace = trace.end.start_trace.filter_by(turn_nb=trace.turn_nb + 1).first()
                print(next_trace)
            else:
                next_trace = trace.end.start_trace.filter_by(turn_nb=trace.turn_nb).first()
            print(trace.end, parcours.end_stand, trace.end.end_trace.filter_by(turn_nb=trace.turn_nb+1).all())
            #! eviter les boucles hors du depart
            if trace.end == parcours.start_stand and not (trace.end == parcours.end_stand and len(trace.end.end_trace.filter_by(turn_nb=trace.turn_nb+1).all())==0):
                # trouver tous les stans que pass depuis le dernier passage par le start
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
                    print(stand, 'stand', stand.start_trace.filter_by(turn_nb = trace.turn_nb+1).first())
                    stand = stand.start_trace.filter_by(turn_nb = trace.turn_nb+1).first().end
                print(before, after)
                if not any([e in after[1:] for e in before[1:]]) and trace.end == parcours.start_stand and trace.start == trace.end.start_trace.filter_by(turn_nb = trace.turn_nb+1).first().end:
                    # si apres la suppression on passe d'un stand au même
                    print('coucou')
                    db.session.delete(trace.end.start_trace.filter_by(turn_nb = trace.turn_nb+1).first())
                    loop=False
                elif any([e in after for e in before]):
                    print('ahhhh')
                    flash('action impossible', 'danger')
                    loop=True
                else:
                    loop=False
            else:
                loop= False
            if not loop:
                if trace.end == parcours.end_stand and len(trace.end.end_trace.filter_by(turn_nb=trace.turn_nb+1).all())==0:
                    # c'est la fin du parcours il faut donc
                    # changer le stand final du parcours
                    print('it is the last trace of the parcours')
                    parcours.end_stand = trace.start
                    parcours.end_stand.chrono = 1
                else:
                    print('it is not the last')
                    # ce n'est pas la fin donc on doit coller les 2 etapes
                    next_trace.path = str(eval(trace.trace) + eval(next_trace.trace))
                    next_trace.start = trace.start
                    next_trace.turn_nb = trace.turn_nb

                if nb_etape_end == 1 and trace.end != parcours.start_stand:
                    print('on peut supp le marker')
                    db.session.delete(trace.end)# alors on peut le supprimer
                # supprimer l'etape
                db.session.delete(trace)
                db.session.commit()

            print('redirect')
            return redirect(request.path)
        print('redirected')
        #! creation du formulaire de modification
        modif_form = Etape_modif_form(data={'name':trace.name, 'path':trace.trace})
        if modif_form.validate_on_submit():
            # name
            trace.name = modif_form.name.data
            try:
                def float_int(value):
                    try:
                        str(value).index('.')
                        return float(value)
                    except:
                        return int(value)

                new = str([[float_int(lat),float_int(lng)] for lat,lng in list(eval(modif_form.path.data))])
            except:
                pass
            else:
                trace.trace = new
            db.session.commit()
            return redirect(request.path)
    elif request.args.get('new'): #? ajout de nouvelles trace et marker si besoin
        print('new')
        modif_form_type = 'new'

        try:
            last_marker = int(request.args.get('new'))
        except:
            return redirect(request.path)

        # trouve le marker qui est le debut de la traces
        print(last_marker)
        turn_nb = 1
        stand : Stand = parcours.start_stand
        for i in range(last_marker):
            #print(stand, turn_nb)
            stand = stand.start_trace.filter_by(turn_nb=turn_nb).first().end
            if stand == parcours.start_stand:
                turn_nb += 1
        print(stand, turn_nb)

        #! creer le modif_form
        if last_marker == -1 or not stand.start_trace.filter_by(turn_nb=turn_nb).first():
            print('first or last')
            modif_form= Stand_modif_form()
            modif_form.chrono.data=1
            modif_form.chrono.render_kw  = {'disabled':''}
        else:
            print('next', last_marker)
            modif_form= Stand_modif_form()

        #! efectue les actions si le form est submit
        if modif_form.validate_on_submit():
            print('creer le nouveau stand')
            print(modif_form.name.data)
            print(modif_form.lat.data)
            print(modif_form.lng.data)

            if last_marker == -1: # il sera le premier
                return redirect(request.path)
            elif not stand.start_trace.filter_by(turn_nb=turn_nb).first(): # il sera le dernier
                print('dernier eee')
                stand.end_stand=None
                args = {'name':modif_form.name.data,
                          'lat':modif_form.lat.data,
                          'lng':modif_form.lng.data,
                          'parcours_id':parcours.id,
                          'color':modif_form.color.data,
                          'chrono':modif_form.chrono.data,
                          'end_stand':parcours.id
                          }
            else:
                print('non eee')
                args = {'name':modif_form.name.data,
                          'lat':modif_form.lat.data,
                          'lng':modif_form.lng.data,
                          'parcours_id':parcours.id,
                          'color':modif_form.color.data,
                          'chrono':modif_form.chrono.data,
                          }

            trace_start = stand
            trace_end = Stand(**args )
            db.session.add(trace_end)
            nb_name = len(Trace.query.filter(Trace.name.contains(f'{trace_start.name} - {trace_end.name}')).all())
            old_trace = Trace.query.filter_by(start_id = trace_start.id, turn_nb=turn_nb).first()
            name = f"{trace_start.name} - {trace_end.name} {'(' if nb_name else ''}{nb_name if nb_name else ''}{')' if nb_name else ''}"
            print(trace_start, trace_end)
            new_trace = Trace(name=name, parcours_id=parcours.id, start_id = trace_start.id, end_id = trace_end.id, turn_nb=turn_nb)

            all_stands = set()
            for t in Trace.query.filter_by(turn_nb=turn_nb).all():
                all_stands.add(t.start)
                all_stands.add(t.end)
            print(all_stands)
            if trace_end in all_stands:
                flash('action pas possible', 'danger')
                return redirect(request.path)

            if old_trace:
                print('old_trace')

                old_trace.start = trace_end
                print(old_trace.start, trace_end, 'start', old_trace)

            if not trace_end.start_trace.filter_by(turn_nb=turn_nb).first():
                parcours.end_stand=trace_end
                print('start stand est le dernier')
            db.session.add(new_trace)
            db.session.commit()

            return redirect(request.path)

        if request.args.get('stand'): # creer la trace en direction d'un stand
            print(request.args.get('stand'), 'stand')
            try:
                nb_stand = int(request.args.get('stand'))
            except:
                redirect(request.path)

            trace_start = stand
            trace_end = Stand.query.filter_by(id = nb_stand).first()
            nb_name = len(Trace.query.filter(Trace.name.contains(f'{trace_start.name} - {trace_end.name}')).all())
            old_trace = Trace.query.filter_by(start_id = trace_start.id, turn_nb=turn_nb).first()
            name = f"{trace_start.name} - {trace_end.name} {'(' if nb_name else ''}{nb_name if nb_name else ''}{')' if nb_name else ''}"
            print(trace_start, trace_end)
            new_trace = Trace(name=name, parcours_id=parcours.id, start_id = trace_start.id, end_id = trace_end.id, turn_nb=turn_nb)

            all_stands = set()
            for t in Trace.query.filter_by(turn_nb=turn_nb).all():
                all_stands.add(t.start)
                all_stands.add(t.end)
            print(all_stands)
            if trace_end in all_stands:
                flash('action pas possible', 'danger')
                return redirect(request.path)

            if old_trace:
                print('old_trace')

                old_trace.start = trace_end
                print(old_trace.start, trace_end, 'start', old_trace)

            if not stand.start_trace.filter_by(turn_nb=turn_nb).first():
                parcours.end_stand=trace_end
                print('start stand est le dernier')
            db.session.add(new_trace)
            db.session.commit()
            return redirect(request.path)
    else: #? simple affichage
        modif_form_type = None
        modif_form=None

    element_name, last_path_name, next_path_name, markers_name, program_list, map = create_map(parcours)


    #? render the map
    map.get_root().width = '100%'
    map.get_root().height = '450px'
    map.get_root().render()

    header= map.get_root().header.render()
    body= map.get_root().html.render()
    script= map.get_root().script.render()

    folium_map={'header':header, 'body':body, 'script':script}
    return render_template('modify_parcours.html', user_data=user, event_data=event, parcours_data=parcours, name_form=name_form, folium_map=folium_map,
                           map_name=map.get_name(), element_name=element_name, path_names={'last':last_path_name, 'next':next_path_name} if last_path_name else markers_name,
                           program_list=program_list, modif=modif, modif_form=modif_form, modif_form_type=modif_form_type)
