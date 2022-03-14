from telnetlib import SE
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from .models import Sequences, LangAnn
from webapp import db

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
            all_being_annotated = LangAnn.query.filter_by(lang_ann='')
            langdata = all_being_annotated.filter_by(user_id=current_user.id).first()
            langdata.lang_ann = request.form['lang_ann']
            db.session.commit()
            seq_id = max(db.session.query(LangAnn.id).all())[0]+1

    else:
        try:
            seq_id = max(db.session.query(LangAnn.id).all())[0]+1
            if seq_id-1 == Sequences.query.count():
                return redirect(url_for('views.completed'))
        except Exception:
            print("Starting LangData table!")
            seq_id = 1

    seq = Sequences.query.filter_by(id=seq_id).first()
    if seq == None:
        return redirect(url_for('views.completed'))

    new_langdata = LangAnn(seq_id=seq.id, user_id=current_user.id, lang_ann='')
    db.session.add(new_langdata)
    db.session.commit()

    progress = float(LangAnn.query.count()-1)/float(Sequences.query.count())*100
    return render_template("annotate.html", content=seq.img_name, progress=progress, user=current_user)

#
# @annotator.route("/confirm", methods=["GET", "POST"])
# @login_required
# def confirm_annotation(answer, lang_data):
#     if request.method=="POST":
#         if request.form.get('no'):
#
#             return redirect(url_for('annotator.annotate', user=current_user))
