from pydoc import render_doc
from flask import Blueprint, current_app, request, make_response, render_template
from markupsafe import escape
import os

from .dashcamFTP import Dashcam
import sqlite3

DB_PATH = os.environ.get("VT_AUTOMATOR_DB_PATH", "dashcam.db")

dashcam_tables = [
    """CREATE TABLE IF NOT EXISTS dashcams(
        ip TEXT PRIMARY KEY,
        user TEXT NOT NULL,
        password TEXT NOT NULL,
        ingestDirectory TEXT NOT NULL
    );
    """
]

bp = Blueprint("main", __name__)

try:
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        for statement in dashcam_tables:
            cursor.execute(statement)
        conn.commit()
        print("Created tables")
        pass
except sqlite3.OperationalError as e:
    print("Failed to open database:", e)


def addDashcam(ip: str, user: str, password: str, ingestDirectory: str) -> bool:
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            statement = """INSERT INTO dashcams(ip,user,password,ingestDirectory)
                           VALUES(?,?,?,?);"""
            dashcam = [ip, user, password, ingestDirectory]
            cursor.execute(statement, dashcam)
            return True
    except sqlite3.Error as e:
        print(e)
        return False


def getDashcams():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        statement = """SELECT * FROM dashcams;"""
        cursor.execute(statement)
        rows = cursor.fetchall()
        return rows


def getDashcam(ip: str, password: bool = False):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        if password:
            statement = """SELECT ip,user,password,ingestDirectory FROM dashcams WHERE ip = ?;"""
        else:
            statement = """SELECT ip,user,ingestDirectory FROM dashcams WHERE ip = ?;"""
        cursor.execute(statement, [ip])
        row = cursor.fetchone()
        return row


def updateDashcam(ip: str, user: str, ingestDirectory: str, password: str = "") -> bool:
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            statement = """UPDATE dashcams
                            SET ip = ?, user = ?, ingestDirectory = ?
                            WHERE ip = ?;"""
            dashcam = [ip, user, ingestDirectory, ip]
            if password != "REDACTED":
                statement = """UPDATE dashcams
                            SET ip = ?, user = ?, password = ?, ingestDirectory = ?
                            WHERE ip = ?;"""
                dashcam = [ip, user, password, ingestDirectory, ip]
                print(f"Updating password: {dashcam}")
            cursor.execute(statement, dashcam)
            return True
    except sqlite3.Error as e:
        print(e)
        return False


def deleteDashcam(ip: str):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            statement = """DELETE FROM dashcams WHERE ip = ?;"""

            cursor.execute(statement, [ip])
            return True
    except sqlite3.Error as e:
        print(e)
        return False


@bp.route("/")
def pageDashcams():
    dashcams = getDashcams()
    print(dashcams)
    return render_template("dashcams.html", dashcams=dashcams)


@bp.route("/dashcam/new", methods=["GET", "POST"])
def pageNewDashcam():
    if request.method == "GET":
        return render_template("addDashcam.html")
    elif request.method == "POST":
        ip = request.form["ip"]
        user = request.form["user"]
        password = request.form["password"]
        ingestDirectory = request.form["ingestDir"]
        if addDashcam(ip, user, password, ingestDirectory):
            return "<p>Success!</p>"
        else:
            resp = make_response(
                "<p>Dashcam could not be added. Please see server logs</p>", 500
            )
            return resp


@bp.route("/dashcam/delete/<ip>")
def pageDeleteDashcam(ip):
    ipSanitised = escape(ip)
    if deleteDashcam(ipSanitised):
        return f"<p>Dashcam {ipSanitised} deleted</p>"
    else:
        resp = make_response(
            "<p>Dashcam could not be deleted. Please see server logs</p>", 500
        )
        return resp


@bp.route("/dashcam/update/<ip>", methods=["GET", "POST"])
def pageUpdateDashcam(ip):
    ipSanitised = escape(ip)
    dashcam = getDashcam(ipSanitised)
    if request.method == "GET":
        return render_template("updateDashcam.html", details=dashcam)
    elif request.method == "POST":
        providedIp = request.form["ip"]
        user = request.form["user"]
        password = request.form["password"]
        ingestDirectory = request.form["ingestDir"]
        updateResult = False

        print(f"Password provided: {password}")
        if password == "REDACTED":
            updateResult = updateDashcam(providedIp, user, ingestDirectory)
        else:
            updateResult = updateDashcam(
                providedIp, user, ingestDirectory, password=password
            )

        if updateResult:
            return "<p>Success!</p>"
        else:
            resp = make_response(
                "<p>Dashcam could not be added. Please see server logs</p>", 500
            )
            return resp


@bp.route("/dashcam/ingest/<ip>")
def pageIngestDashcam(ip):
    ipSanitised = escape(ip)
    details = getDashcam(ipSanitised, password=True)
    ingestDirectory = details[3]
    dashcam = Dashcam(ip=ipSanitised, user=details[1], password=details[2])
    dashcam.downloadEventFiles(ingestDirectory, deleteFiles=False)
    return f"<p>Downloading files from {ipSanitised}"
