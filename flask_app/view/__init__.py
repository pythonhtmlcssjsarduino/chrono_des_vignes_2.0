from flask import Blueprint, render_template, redirect, url_for
from flask_app import db
from flask_app.models import Event, Inscription
from flask_app.admin.parcours import create_map_and_alt_graph
from flask_login import current_user, login_required
from datetime import datetime
from flask_babel import _

view = Blueprint('view', __name__, template_folder='templates', url_prefix='/view')

def deg_to_dms(deg):
    """Convert from decimal degrees to degrees, minutes, seconds."""
    m, s = divmod(abs(deg)*3600, 60)
    d, m = divmod(m, 60)
    if deg < 0:
        d = -d
    d, m = int(d), int(m)
    return d, m, s

@view.route('/inscription/<inscription>/delete')
@login_required
def delete_inscription(inscription):
    user = current_user
    inscription = user.inscriptions.filter_by(id=inscription).first_or_404(_('view.error.notyourinscription'))
    db.session.delete(inscription)
    db.session.commit()

    return redirect(url_for('home'))


@view.route('/inscription/<inscription>')
@login_required
def view_inscription_page(inscription):
    user = current_user
    inscription = user.inscriptions.filter_by(id=inscription).first_or_404(_('view.error.notyourinscription'))
    event = inscription.event
    edition = inscription.edition
    parcours = inscription.parcours
    if inscription.inscrit != user:
        return redirect(url_for('home'))

    rdv_url= "https://www.google.com/maps/place/{0}%C2%B0{1}'{2}".format(*deg_to_dms(edition.rdv_lat))+"%22N+{0}%C2%B0{1}'{2}".format(*deg_to_dms(edition.rdv_lng))+f"%22E/@{edition.rdv_lat},{edition.rdv_lng},15z"

    element_name, last_path_name, next_path_name, markers_name, program_list, map, graph = create_map_and_alt_graph(parcours, rdv=(edition.rdv_lat, edition.rdv_lng),)

    #? render the map
    map.get_root().width = '100%'
    map.get_root().height = '450px'
    map.get_root().render()

    header= map.get_root().header.render()
    body= map.get_root().html.render()
    script= map.get_root().script.render()

    folium_map={'header':header, 'body':body, 'script':script}

    return render_template('view_inscription.html', user_data=user, inscription=inscription, folium_map=folium_map, rdv_url=rdv_url)

@view.route('/<event>')
def view_event_page(event):
    user_data = current_user if current_user.is_authenticated else None
    event = Event.query.filter_by(name=event).first_or_404(_('view.error.eventdontexist:event').format(event=event))
    return render_template('view_event.html', user_data = user_data, event_data=event, time = datetime.now())

@view.route('/<event>/edition/<edition>')
def view_edition_page(event, edition):
    user = current_user if current_user.is_authenticated else None
    event = Event.query.filter_by(name=event).first_or_404(_('view.error.eventdontexist:event').format(event=event))
    edition = event.editions.filter_by(name=edition).first_or_404(_('view.error.editiondontexist:edition').format(edition=edition))

    rdv_url= "https://www.google.com/maps/place/{0}%C2%B0{1}'{2}".format(*deg_to_dms(edition.rdv_lat))+"%22N+{0}%C2%B0{1}'{2}".format(*deg_to_dms(edition.rdv_lng))+f"%22E/@{edition.rdv_lat},{edition.rdv_lng},15z"
    return render_template('view_edition.html', user_data = user, event_data = event, edition_data=edition, rdv_url=rdv_url, time= datetime.now())

@view.route('/<event>/parcours/<parcours>')
def view_parcours_page(event, parcours):
    user_data = current_user if current_user.is_authenticated else None
    event = Event.query.filter_by(name=event).first_or_404(_('view.error.eventdontexist:event').format(event=event))
    parcours = event.parcours.filter_by(name=parcours).first_or_404(_('view.error.parcoursdontexist:parcours').format(parcours=parcours))
    
    element_name, last_path_name, next_path_name, markers_name, program_list, map, graph = create_map_and_alt_graph(parcours)

    #? render the map
    map.get_root().width = '100%'
    map.get_root().height = '450px'
    map.get_root().render()

    header= map.get_root().header.render()
    body= map.get_root().html.render()
    script= map.get_root().script.render()

    folium_map={'header':header, 'body':body, 'script':script}

    return render_template('view_parcours.html', user_data = user_data, parcours = parcours, event_data=event, program_list=program_list, graph=graph, folium_map=folium_map)
