from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from flask_login import login_required, current_user
from webapp import db
from .models import LangAnn, Sequences
import json


views = Blueprint('views', __name__)  # set up blueprint


@views.route("/", methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        return redirect(url_for('annotator.annotate', user=current_user))
    else:
        if Sequences.query.count() < 1:
            with open('./webapp/static/images/dataset.json') as json_file:
                data = json.load(json_file)
                for i, img_dir in enumerate(data['images']):
                    start, end = data['info']['indx'][i][:2]
                    new_data_point = Sequences(img_name=img_dir,
                                               n_frames=end-start,
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


