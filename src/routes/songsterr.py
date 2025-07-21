from flask import Blueprint, render_template, request, jsonify
from src.database.models import db, SongsterrLink

songsterr_bp = Blueprint('songsterr', __name__)

@songsterr_bp.route('/manage-songsterr-links', methods=['GET', 'POST'])
def manage_links():
    message = None
    message_type = None
    if request.method == 'POST':
        song_name = request.form.get('song_name')
        songsterr_link = request.form.get('songsterr_link')
        try:
            last_order = db.session.query(db.func.max(SongsterrLink.display_order)).scalar() or 0
            new_link = SongsterrLink(
                song_name=song_name,
                songsterr_link=songsterr_link,
                display_order=last_order + 1
            )
            db.session.add(new_link)
            db.session.commit()
            message = f"Lien ajouté pour '{song_name}' !"
            message_type = 'success'
        except Exception as e:
            db.session.rollback()
            message = f"Erreur lors de l'ajout : {str(e)}"
            message_type = 'error'
    links = SongsterrLink.query.order_by(SongsterrLink.display_order).all()
    return render_template('songsterr_links.html', links=links, message=message, message_type=message_type)

@songsterr_bp.route('/delete-songsterr-link/<song_name>', methods=['POST'])
def delete_link(song_name):
    message = None
    message_type = None
    try:
        link = SongsterrLink.query.filter_by(song_name=song_name).first_or_404()
        db.session.delete(link)
        db.session.commit()
        message = f"Lien supprimé pour '{song_name}' !"
        message_type = 'success'
    except Exception as e:
        db.session.rollback()
        message = f"Erreur lors de la suppression : {str(e)}"
        message_type = 'error'
    links = SongsterrLink.query.all()
    return render_template('songsterr_links.html', links=links, message=message, message_type=message_type)

@songsterr_bp.route('/update-songsterr-links-order', methods=['POST'])
def update_links_order():
    try:
        data = request.get_json()
        new_order = data.get('order', [])
        for index, link_id in enumerate(new_order):
            link = SongsterrLink.query.get(link_id)
            if link:
                link.display_order = index
        db.session.commit()
        return jsonify({'message': 'Ordre mis à jour avec succès'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
