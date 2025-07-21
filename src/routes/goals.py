from flask import Blueprint, render_template, request, redirect, url_for
from src.database.models import db, GuitarGoal

goals_bp = Blueprint('goals', __name__)

@goals_bp.route('/guitar-goals', methods=['GET', 'POST'])
def guitar_goals():
    if request.method == 'POST':
        try:
            new_goal = GuitarGoal(
                title=request.form['title'],
                description=request.form['description'],
                category=request.form['category'],
                progress=int(request.form['progress']),
                target_bpm=int(request.form['target_bpm']) if request.form['target_bpm'] else None
            )
            db.session.add(new_goal)
            db.session.commit()
            message = "Objectif ajouté avec succès !"
            mtype = 'success'
        except Exception as e:
            db.session.rollback()
            message = f"Erreur lors de l'ajout de l'objectif : {str(e)}"
            mtype = 'error'
        goals = GuitarGoal.query.all()
        return render_template('guitar_goals.html', goals=goals, message=message, message_type=mtype)
    goals = GuitarGoal.query.all()
    return render_template('guitar_goals.html', goals=goals)

@goals_bp.route('/edit-goal/<int:goal_id>', methods=['GET', 'POST'])
def edit_goal(goal_id):
    goal = GuitarGoal.query.get_or_404(goal_id)
    if request.method == 'POST':
        try:
            goal.title = request.form['title']
            goal.description = request.form['description']
            goal.category = request.form['category']
            goal.progress = int(request.form['progress'])
            goal.target_bpm = int(request.form['target_bpm']) if request.form['target_bpm'] else None
            db.session.commit()
            return redirect(url_for('goals.guitar_goals'))
        except Exception as e:
            db.session.rollback()
            return render_template('edit_goal.html', goal=goal, message=f"Erreur : {str(e)}", message_type='error')
    return render_template('edit_goal.html', goal=goal)

@goals_bp.route('/delete-goal/<int:goal_id>')
def delete_goal(goal_id):
    try:
        goal = GuitarGoal.query.get_or_404(goal_id)
        db.session.delete(goal)
        db.session.commit()
        message = "Objectif supprimé avec succès !"
        mtype = 'success'
    except Exception as e:
        db.session.rollback()
        message = f"Erreur lors de la suppression : {str(e)}"
        mtype = 'error'
    goals = GuitarGoal.query.all()
    return render_template('guitar_goals.html', goals=goals, message=message, message_type=mtype)
