from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from flask_login import login_required, current_user
from webapp import db
from .models import RawData, LangAnn, Sequences
import json


views = Blueprint('views', __name__)  # set up blueprint


@views.route("/", methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        return redirect(url_for('annotator.annotate', user=current_user))
    else:
        if Sequences.query.count() < 1:
            with open('./webpage/static/images/dataset.json') as json_file:
                data = json.load(json_file)
                for i, img_dir in enumerate(data['images']):
                    new_data_point = RawData(img_name=img_dir, start_frame=data['info']['indx'][i][0],
                                             end_frame=data['info']['indx'][i][1])
                    db.session.add(new_data_point)
                db.session.commit()
        return render_template('home.html', user=current_user)


@views.route("/completed")
@login_required
def completed():
    flash("\nData collection completed successfully!\n Congratulations!")
    return render_template('completed.html', user=current_user)


