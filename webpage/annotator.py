from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from .models import RawData, LangData
from . import db
from sqlalchemy.sql import func
import datetime

annotator = Blueprint('annotator', __name__)  # set up blueprint


@annotator.route("/annotator", methods=['GET', 'POST'])
@login_required
def annotate():
    if request.method == "POST":
        if request.form.get('done'):
            flash("Thank you for your contribution!")
            return redirect(url_for('auth.logout', user=current_user))
        else:
            print(current_user.id)
            all_being_annotated = LangData.query.filter_by(lang_ann='')
            langdata = all_being_annotated.filter_by(user_id=current_user.id).first()
            langdata.lang_ann = request.form['lang_ann']
            db.session.commit()
            rawdata_id = max(db.session.query(LangData.id).all())[0]+1

    else:

        try:
            rawdata_id = max(db.session.query(LangData.id).all())[0]+1
            if rawdata_id-1 == RawData.query.count():
                return redirect(url_for('views.completed'))
        except Exception:
            print("Starting LangData table!")
            rawdata_id = 1

    rawdata = RawData.query.filter_by(id=rawdata_id).first()

    if rawdata == None:
        return redirect(url_for('views.completed'))

    empty_ann = LangData.query.filter_by(lang_ann='')
    empty_ann.filter_by(user_id=current_user.id).delete()
    db.session.commit()

    new_langdata = LangData(rawdata_id=rawdata.id, user_id=current_user.id, lang_ann='')
    db.session.add(new_langdata)
    db.session.commit()

    progress = round(float(LangData.query.count()-1)/float(RawData.query.count())*100)
    return render_template("annotate.html", content=rawdata.img_name, progress=progress, user=current_user)


@annotator.route("contributions", methods=['GET', 'POST'])
@login_required
def my_contributions():
    if request.method=="POST":
        id_update = int(list(request.form)[0])
        lang_ann_update = LangData.query.filter_by(id=id_update).first()
        return redirect(url_for('annotator.update_annotation', lang_update_id=lang_ann_update.id, user=current_user))
    else:
        empty_ann = LangData.query.filter_by(lang_ann='')
        empty_ann.filter_by(user_id=current_user.id).delete()
        db.session.commit()
        usr_annotations = list(reversed(LangData.query.filter_by(user_id=current_user.id).all()))
        user_progress = float(LangData.query.filter_by(user_id=current_user.id).count()) / float(LangData.query.count())*100
        return render_template('contributions.html', annotations=usr_annotations, user=current_user, user_progress=user_progress, time=datetime.datetime.now())


@annotator.route("/update/<lang_update_id>", methods=['GET', 'POST'])
@login_required
def update_annotation(lang_update_id):
    if request.method=="POST":
        if request.form.get('update'):
            lang_update = LangData.query.filter_by(id=int(lang_update_id)).first()
            lang_update.lang_ann = request.form['lang_ann']
            db.session.commit()
        return redirect(url_for('annotator.my_contributions'))

    else:
        lang_update = LangData.query.filter_by(id=int(lang_update_id)).first()
        rawdata = RawData.query.filter_by(id=lang_update.rawdata_id).first()
        return render_template('update.html', content=rawdata.img_name, lang_ann=lang_update.lang_ann, user=current_user)
