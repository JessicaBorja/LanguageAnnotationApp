from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from flask_login import login_required, current_user
from webapp import db
from .models import LangAnn, Sequences
from webapp.helpers.data_utils import DataManager
from webapp import data_manager
import json


views = Blueprint('views', __name__)  # set up blueprint

def get_sequences():

    return data_manager.data

@views.route("/", methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        return redirect(url_for('annotator.annotate', user=current_user))
    else:
        if Sequences.query.count() < 1:
            data = get_sequences()
            for info in data:
                start, end = info['indx'][:2]
                new_data_point = Sequences(dir=info['dir'],
                                           n_frames=info['n_frames'],
                                           start_frame=start,
                                           end_frame=end)
                db.session.add(new_data_point)
            db.session.commit()
        return render_template('home.html', user=current_user)


@views.route("/completed")
@login_required
def completed():
    flash("\nData collection completed successfully!\n Congratulations!")
    return render_template('completed.html', user=current_user)


