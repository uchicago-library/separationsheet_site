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
from wtforms import StringField, IntegerField, TextAreaField

import barcode


__author__ = "Brian Balsamo"
__email__ = "balsamo@uchicago.edu"
__version__ = "0.0.1"


log = logging.getLogger(__name__)


BLUEPRINT = Blueprint('separationsheet_site', __name__,
                      template_folder='templates',
                      static_folder='static')


class JustRemovalForm(FlaskForm):
    acc_no = StringField("Accession Number")
    batch_name = StringField("Batch Name")
    identifier = StringField("Identifier")
    media_type = TextAreaField("Media Type")
    existing_label = TextAreaField("Existing Label")
    note = TextAreaField("Notes")


class BothForm(FlaskForm):
    count = IntegerField("Count")


def make_identifier():
    identifier = \
        ''.join(
            [random.choice(string.ascii_uppercase+string.digits)
             for _ in range(6)]
        )
    return identifier


@BLUEPRINT.route("/")
def root():
    content = """
    <html>
    <body>
    <l>
        <li><a href="/both">Make form pairs</a></li>
        <li><a href="/removal">Make a removal sheet</a></li>
    </l>
    </body>
    </html>
    """
    return content


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
        return render_template(
            "just_removal.html",
            acc_no=request.form['acc_no'],
            batch_name=request.form['batch_name'],
            identifier=request.form['identifier'],
            media_type=request.form['media_type'],
            existing_label=request.form['existing_label'],
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
