from flask import Flask, request, render_template, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request, render_template, redirect, url_for, send_file
import os
import pdfkit
import pdfkit
from PyPDF2 import PdfMerger
from datetime import datetime
from werkzeug.utils import secure_filename
from utils import generate_cover_pdf, generate_second_page_with_info, reference_images_to_pdf
from werkzeug.security import generate_password_hash, check_password_hash
from flask import send_from_directory
import os


from sqlalchemy.orm import aliased
from PIL import Image, ImageDraw, ImageFont
import platform
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///forms.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

import fitz  # PyMuPDF

def fill_blanks_with_coordinates(form_id,fill_values):
    input_pdf = "risk_assestment_matrix.pdf"
    coordinates = [
    (179, 423),  # x=100, y=200
    (271, 423),  # x=200, y=200
    (362, 423),  # x=300, y=200
    ]

    output_pdf_path = f"risk_assestment_matrix_output{form_id}.pdf"
    """
    Fill blanks in a PDF by placing text at specified coordinates.

    :param input_pdf_path: Path to the input PDF.
    :param output_pdf_path: Path to save the modified PDF.
    :param fill_values: List of values to fill in the blanks.
    :param coordinates: List of tuples with coordinates (x, y) for each value.
    """
    # Open the PDF
    pdf_document = fitz.open(input_pdf)
    page = pdf_document[0]  # Assuming there is only one page

    # Iterate over each blank to fill
    for i, (x, y) in enumerate(coordinates):
        if i < len(fill_values):
            text = str(fill_values[i])
            page.insert_text((x, y), text, fontsize=8, color=(0, 0, 0))

    # Save the modified PDF
    pdf_document.save(output_pdf_path)
    pdf_document.close()



def get_answer_by_form_id(form_id):
    # Query each question separately by form_id and question_id
    address = db.session.query(PrimaryAnswer.answer).filter_by(form_id=form_id, question_id="0.02").first()
    assessment_date = db.session.query(PrimaryAnswer.answer).filter_by(form_id=form_id, question_id="0.08").first()
    next_assessment_date = db.session.query(PrimaryAnswer.answer).filter_by(form_id=form_id, question_id="0.08").first()
    assessor = db.session.query(PrimaryAnswer.answer).filter_by(form_id=form_id, question_id="0.04").first()
    responsible_person = db.session.query(PrimaryAnswer.answer).filter_by(form_id=form_id, question_id="0.01").first()

    # Check if all results are found
    if address and assessment_date and next_assessment_date and assessor and responsible_person:
        return {
            "address": address[0],  # Extracting the answer from the tuple
            "assessment_date": assessment_date[0],
            "next_assessment_date": next_assessment_date[0],
            "assessor": assessor[0],
            "responsible_person": responsible_person[0]
        }
    else:
        return None




""" QUESTIONS AND PRIMARY QUESTIONS ARE FOR THE NON HOUSING REQUIREMENT 


"""


PRIMARY_HOUSING_QUESTIONS = [
    {"id": "0.01", "question": "Responsible person (e.g. employer) or person having control of premises?"},
    {"id": "0.02", "question": "Address of premises?"},
    {"id": "0.03", "question": "Person(s) consulted?"},
    {"id": "0.04", "question": "Assessor?"},
    {"id": "0.05", "question": "Assessors statement?"},
    {"id": "0.06", "question": "Report validated by?"},
    {"id": "0.07", "question": "Date of fire risk assessment?"},
    {"id": "0.08", "question": "Date of previous fire risk assessment?"},
    {"id": "0.09", "question": "Suggested date for review?"},
    {"id": "0.10", "question": "Fire Risk Assessment Review?"},
    {"id": "0.11", "question": "Report compliance?"},
    {"id": "1.01", "question": "Number of floors at ground level and above"},
    {"id": "1.02", "question": "Number of floors entirely below ground level"},
    {"id": "1.03", "question": "Floors on which car parking is provided"},
    {"id": "1.04", "question": "Number of flats"},
    {"id": "1.05", "question": "Approximate gross floor area"},
    {"id": "1.06", "question": "Brief details of construction and approximate age of building"},
    {"id": "1.07", "question": "Occupancy"},
    {"id": "2.01", "question": "Approximate maximum number of employees at any one time"},
    {"id": "2.02", "question": "Approximate maximum number of residents and visitors at any one time"},
    {"id": "3.01", "question": "Sleeping occupants"},
    {"id": "3.02", "question": "Occupants in remote areas and lone workers"},
    {"id": "3.03", "question": "Others"},
    {"id": "3.04", "question": "Disabled occupants (if known)"},
    {"id": "4.01", "question": "Fires in the past"},
    {"id": "4.02", "question": "Cost of past fire losses"},
    {"id": "5.01", "question": "Detail here if required"},
    {"id": "6.01", "question": "The following fire safety legislation applies to these premises"},
    {"id": "6.02", "question": "The above legislation is enforced by"},
    {"id": "6.03", "question": "Other legislation that makes significant requirements for fire precautions in these premises"},
    {"id": "6.04", "question": "The other legislation referred to above is enforced by"},
    {"id": "6.05", "question": "Is there an alterations notice in force?"},
    {"id": "6.06", "question": "Relevant information and deficiencies observed"},
    {"id": "6.07", "question": "Other information if required"},
    {"id": "6.08", "question": "Risk Likelyhood?"},
    {"id": "6.09", "question": "Risk Severity?"},
    {"id": "6.10", "question": "Risk Rating Score?"},
]





PRIMARY_QUESTIONS = [
    {"id": "0.01", "question": "Responsible person (e.g. employer) or person having control of premises?"},
    {"id": "0.02", "question": "Address of premises?"},
    {"id": "0.03", "question": "Person(s) consulted?"},
    {"id": "0.04", "question": "Assessor?"},
    {"id": "0.05", "question": "Assessors statement?"},
    {"id": "0.06", "question": "Report validated by?"},
    {"id": "0.07", "question": "Date of fire risk assessment?"},
    {"id": "0.08", "question": "Date of previous fire risk assessment?"},
    {"id": "0.09", "question": "Suggested date for review?"},
    {"id": "0.10", "question": "Fire Risk Assessment Review?"},
    {"id": "0.11", "question": "Report compliance?"},
    {"id": "1.01", "question": "Number of floors at ground level and above?"},
    {"id": "1.02", "question": "Number of floors entirely below ground level?"},
    {"id": "1.03", "question": "Floors on which car parking is provided?"},
    {"id": "1.04", "question": "Approximate floor area per floor?"},
    {"id": "1.05", "question": "Approximate floor area gross?"},
    {"id": "1.06", "question": "Approximate floor area on ground floor?"},
    {"id": "1.07", "question": "Details of construction and layout?"},
    {"id": "1.08", "question": "Occupancy?"},
    {"id": "2.01", "question": "Approximate maximum number of employees at any one time?"},
    {"id": "2.02", "question": "Approximate maximum number of other occupants at any one time?"},
    {"id": "2.03", "question": "Approximate total number of people present in the building at any one time?"},
    {"id": "3.01", "question": "Sleeping occupants?"},
    {"id": "3.02", "question": "Disabled employees?"},
    {"id": "3.03", "question": "Other disabled occupants?"},
    {"id": "3.04", "question": "Occupants in remote areas and lone workers?"},
    {"id": "3.05", "question": "Young persons?"},
    {"id": "3.06", "question": "Others?"},
    {"id": "4.01", "question": "Fires in past 10 years?"},
    {"id": "4.02", "question": "Cost of past fire losses?"},
    {"id": "5.01", "question": "Detail if required?"},
    {"id": "6.01", "question": "The following fire safety legislation applies to these premises?"},
    {"id": "6.02", "question": "The above legislation is enforced by?"},
    {"id": "6.03", "question": "Other legislation that makes significant requirements for fire precautions in these premises?"},
    {"id": "6.04", "question": "The other legislation referred to above is enforced by?"},
    {"id": "6.05", "question": "Is there an alterations notice in force?"},
    {"id": "6.06", "question": "Relevant information and deficiencies observed?"},
    {"id": "6.07", "question": "Other information?"},
    {"id": "6.08", "question": "Risk Likelyhood?"},
    {"id": "6.09", "question": "Risk Severity?"},
    {"id": "6.10", "question": "Risk Rating Score?"},

]


# Static Questions
QUESTIONS = [
    {"id": "7.01", "question": "Are reasonable measures taken to prevent fires of electrical origin?"},
    {"id": "7.03", "question": "Are fixed installations periodically inspected and tested?"},
    {"id": "7.04", "question": "Is portable appliance testing carried out?"},
    {"id": "7.05", "question": "Is there suitable control over the use of personal electrical appliances?"},
    {"id": "7.06", "question": "Is there suitable limitation of trailing leads and adapters?"},
    {"id": "8.01", "question": "Are reasonable measures taken to prevent fires as a result of smoking?"},
    {"id": "8.02", "question": "Is smoking prohibited in the building?"},
    {"id": "8.03", "question": "Is smoking prohibited in appropriate areas?"},
    {"id": "8.04", "question": "Are there suitable arrangements for those who wish to smoke?"},
    {"id": "8.05", "question": "Did the smoking policy appear to be observed at the time of inspection?"},
    {"id": "9.01", "question": "Does basic security against arson by outsiders appear reasonable?"},
    {"id": "9.02", "question": "Is there an absence of unnecessary fire load in close proximity to the premises or available for ignition by outsiders?"},
    {"id": "10.01", "question": "Is there satisfactory control over the use of portable heaters?"},
    {"id": "10.02", "question": "Are fixed heating and ventilation installations subject to regular maintenance?"},
    {"id": "11.01", "question": "Are reasonable measures taken to prevent fires as a result of cooking?"},
    {"id": "11.02", "question": "Are filters cleaned or changed and ductwork cleaned regularly?"},
    {"id": "12.01", "question": "Does the building have a lightning protection system?"},
    {"id": "13.01", "question": "Is the overall standard of housekeeping adequate?"},
    {"id": "13.02", "question": "Do combustible materials appear to be separated from ignition sources?"},
    {"id": "13.03", "question": "Is unnecessary accumulation or inappropriate storage of combustible materials or waste avoided?"},
    {"id": "14.01", "question": "Is there satisfactory control over works carried out in the building?"},
    {"id": "14.02", "question": "Are fire safety conditions imposed on outside contractors?"},
    {"id": "14.03", "question": "Is a permit to work system used?"},
    {"id": "14.04", "question": "Are suitable precautions taken by in-house maintenance personnel who carry out works?"},
    {"id": "15.01", "question": "Are the general fire precautions adequate to address the hazards associated with dangerous substances?"},
    {"id": "16.01", "question": "Are there other significant fire hazards that warrant consideration?"},
    {"id": "17.01", "question": "Is the design and maintenance of the means of escape considered adequate?"},
    {"id": "17.02", "question": "Do staircase and exit capacities appear to be adequate for the number of occupants?"},
    {"id": "17.03", "question": "Are there reasonable distances of travel where there is escape in a single direction?"},
    {"id": "17.04", "question": "Are there reasonable distances of travel where there are alternative means of escape?"},
    {"id": "17.05", "question": "Is there adequate provision of exits?"},
    {"id": "17.06", "question": "Do fire exits open in the direction of escape, where necessary?"},
    {"id": "17.07", "question": "Are there satisfactory arrangements for escape where revolving or sliding doors are used as exits?"},
    {"id": "17.08", "question": "Are the arrangements provided for securing exits satisfactory?"},
    {"id": "17.09", "question": "Is a suitable standard of protection designed for escape routes?"},
    {"id": "17.10", "question": "Are there reasonable arrangements for means of escape for disabled people?"},
    {"id": "17.11", "question": "Are the escape routes available for use and suitably maintained?"},
    {"id": "17.12", "question": "Are fire-resisting doors maintained in sound condition and self-closing, where necessary?"},
    {"id": "17.13", "question": "Is the fire-resisting construction protecting escape routes in sound condition?"},
    {"id": "17.14", "question": "Are all escape routes clear of obstructions?"},
    {"id": "17.15", "question": "Are all fire exits easily and immediately openable?"},
    {"id": "18.01", "question": "Is there compartmentation of a reasonable standard?"},
    {"id": "18.02", "question": "Is there reasonable limitation of linings that may promote fire spread?"},
    {"id": "18.03", "question": "Are fire dampers provided to protect critical means of escape?"},
    {"id": "19.01", "question": "Has a reasonable standard of emergency escape lighting system been provided?"},
    {"id": "20.01", "question": "Is there a reasonable standard of fire safety signs and notices?"},
    ]


HOUSING_QUESTIONS = [
    {"id": "7.01", "question": "Are reasonable measures taken to prevent fires of electrical origin?"},
    {"id": "7.02a", "question": "Are fixed installations periodically inspected and tested?"},
    {"id": "7.02b", "question": "Is portable appliance testing carried out?"},
    {"id": "8.01", "question": "Are reasonable measures taken to prevent fires as a result of smoking?"},
    {"id": "8.02a", "question": "Is smoking prohibited in appropriate areas?"},
    {"id": "8.02b", "question": "Are there suitable arrangements for those who wish to smoke?"},
    {"id": "8.02c", "question": "Did the smoking policy appear to be observed at the time of inspection?"},
    {"id": "8.02d", "question": "Are \"No smoking\" signs provided in the common areas?"},
    {"id": "9.01", "question": "Does basic security against arson by outsiders appear reasonable?"},
    {"id": "9.02", "question": "Is there an absence of unnecessary fire load in close proximity to the premises or available for ignition by outsiders?"},
    {"id": "10.01", "question": "Is there satisfactory control over the use of portable heaters?"},
    {"id": "10.02", "question": "Are fixed heating and ventilation installations subject to regular maintenance?"},
    {"id": "11.01", "question": "Are reasonable measures taken to prevent fires as a result of cooking?"},
    {"id": "12.01", "question": "Does the building have a lightning protection system?"},
    {"id": "13.01", "question": "Is the overall standard of housekeeping adequate?"},
    {"id": "13.02a", "question": "Do combustible materials appear to be separated from ignition sources?"},
    {"id": "13.02b", "question": "Is unnecessary accumulation or inappropriate storage of combustible materials or waste?"},
    {"id": "13.02c", "question": "Are gas and electricity intake/meter cupboards adequately secured and kept clear of combustible materials?"},
    {"id": "14.01", "question": "Is there satisfactory control over works carried out in the building?"},
    {"id": "15.01", "question": "Are the general fire precautions adequate to address the hazards associated with dangerous substances used or stored within the premises?"},
    {"id": "16.01", "question": "Hazards"},
    {"id": "17.01", "question": "Is the design and maintenance of the means of escape considered adequate?"},
    {"id": "17.02a", "question": "Are there reasonable distances of travel:"},
    {"id": "17.02a1", "question": "Where there is escape in a single direction?"},
    {"id": "17.02a2", "question": "Where there are alternative means of escape?"},
    {"id": "17.02b", "question": "Is there adequate provision of exits?"},
    {"id": "17.02c", "question": "Do fire exits open in the direction of escape, where necessary?"},
    {"id": "17.02d", "question": "Are the arrangements provided for securing exits satisfactory?"},
    {"id": "17.02e", "question": "Is the fire-resisting construction protecting escape routes and staircases of a suitable standard and maintained in sound condition?"},
    {"id": "17.02f", "question": "Is the fire resistance of doors to staircases and the common areas considered adequate, and are the doors maintained in sound condition?"},
    {"id": "17.02g", "question": "Are suitable self closing devices fitted to fire doors in the common areas?"},
    {"id": "17.02h", "question": "Is the fire resistance of doors to meter cupboards/store rooms/plant rooms in common areas considered adequate, and are they adequately secured and/or fitted with suitable self-closing devices?"},
    {"id": "17.02i", "question": "Is the fire resistance of flat entrance doors considered adequate, and are the doors maintained in sound condition?"},
    {"id": "17.02j", "question": "Are suitable self closing devices fitted to flat entrance fire doors and, where fitted, maintained in good working order?"},
    {"id": "17.02k", "question": "Are there adequate smoke control provisions to protect the common escape routes, where necessary?"},
    {"id": "17.02l", "question": "Are all escape routes clear of obstructions?"},
    {"id": "17.02m", "question": "Are all fire exits easily and immediately openable?"},
    {"id": "17.02n", "question": "Are there reasonable arrangements for means of escape for disabled people?"},
    {"id": "18.01a", "question": "Adequate levels of compartmentation between floors and between flats and the common escape routes?"},
    {"id": "18.01b", "question": "Reasonable limitation of linings that may promote fire spread?"},
    {"id": "18.01c", "question": "As far as can be reasonably be ascertained, reasonable fire separation within any roof space?"},
    {"id": "18.01d", "question": "Adequately fire protected service risers and/or ducts in common areas, that will restrict the spread of fire and smoke?"},
    {"id": "18.02", "question": "As far as can be reasonably be ascertained, are fire dampers provided necessary to protect critical means of escape against passage of fire, smoke and products of combustion in the early stages of a fire?"},
    {"id": "19.01", "question": "Has a reasonable standard of emergency escape lighting system been provided?"},
    {"id": "20.01", "question": "Is there a reasonable standard of fire safety signs and notices?"},
    {"id": "21.01", "question": "Is a reasonable fire detection and fire alarm system provided in common areas, where necessary?"},
    {"id": "21.02", "question": "If there is a communal fire detection and fire alarm system, does it extend into the dwellings?"},
    {"id": "21.03", "question": "Where appropriate, has a fire alarm zone plan been provided?"},
    {"id": "21.04", "question": "Where appropriate, are there adequate arrangements for silencing and resetting an alarm condition?"},
    {"id": "22.01", "question": "Is there reasonable provision of manual fire extinguishing appliances?"},
    {"id": "22.02", "question": "Are all fire extinguishing appliances readily accessible?"},
    {"id": "23.01a", "question": "Sprinkler system?"},
    {"id": "23.01b", "question": "Misting system?"},
    {"id": "24.01", "question": "Type of other fixed system(s) installed"},
    {"id": "24.02", "question": "Are there appropriately sited facilities for electrical isolation of any photovoltaic (PV) cells, with appropriate signage, to assist the fire and rescue service?"},
    {"id": "25.01", "question": "Safety assistance"},
    {"id": "25.02", "question": "Fire safety at the premises is managed by"},
    {"id": "25.03", "question": "Is there a suitable record of the fire safety arrangements?"},
    {"id": "25.04", "question": "Evacuation strategy"},
    {"id": "25.05", "question": "Are procedures in the event of a fire appropriate and properly documented, where appropriate?"},
    {"id": "25.06", "question": "Are routine in-house inspections of fire precautions undertaken?"},
    {"id": "26.01", "question": "Are all staff given adequate fire safety instruction and training on induction?"},
    {"id": "26.02", "question": "When the employees of another employer work in the premises, is appropriate information on the fire risks and fire safety measures provided?"},
    {"id": "27.01", "question": "Is there adequate maintenance of the premises?"},
    {"id": "27.02", "question": "Is weekly testing and periodic servicing of fire detection and alarm system undertaken?"},
    {"id": "27.03", "question": "Is monthly and annual testing routines for emergency lighting?"},
    {"id": "27.04", "question": "Is annual maintenance of fire extinguishing appliances undertaken?"},
    {"id": "27.05", "question": "Are six-monthly inspection and annual testing of rising mains undertaken?"},
    {"id": "27.06", "question": "Are weekly and monthly testing, six monthly inspection and annual testing of fire-fighting lift(s) provided?"},
    {"id": "27.07", "question": "Other relevant inspections or tests"},
    {"id": "28.01a", "question": "Fire alarm tests (where relevant)?"},
    {"id": "28.01b", "question": "Emergency escape lighting tests?"},
    {"id": "28.01c", "question": "Maintenance and testing of other fire protection equipment?"},
    {"id": "29.09", "question": "Is the fire emergency plan available to the enforcing authority?"},
    {"id": "29.10", "question": "Are Personal Emergency Evacuation Plans (PEEPS) required and in place?"},
    {"id": "29.01", "question": "Is there a suitably located premises information box for the fire and rescue service?"},
    {"id": "29.02", "question": "Are there arrangements to keep the premises information box up to date?"},
    {"id": "30.01", "question": "Has information on fire procedures been disseminated to residents?"},
    {"id": "30.02", "question": "Is fire safety information disseminated to residents?"}
]




# Database Models
class Form(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    form_id = db.Column(db.String(50), unique=True, nullable=False)
    form_type = db.Column(db.String(20), nullable=False)  # new column to store form type
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    property_name = db.Column(db.String(100), nullable=True)

class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    form_id = db.Column(db.String(50), db.ForeignKey('form.form_id'), nullable=False)
    question_id = db.Column(db.String(10), nullable=False)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.String(10), nullable=False)  # Yes, No, N/A
    control_measures = db.Column(db.Text, nullable=True)


class PrimaryAnswer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    form_id = db.Column(db.String(50), db.ForeignKey('form.form_id'), nullable=False)
    question_id = db.Column(db.String(10), nullable=False)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)  

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)  # Store hashed password








import secrets
from flask import session

app.secret_key = secrets.token_hex(32)  # Set a secret key for session management

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            # Save user info in session
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('index'))
        else:
            return "Invalid username or password", 400

    return render_template('login.html')


from functools import wraps
from flask import session, redirect, url_for

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function



@app.route('/logout')
@login_required
def logout():
    session.clear()  # Clear the session
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
@login_required
def register():

       # Check if current logged-in user is admin
    if session.get('username') != 'admin':
       return "Registration is only allowed for admin user", 403

    # Count existing users
    total_users = User.query.count()
    
    # Maximum users allowed
    MAX_USERS = 5
    
    if total_users >= MAX_USERS:
        return "Maximum number of users already registered. Contact administrator.", 403


    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        admin_username = 'admin'  # Set your predefined admin username
        

        
        # Generate the hashed password
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        
        # Check if admin user already exists
        existing_admin = User.query.filter_by(username=username).first()
        if existing_admin:
            return "Admin user already exists", 400
        
        # Add the user to the database
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        
        return redirect(url_for('login'))
    
    return render_template('register.html')





@app.route('/')
@login_required
def index():
    forms = Form.query.all()
    return render_template('index.html', forms=forms)


@app.route('/form/new', methods=['GET', 'POST'])
@login_required
def create_form():
    if request.method == 'POST':
        form_id = request.form['form_id']
        form_type = request.form['form_type']
        property_name = request.form.get('property_name', '')  # Get property name, default to empty string

        # Create a new form with the selected form_type and property_name
        new_form = Form(
            form_id=form_id, 
            form_type=form_type, 
            property_name=property_name
        )
        db.session.add(new_form)
        db.session.commit()

        return redirect(url_for('fill_form', form_id=form_id))

    # Fetch the last form ID from the database to increment it
    last_form = Form.query.order_by(Form.id.desc()).first()
    if last_form:
        # Extract the numeric part of the form_id and increment it
        # Assuming form_id is numeric; adjust based on your format
        new_form_id = str(int(last_form.form_id) + 1)
    else:
        new_form_id = '1'  # If no forms exist, start with form_id '1'

    return render_template('create_form.html', new_form_id=new_form_id)




@app.route('/form/<form_id>', methods=['GET', 'POST'])
@login_required
def fill_form(form_id):
    form = Form.query.filter_by(form_id=form_id).first()
    if not form:
        return "Form not found", 404

    # Select question sets based on form type
    if form.form_type == 'housing':
        primary_questions = PRIMARY_HOUSING_QUESTIONS
        questions = HOUSING_QUESTIONS
    else:
        primary_questions = PRIMARY_QUESTIONS
        questions = QUESTIONS

    if request.method == 'POST':
        # Save responses to primary questions
        for question in primary_questions:
            answer = request.form.get(f"primary-answer-{question['id']}")
            new_primary_answer = PrimaryAnswer(
                form_id=form_id,
                question_id=question["id"],
                question=question["question"],
                answer=answer
            )
            db.session.add(new_primary_answer)

        # Save responses to main questions
        for question in questions:
            answer = request.form.get(f"answer-{question['id']}")
            control_measures = request.form.get(f"control-measures-{question['id']}")
            new_answer = Answer(
                form_id=form_id,
                question_id=question["id"],
                question=question["question"],
                answer=answer,
                control_measures=control_measures if answer == "No" else None,
            )
            db.session.add(new_answer)

        # Handle file uploads
        upload_folder = os.path.join("uploads", form_id)
        os.makedirs(upload_folder, exist_ok=True)

        # Regular images
        for file in request.files.getlist('images'):
            if file:
                filename = secure_filename(file.filename)
                file.save(os.path.join(upload_folder, filename))



        # Building cover image
        building_cover_image = request.files.get('building_cover_image')
        if building_cover_image and building_cover_image.filename:
            # Create a cover_image subfolder
            cover_image_folder = os.path.join(upload_folder, "cover_image")
            os.makedirs(cover_image_folder, exist_ok=True)
            
            filename = f"building_cover_image_{form_id}{os.path.splitext(secure_filename(building_cover_image.filename))[1]}"
            building_cover_image.save(os.path.join(cover_image_folder, filename))



        db.session.commit()
        return redirect(url_for('view_form', form_id=form_id))

    return render_template(
        'fill_form.html',
        form_id=form_id,
        form_type=form.form_type,
        primary_questions=primary_questions,
        questions=questions
    )

@app.route('/uploads/<path:filename>')
def download_file(filename):
    # Define the base path for your uploads directory
    uploads_dir = 'uploads'  # Change this to the absolute path if necessary
    return send_from_directory(uploads_dir, filename)


@app.route('/form/<form_id>/view')
@login_required
def view_form(form_id):
    primary_answers = PrimaryAnswer.query.filter_by(form_id=form_id).all()
    answers = Answer.query.filter_by(form_id=form_id).all()

    # Base path for the images folder
    image_folder = os.path.join('uploads', form_id)
    cover_image_folder = os.path.join('uploads', form_id, 'cover_image')

    # Ensure forward slashes in file paths
    image_folder = image_folder.replace(os.sep, '/')
    cover_image_folder = cover_image_folder.replace(os.sep, '/')

    # Get all image file paths for uploaded images
    uploaded_images = [
        os.path.join(form_id, file).replace(os.sep, '/')  # Use forward slashes
        for file in os.listdir(image_folder)
        if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))
    ]

    # Get the cover image
    cover_image = None
    if os.path.exists(cover_image_folder):
        cover_image_files = [
            file for file in os.listdir(cover_image_folder)
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))
        ]
        if cover_image_files:
            cover_image = os.path.join(form_id, 'cover_image', cover_image_files[0]).replace(os.sep, '/')

    return render_template(
        'view_form.html', 
        form_id=form_id, 
        primary_answers=primary_answers, 
        answers=answers, 
        current_date=datetime.now().strftime("%Y-%m-%d"),
        uploaded_images=uploaded_images,  # Pass the list of image paths
        cover_image=cover_image         # Pass the cover image path
    )

@app.route('/form/<form_id>/download', methods=['GET'])
@login_required
def download_form(form_id):
    # Fetch PrimaryAnswer and Answer data
    primary_answers = PrimaryAnswer.query.filter_by(form_id=form_id).all()
    answers = Answer.query.filter_by(form_id=form_id).all()

    # Fetch specific PrimaryAnswer values for question IDs 6.08, 6.09, and 6.10
    specific_primary_answers = PrimaryAnswer.query.filter(
        PrimaryAnswer.form_id == form_id,
        PrimaryAnswer.question_id.in_(["6.08", "6.09", "6.10"])
    ).all()

    # Create a dictionary for quick access
    specific_values_dict = {answer.question_id: answer.answer for answer in specific_primary_answers}

    # Convert the answers into a numeric array
    numeric_array = [
        specific_values_dict.get("6.08", 0),  # Default to 0 if missing
        specific_values_dict.get("6.09", 0),
        specific_values_dict.get("6.10", 0)
    ]

    # Call your custom function
    fill_blanks_with_coordinates(form_id, numeric_array)

    # Images section generation
    reference_images_to_pdf(form_id)
    
    form = Form.query.filter_by(form_id=form_id).first()
    property_name = form.property_name if form else "Sample Building Name"

    cover_pdf_path = generate_cover_pdf(form_id,property_name)


    answer_data = get_answer_by_form_id(form_id)
    if answer_data:
        second_page_path = generate_second_page_with_info(
            answer_data["address"],                # Address
            answer_data["assessment_date"],        # Assessment Date
            answer_data["next_assessment_date"],   # Next Assessment Date
            answer_data["assessor"],               # Assessor
            answer_data["responsible_person"],     # Responsible person
            form_id                                # Form ID
        )
    else:
        print(f"No answers found for form_id: {form_id}")

    
    # Ensure data exists
    if not primary_answers and not answers:
        return "No data found for this form.", 404

    # Generate HTML content
    html_content = render_template(
        'form_download.html',
        form_id=form_id,
        primary_answers=primary_answers,
        answers=answers,
        current_date=datetime.now().strftime("%Y-%m-%d")
    )

    # Define paths for the PDFs
    generated_pdf_filename = f"{form_id}_generated.pdf"
    merged_pdf_filename = f"{form_id}_merged.pdf"
    final_pdf_filename = f"{form_id}_final.pdf"
    generated_pdf_path = os.path.join("downloads", generated_pdf_filename)
    merged_pdf_path = os.path.join("downloads", merged_pdf_filename)
    final_pdf_path = os.path.join("downloads", final_pdf_filename)
    os.makedirs("downloads", exist_ok=True)

    # Convert HTML to PDF
    pdfkit.from_string(html_content, generated_pdf_path)

    # Path to the additional PDFs
    cover_page_path = "cover_page.pdf"  # Ensure this file exists in your project directory
    risk_assessment_matrix_path = f"risk_assestment_matrix_output{form_id}.pdf"  # Ensure this file exists in your project directory
    reference_pictures_path = f"downloads/reference_pictures_{form_id}.pdf"  # Path to the reference pictures PDF

    # Merge the PDFs
    merger = PdfMerger()
    
    # Check and append the cover page first
    if os.path.exists(cover_page_path):
        merger.append(cover_page_path)
       
    # Append the second_page_path after the cover page
    if os.path.exists(second_page_path):
        merger.append(second_page_path)
    # Append the cover_pdf_path after the cover page
    if os.path.exists(cover_pdf_path):
        merger.append(cover_pdf_path)
    
    # Append the generated PDF
    if os.path.exists(generated_pdf_path):
        merger.append(generated_pdf_path)
    
    # Append the risk assessment matrix if it exists
    if os.path.exists(risk_assessment_matrix_path):
        merger.append(risk_assessment_matrix_path)
    
    # Append reference pictures if they exist
    if os.path.exists(reference_pictures_path):
        merger.append(reference_pictures_path)
    
    # Write the final merged PDF
    merger.write(final_pdf_path)
    merger.close()


    # Serve the final merged PDF file
    return send_file(final_pdf_path, as_attachment=True)




@app.route('/form/<form_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_form(form_id):
    # Validate form existence
    form = Form.query.filter_by(form_id=form_id).first()
    if not form:
        return "Form not found", 404

    # Determine question sets based on form type
    if form.form_type == 'housing':
        primary_questions = PRIMARY_HOUSING_QUESTIONS
        additional_questions = HOUSING_QUESTIONS
    else:
        primary_questions = PRIMARY_QUESTIONS
        additional_questions = QUESTIONS

    # Fetch existing answers
    primary_answers = {pa.question_id: pa for pa in PrimaryAnswer.query.filter_by(form_id=form_id).all()}
    existing_answers = {a.question_id: a for a in Answer.query.filter_by(form_id=form_id).all()}

    # Image folder paths
    upload_folder = os.path.join("uploads", form_id)
    cover_image_folder = os.path.join(upload_folder, "cover_image")

    # Prepare image collections
    existing_images = []
    existing_cover_image = None

    # Collect existing regular images
    if os.path.exists(upload_folder):
        existing_images = [
            file for file in os.listdir(upload_folder)
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')) 
            and file != 'cover_image'
        ]

    # Collect existing cover image
    if os.path.exists(cover_image_folder):
        cover_image_files = [
            file for file in os.listdir(cover_image_folder)
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))
        ]
        if cover_image_files:
            existing_cover_image = cover_image_files[0]

    # Handle form submission
    if request.method == 'POST':
        # Create upload directories if they don't exist
        os.makedirs(upload_folder, exist_ok=True)
        os.makedirs(cover_image_folder, exist_ok=True)

        # Process primary question answers
        for question in primary_questions:
            answer = request.form.get(f"primary-answer-{question['id']}")
            
            if question['id'] in primary_answers:
                # Update existing primary answer
                primary_answers[question['id']].answer = answer or ''
            else:
                # Create new primary answer if not exists
                new_primary_answer = PrimaryAnswer(
                    form_id=form_id,
                    question_id=question['id'],
                    question=question['question'],
                    answer=answer or ''
                )
                db.session.add(new_primary_answer)

        # Process additional questions answers
        for question in additional_questions:
            answer = request.form.get(f"answer-{question['id']}")
            control_measures = request.form.get(f"control-measures-{question['id']}")

            if question['id'] in existing_answers:
                # Update existing answer
                existing_answers[question['id']].answer = answer or ''
                existing_answers[question['id']].control_measures = control_measures if answer == "No" else None
            else:
                # Create new answer if not exists
                new_answer = Answer(
                    form_id=form_id,
                    question_id=question['id'],
                    question=question['question'],
                    answer=answer or '',
                    control_measures=control_measures if answer == "No" else None
                )
                db.session.add(new_answer)

        # Handle image deletions
        deleted_images = request.form.getlist('delete_images')
        for image in deleted_images:
            image_path = os.path.join(upload_folder, image)
            if os.path.exists(image_path):
                os.remove(image_path)

        # Handle cover image deletion
        if request.form.get('delete_cover_image') and existing_cover_image:
            cover_image_path = os.path.join(cover_image_folder, existing_cover_image)
            if os.path.exists(cover_image_path):
                os.remove(cover_image_path)

        # Process new image uploads
        for file in request.files.getlist('images'):
            if file and file.filename:
                filename = secure_filename(file.filename)
                file.save(os.path.join(upload_folder, filename))

        # Process new cover image upload
        building_cover_image = request.files.get('building_cover_image')
        if building_cover_image and building_cover_image.filename:
            filename = f"building_cover_image_{form_id}{os.path.splitext(secure_filename(building_cover_image.filename))[1]}"
            building_cover_image.save(os.path.join(cover_image_folder, filename))

        # Commit all changes
        db.session.commit()

        # Redirect to view form after successful update
        return redirect(url_for('view_form', form_id=form_id))

    # Render edit form template
    return render_template(
        'edit_form.html',
        form_id=form_id,
        primary_questions=primary_questions,
        primary_answers=primary_answers,
        questions=additional_questions,
        answers=existing_answers,
        existing_images=existing_images,
        existing_cover_image=existing_cover_image
    )



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)

