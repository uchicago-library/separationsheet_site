"""
separationsheet_site
"""
import logging
import random
import string
from io import BytesIO
from tempfile import TemporaryDirectory
from uuid import uuid4
from os.path import join

from flask import Blueprint, render_template, send_file, request
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField, SelectField, ValidationError
from wtforms.validators import DataRequired

import barcode

from .. import mongo


__author__ = "Brian Balsamo"
__email__ = "balsamo@uchicago.edu"
__version__ = "0.0.1"


log = logging.getLogger(__name__)


BLUEPRINT = Blueprint('separationsheet_site', __name__,
                      template_folder='../templates',
                      static_folder='../static')


# TODO: Make these into a real validator
def onlyOtherRestriction(form, field):
    if field.data and form.restriction.data != "Other":
        raise ValidationError("Restriction Dropdown not set to 'Other'")


def onlyOtherMediaType(form, field):
    if field.data and form.media_type.data != "Other":
        raise ValidationError("Restriction Dropdown not set to 'Other'")


class JustRemovalForm(FlaskForm):
    acc_no = StringField("Accession Number", [DataRequired()])
    batch_name = StringField("Batch Name", [DataRequired()])
    identifier = StringField("Identifier", [DataRequired()])
    restriction = SelectField(
        "Restriction",
        choices=[
            ('', 'None'),
            ('R-30', 'R-30'),
            ('R-50', 'R-50'),
            ('R-80', 'R-80'),
            ('R-X', 'R-X'),
            ('Other', 'Other')
        ]
    )
    restriction_freetype = TextAreaField("Other Restriction", [onlyOtherRestriction])
    media_type = SelectField(
        "Media Type",
        choices=[
            ('', 'None'),
            ("3.5\" Floppy Disk", "3.5\" Floppy Disk"),
            ("CD", "CD"),
            ("DVD", "DVD"),
            ("Flash Drive", "Flash Drive"),
            ("External Hard Drive", "External Hard Drive"),
            ("Other", "Other")
        ]
    )
    media_type_freetype = TextAreaField("Other Media Type", [onlyOtherMediaType])
    existing_label = TextAreaField("Existing Label")
    note = TextAreaField("Notes")


class BothForm(FlaskForm):
    count = IntegerField("Count")


class FakeDB:
    def __init__(self):
        self.records = {}

    def write_record(self, record):
        unmulti = {x: record[x][0] for x in record}
        self.records[unmulti['identifier']] = unmulti

    def list_records(self, cursor=0):
        return mongo.db.separationshieet.sheets.find()

    def get_record(self, q):
        return self.records[q]


db = FakeDB()


def make_identifier():
    identifier = \
        ''.join(
            [random.choice(string.ascii_uppercase+string.digits)
             for _ in range(6)]
        )
    return identifier


@BLUEPRINT.route("/")
def root():
    return render_template("index.html")


@BLUEPRINT.route("/list")
def list():
    records = db.list_records()
    for x in records:
        x['link'] = "/view/{}".format(x['identifier'])
    return render_template(
        "list.html",
        records=records
    )


@BLUEPRINT.route("/view/<string:identifier>")
def view(identifier):
    record = db.get_record(identifier)
    return render_template(
        "just_removal.html",
        acc_no=record['acc_no'],
        batch_name=record['batch_name'],
        identifier=record['identifier'],
        media_type=record['media_type'],
        media_type_freetype=record['media_type_freetype'],
        existing_label=record['existing_label'],
        restriction=record['restriction'],
        restriction_freetype=record['restriction_freetype'],
        note=record['note']
    )


@BLUEPRINT.route("/both", methods=['GET', 'POST'])
def both():
    form = BothForm()
    # POST
    if form.validate_on_submit():
        return render_template(
            "both_sheets.html",
            identifiers=[make_identifier() for _ in range(int(request.form['count']))]
        )
    # GET
    else:
        return render_template(
            'both_form.html',
            form=form
        )


@BLUEPRINT.route("/removal", methods=['GET', 'POST'])
def just_removal():
    form = JustRemovalForm()
    # POST
    if form.validate_on_submit():
        form_dict = dict(request.form)
        db.write_record(form_dict)
        return render_template(
            "just_removal.html",
            acc_no=request.form['acc_no'],
            batch_name=request.form['batch_name'],
            identifier=request.form['identifier'],
            media_type=request.form['media_type'],
            media_type_freetype=request.form['media_type_freetype'],
            existing_label=request.form['existing_label'],
            restriction=request.form['restriction'],
            restriction_freetype=request.form['restriction_freetype'],
            note=request.form['note']
        )
    else:
        return render_template(
            'removal_form.html',
            form=form
        )


@BLUEPRINT.route("/barcode/<string:code>")
def barcode_generator(code):
    bc = barcode.codex.Code39(code, add_checksum=False, writer=barcode.writer.ImageWriter())
    barcode_image = BytesIO()
    with TemporaryDirectory() as tmpdir:
        tmpfile = join(tmpdir, uuid4().hex)
        bc.save(
            tmpfile,
            options={
                'write_text': False,
                'quiet_zone': 2,
                'dpi': 300,
                'module_height': 4
            }
        )
        with open(tmpfile + ".png", 'rb') as f:
            barcode_image.write(f.read())
    barcode_image.seek(0)
    return send_file(barcode_image, mimetype="image/png")
