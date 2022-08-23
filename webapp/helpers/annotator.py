import json
from telnetlib import SE

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from webapp import colors, data_manager, db, tasks

from .models import LangAnn, Sequences

annotator = Blueprint("annotator", __name__)  # set up blueprint


@annotator.route("/annotator", methods=["GET", "POST"])
@login_required
def annotate():
    if request.method == "POST":
        # Handle requests coming from annotate.html
        # To save to database
        if request.form["submit_button"] == "next" or request.form["submit_button"] == "no_task":
            _ids_annotated = db.session.query(LangAnn.id).all()
            _user_ann_seq = db.session.query(LangAnn).filter(LangAnn.user_id==current_user.id)
            _user_ann_seq = _user_ann_seq.all()
            if len(_user_ann_seq) > 0:
                # Get last annotation
                seq_id = max([ann.seq_id for ann in _user_ann_seq])[0] + 1
            else:
                if len(_ids_annotated) > 0:
                    seq_id = max(_ids_annotated)[0] + 1 
                else:
                    seq_id = 1
            
            # If sequence_id is not labeled
            if(seq_id < LangAnn.query.count()):
                # Save to database
                if "color_x" in request.form:
                    color_x = request.form["color_x"]
                else:
                    color_x = ""

                if "color_y" in request.form:
                    color_y = request.form["color_y"]
                else:
                    color_y = ""

                new_langdata = LangAnn(
                    seq_id=seq_id,
                    user_id=current_user.id,
                    task=request.form["task"] if request.form["submit_button"] == "next" else "no_task",
                    annotation="",
                    color_x=color_x,
                    color_y=color_y,
                )
                db.session.add(new_langdata)
                db.session.commit()
            seq_id += 1
        elif request.form["submit_button"] == "end":
            return redirect(url_for("views.home"))
    else:
        # GET: Loading for first time
        try:
            seq_id = max(db.session.query(LangAnn.seq_id).all())[0] + 1
            if seq_id - 1 >= Sequences.query.count():
                return redirect(url_for("views.completed"))
        except Exception:
            print("Starting LangData table!")
            seq_id = 1

    seq = Sequences.query.filter_by(seq_id=seq_id).first()
    if seq is None:
        return redirect(url_for("views.completed"))
    progress = float(LangAnn.query.count()) / float(Sequences.query.count()) * 100
    filename = data_manager.video_tags[int(seq.start_frame), int(seq.end_frame)]
    if not data_manager.check_exists(filename):
        filename = data_manager.create_tmp_video(seq.start_frame, seq.end_frame, seq.dir)
    return render_template(
        "annotate.html", content=filename, progress=progress, tasks=tasks, colors=colors, user=current_user
    )


# @annotator.route('/get_video', methods = ['GET'])
# def get_video():
#     video = 'static/images/tmp.webM'
#     return json.dumps({'video':video})
