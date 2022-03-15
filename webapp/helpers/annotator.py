from telnetlib import SE
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from .models import Sequences, LangAnn
from webapp import db, data_manager, tasks


annotator = Blueprint('annotator', __name__)  # set up blueprint

@annotator.route("/annotator", methods=['GET', 'POST'])
@login_required
def annotate():
    if request.method == "POST":
        if request.form.get('done'):
            flash("Thank you for your contribution!")
            return redirect(url_for('auth.logout', user=current_user))
        else:
            # Handle requests comming from annotate.html
            # To save to database
            print(current_user.id)
            _curr_ids = db.session.query(LangAnn.id).all()
            if len(_curr_ids) > 0:
                seq_id=max(_curr_ids)[0] + 1
            else:
                seq_id=1
            new_langdata = LangAnn(seq_id=seq_id,
                                   user_id=current_user.id,
                                   task=request.form['task'],
                                   lang_ann=request.form['lang_ann'])
            db.session.add(new_langdata)
            db.session.commit()
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
    progress = float(LangAnn.query.count()-1)/float(Sequences.query.count())*100
    data_manager.create_tmp_video(seq.start_frame, seq.end_frame, seq.dir)
    return render_template("annotate.html",
                            content="tmp.webM",
                            progress=progress,
                            tasks=tasks,
                            user=current_user)

# @app.route('/')
# def index():
#     return render_template('index.html')

# def gen(camera):
#     while True:
#         frame = camera.get_frame()
#         yield (b'--frame\r\n'
#                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# @app.route('/video_feed')
# def video_feed():
#     return Response(gen(Camera()),
#                     mimetype='multipart/x-mixed-replace; boundary=frame')