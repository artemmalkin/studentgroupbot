import psycopg2
import config

def connect():
    return psycopg2.connect(dbname=config.db_name, user=config.db_user, password=config.db_password, host=config.db_host, port=config.db_port)

def create_tables_if_not_exists():
    commands = (
        """
        CREATE TABLE IF NOT EXISTS groups (
            group_id SERIAL PRIMARY KEY,
            group_name VARCHAR(255) NOT NULL,
            group_password VARCHAR(255)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS students (
            student_id SERIAL PRIMARY KEY,
            student_name VARCHAR(255) NOT NULL,
            group_id INTEGER,
            role VARCHAR(50),
            telegram_id BIGINT,
            FOREIGN KEY (group_id)
                REFERENCES groups (group_id)
                ON UPDATE CASCADE ON DELETE CASCADE,
            UNIQUE (telegram_id)
        );

        CREATE INDEX idx_telegram_id ON students (telegram_id);
        """,
        """
        CREATE TABLE IF NOT EXISTS announcements (
            announcement_id SERIAL PRIMARY KEY,
            announcement_text TEXT NOT NULL,
            confirmed_by INTEGER[],
            creation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS votes (
            vote_id SERIAL PRIMARY KEY,
            vote_title VARCHAR(255),
            options TEXT[],
            results INTEGER[]
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS notes (
            note_id SERIAL PRIMARY KEY,
            note_text TEXT,
            link TEXT,
            student_id INTEGER,
            FOREIGN KEY (student_id)
                REFERENCES students (student_id)
                ON UPDATE CASCADE ON DELETE CASCADE
        )
        """
    )
    conn = connect()
    try:
        cur = conn.cursor()
        for command in commands:
            cur.execute(command)
        cur.close()
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

def drop_tables():
    commands = (
        "DROP TABLE IF EXISTS notes",
        "DROP TABLE IF EXISTS assignments",
        "DROP TABLE IF EXISTS votes",
        "DROP TABLE IF EXISTS reminders",
        "DROP TABLE IF EXISTS students",
        "DROP TABLE IF EXISTS groups"
    )
    conn = connect()
    try:
        cur = conn.cursor()
        for command in commands:
            cur.execute(command)
        cur.close()
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

def add_group(group_name, group_password):
    sql = """INSERT INTO groups(group_name, group_password) VALUES (%s, %s) RETURNING group_id;"""
    conn = connect()
    group_id = None
    try:
        cur = conn.cursor()
        cur.execute(sql, (group_name, group_password))
        group_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
    return group_id

def remove_group(group_id):
    sql = """DELETE FROM groups WHERE group_id = %s;"""
    conn = connect()
    try:
        cur = conn.cursor()
        cur.execute(sql, (group_id,))
        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

def get_group_by_id(group_id):
    sql = """SELECT * FROM groups WHERE group_id = %s;"""
    conn = connect()
    group = None
    try:
        cur = conn.cursor()
        cur.execute(sql, (group_id,))
        group = cur.fetchone()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
    return group

def add_student(student_name, group_id, role):
    sql = """INSERT INTO students(student_name, group_id, role) VALUES (%s, %s, %s) RETURNING student_id;"""
    conn = connect()
    student_id = None
    try:
        cur = conn.cursor()
        cur.execute(sql, (student_name, group_id, role))
        student_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
    return student_id

def remove_student(student_id):
    sql = """DELETE FROM students WHERE student_id = %s;"""
    conn = connect()
    try:
        cur = conn.cursor()
        cur.execute(sql, (student_id,))
        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

def add_reminder(reminder_text):
    sql = """INSERT INTO reminders(reminder_text) VALUES (%s) RETURNING reminder_id;"""
    conn = connect()
    reminder_id = None
    try:
        cur = conn.cursor()
        cur.execute(sql, (reminder_text,))
        reminder_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
    return reminder_id

def confirm_reminder(reminder_id, student_id):
    sql = """UPDATE reminders SET confirmed_by = array_append(confirmed_by, %s) WHERE reminder_id = %s;"""
    conn = connect()
    try:
        cur = conn.cursor()
        cur.execute(sql, (student_id, reminder_id))
        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

def remove_reminder(reminder_id):
    sql = """DELETE FROM reminders WHERE reminder_id = %s;"""
    conn = connect()
    try:
        cur = conn.cursor()
        cur.execute(sql, (reminder_id,))
        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

def add_vote(vote_title, options):
    sql = """INSERT INTO votes(vote_title, options, results) VALUES (%s, %s, %s) RETURNING vote_id;"""
    conn = connect()
    vote_id = None
    try:
        cur = conn.cursor()
        cur.execute(sql, (vote_title, options, [0]*len(options)))
        vote_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
    return vote_id

def remove_vote(vote_id):
    sql = """DELETE FROM votes WHERE vote_id = %s;"""
    conn = connect()
    try:
        cur = conn.cursor()
        cur.execute(sql, (vote_id,))
        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

def vote(vote_id, option_index):
    sql = """UPDATE votes SET results[%s] = results[%s] + 1 WHERE vote_id = %s;"""
    conn = connect()
    try:
        cur = conn.cursor()
        cur.execute(sql, (option_index + 1, option_index + 1, vote_id))
        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

def add_assignment(assignment_description):
    sql = """INSERT INTO assignments(assignment_description, students_assigned) VALUES (%s, %s) RETURNING assignment_id;"""
    conn = connect()
    assignment_id = None
    try:
        cur = conn.cursor()
        cur.execute(sql, (assignment_description, []))
        assignment_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
    return assignment_id

def assign_task(assignment_id, student_id):
    sql = """UPDATE assignments SET students_assigned = array_append(students_assigned, %s) WHERE assignment_id = %s;"""
    conn = connect()
    try:
        cur = conn.cursor()
        cur.execute(sql, (student_id, assignment_id))
        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

def remove_assignment(assignment_id):
    sql = """DELETE FROM assignments WHERE assignment_id = %s;"""
    conn = connect()
    try:
        cur = conn.cursor()
        cur.execute(sql, (assignment_id,))
        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

def add_note(note_text, link, student_id):
    sql = """INSERT INTO notes(note_text, link, student_id) VALUES (%s, %s, %s) RETURNING note_id;"""
    conn = connect()
    note_id = None
    try:
        cur = conn.cursor()
        cur.execute(sql, (note_text, link, student_id))
        note_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
    return note_id

def remove_note(note_id):
    sql = """DELETE FROM notes WHERE note_id = %s;"""
    conn = connect()
    try:
        cur = conn.cursor()
        cur.execute(sql, (note_id,))
        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
