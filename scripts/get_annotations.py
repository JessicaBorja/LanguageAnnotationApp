import os
import sqlite3
from sqlite3 import Error

import numpy as np
from pip import main


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


def get_annotations(conn):
    """
    Query all rows in the lang_ann table
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    cur.execute(
        """
    SELECT lang_ann.annotation, lang_ann.task, sequences.start_frame, sequences.end_frame
    FROM lang_ann INNER JOIN sequences ON lang_ann.seq_id=sequences.seq_id;
    """
    )

    rows = cur.fetchall()

    return rows


def filename_to_idx(filename):
    return int(filename.split("_")[-1][:-4])


def main(save_path):
    data = {
        "language": {"ann": [], "task": [], "emb": []},
        "info": {"episodes": [], "indx": []},
    }  # type: typing.Dict
    conn = create_connection(
        "/mnt/ssd_shared/Users/Jessica/Documents/Thesis_ssd/LanguageAnnotationApp/webapp/database.db"
    )
    rows = get_annotations(conn)
    for ann, task, start_fr, end_fr in rows:
        data["language"]["ann"].append(ann)
        data["language"]["task"].append(task)

        start_idx = filename_to_idx(start_fr)
        end_idx = filename_to_idx(end_fr)
        data["info"]["indx"].append((start_idx, end_idx))

    save_file = os.path.join(save_path, "auto_lang_ann.npy")
    np.save(save_file, data)
    return


if __name__ == "__main__":
    save_path = "./scripts/"
    main(save_path)
