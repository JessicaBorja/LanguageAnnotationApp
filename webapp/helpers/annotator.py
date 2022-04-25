import json
from telnetlib import SE

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from webapp import data_manager, db, tasks

from .models import LangAnn, Sequences

annotator = Blueprint("annotator", __name__)  # set up blueprint


@annotator.route("/annotator", methods=["GET", "POST"])
@login_required
def annotate():
    if request.method == "POST":
        # Handle requests comming from annotate.html
        # To save to database
        if request.form["submit_button"] == "next":
            print(current_user.id)
            _curr_ids = db.session.query(LangAnn.id).all()
            if len(_curr_ids) > 0:
                seq_id = max(_curr_ids)[0] + 1
            else:
                seq_id = 1
            new_langdata = LangAnn(
                seq_id=seq_id, user_id=current_user.id, task=request.form["task"], lang_ann=request.form["lang_ann"]
            )
            db.session.add(new_langdata)
            db.session.commit()
            seq_id += 1
        elif request.form["submit_button"] == "end":
            return redirect(url_for("views.home"))
    else:
        # GET: Loading for first time
        try:
            seq_id = max(db.session.query(LangAnn.id).all())[0] + 1
            if seq_id - 1 >= Sequences.query.count():
                return redirect(url_for("views.completed"))
        except Exception:
            print("Starting LangData table!")
            seq_id = 1

    seq = Sequences.query.filter_by(id=seq_id).first()
    if seq is None:
        return redirect(url_for("views.completed"))
    progress = float(LangAnn.query.count()) / float(Sequences.query.count()) * 100
    filename = data_manager.create_tmp_video(seq.start_frame, seq.end_frame, seq.dir, seq_id)
    return render_template("annotate.html", content=filename, progress=progress, tasks=tasks, user=current_user)


# @annotator.route('/get_video', methods = ['GET'])
# def get_video():
#     video = 'static/images/tmp.webM'
#     return json.dumps({'video':video})
