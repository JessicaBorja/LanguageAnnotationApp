import os
import sqlite3
from sqlite3 import Error
import hydra
import numpy as np
from pip import main
import webapp

def create_connection(db_file):
    """create a database connection to the SQLite database
        specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    return conn


def get_annotations(conn, ignore_empty_tasks=True):
    """
    Query all rows in the lang_ann table
    :param conn: the Connection object
    :return:
    """

    sql_query = """
    SELECT lang_ann.task, lang_ann.color_x, lang_ann.color_y, sequences.start_frame, sequences.end_frame
    FROM lang_ann INNER JOIN sequences ON lang_ann.seq_id=sequences.seq_id
    """
    if ignore_empty_tasks:
        sql_query += '''WHERE lang_ann.task!="no_task"'''
    
    sql_query += ";"
    cur = conn.cursor()
    cur.execute(sql_query)

    rows = cur.fetchall()

    return rows


def filename_to_idx(filename):
    return int(filename.split("_")[-1][:-4])


def compose_task(task, color_x, color_y):
    if '[x]' in task:
        task = task.replace('[x]', color_x)
    if '[y]' in task:
        task = task.replace('[y]', color_y)
    return task


@hydra.main(config_path="config", config_name="retrieve_data")
def main(cfg):
    data = {
        "language": {"ann": [], "task": [], "emb": []},
        "info": {"episodes": [], "indx": []},
    }  # type: typing.Dict

    # Get language model
    nlp_model = hydra.utils.instantiate(cfg.lang_model)

    # Get database connection
    db_path = hydra.utils.get_original_cwd()
    db_path = os.path.join(db_path, cfg.database_path)
    conn = create_connection(db_path)

    # Get database data
    rows = get_annotations(conn, cfg.ignore_empty_tasks)
    for task, color_x, color_y, start_fr, end_fr in rows:
        ann = compose_task(task, color_x, color_y)
        task = compose_task(task, color_x, color_y)
        data["language"]["ann"].append(ann)
        data["language"]["task"].append(task)
        data["language"]["emb"].append(nlp_model(ann).cpu().numpy())

        start_idx = filename_to_idx(start_fr)
        end_idx = filename_to_idx(end_fr)
        data["info"]["indx"].append((start_idx, end_idx))

    save_path = hydra.utils.get_original_cwd()
    save_path = os.path.join(db_path, cfg.save_path)
    save_file = os.path.join(save_path, "auto_lang_ann.npy")
    np.save(save_file, data)
    return


if __name__ == "__main__":
    main()
