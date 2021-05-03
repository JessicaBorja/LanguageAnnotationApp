from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from .models import RawData, LangData
from . import db

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

    new_langdata = LangData(rawdata_id=rawdata.id, user_id=current_user.id, lang_ann='')
    db.session.add(new_langdata)
    db.session.commit()

    progress = float(LangData.query.count()-1)/float(RawData.query.count())*100
    return render_template("annotate.html", content=rawdata.img_name, progress=progress, user=current_user)

#
# @annotator.route("/confirm", methods=["GET", "POST"])
# @login_required
# def confirm_annotation(answer, lang_data):
#     if request.method=="POST":
#         if request.form.get('no'):
#
#             return redirect(url_for('annotator.annotate', user=current_user))
