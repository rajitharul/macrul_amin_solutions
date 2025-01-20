from flask import Flask, request, render_template, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request, render_template, redirect, url_for, send_file
import os
import pdfkit
import pdfkit
from PyPDF2 import PdfMerger
from datetime import datetime
from werkzeug.utils import secure_filename
from utils import reference_images_to_pdf
from werkzeug.security import generate_password_hash, check_password_hash

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
# Database Models
class Form(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    form_id = db.Column(db.String(50), unique=True, nullable=False)
    form_type = db.Column(db.String(20), nullable=False)  # new column to store form type


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




# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
        
#         # Generate the hashed password
#         hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        
#         # Add the user to the database
#         new_user = User(username=username, password=hashed_password)
#         db.session.add(new_user)
#         db.session.commit()
        
#         return redirect(url_for('login'))
    
#     return render_template('register.html')



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
        form_type = request.form['form_type']  # Get the form type from the form

        # Create a new form with the selected form_type
        new_form = Form(form_id=form_id, form_type=form_type)
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

    if request.method == 'POST':
        # Save responses to PRIMARY_QUESTIONS
        for question in PRIMARY_QUESTIONS:
            answer = request.form.get(f"primary-answer-{question['id']}")
            new_primary_answer = PrimaryAnswer(
                form_id=form_id,
                question_id=question["id"],
                question=question["question"],
                answer=answer
            )
            db.session.add(new_primary_answer)

        # Save responses to QUESTIONS
        for question in QUESTIONS:
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
        for file in request.files.getlist('images'):
            if file:
                filename = secure_filename(file.filename)
                file.save(os.path.join(upload_folder, filename))

        db.session.commit()
        return redirect(url_for('view_form', form_id=form_id))

    return render_template(
        'fill_form.html',
        form_id=form_id,
        form_type=form.form_type,
        primary_questions=PRIMARY_QUESTIONS,
        questions=QUESTIONS
    )





@app.route('/form/<form_id>/view')
@login_required
def view_form(form_id):
    primary_answers = PrimaryAnswer.query.filter_by(form_id=form_id).all()
    answers = Answer.query.filter_by(form_id=form_id).all()
    return render_template(
        'view_form.html', 
        form_id=form_id, 
        primary_answers=primary_answers, 
        answers=answers, 
        current_date=datetime.now().strftime("%Y-%m-%d")
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
    if os.path.exists(cover_page_path):
        merger.append(cover_page_path)
    merger.append(generated_pdf_path)
    if os.path.exists(risk_assessment_matrix_path):
        merger.append(risk_assessment_matrix_path)
    if os.path.exists(reference_pictures_path):
        merger.append(reference_pictures_path)
    merger.write(final_pdf_path)
    merger.close()

    # Serve the final merged PDF file
    return send_file(final_pdf_path, as_attachment=True)




@app.route('/form/<form_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_form(form_id):
    form = Form.query.filter_by(form_id=form_id).first()
    if not form:
        return "Form not found", 404

    # Fetch existing answers
    primary_answers = {pa.question_id: pa for pa in PrimaryAnswer.query.filter_by(form_id=form_id).all()}
    answers = {a.question_id: a for a in Answer.query.filter_by(form_id=form_id).all()}

    if request.method == 'POST':
        # Update PrimaryAnswers
        for question in PRIMARY_QUESTIONS:
            answer = request.form.get(f"primary-answer-{question['id']}")
            if question['id'] in primary_answers:
                primary_answers[question['id']].answer = answer
            else:
                new_primary_answer = PrimaryAnswer(
                    form_id=form_id,
                    question_id=question['id'],
                    question=question['question'],
                    answer=answer
                )
                db.session.add(new_primary_answer)

        # Update Answers
        for question in QUESTIONS:
            answer = request.form.get(f"answer-{question['id']}")
            control_measures = request.form.get(f"control-measures-{question['id']}")
            if question['id'] in answers:
                answers[question['id']].answer = answer
                answers[question['id']].control_measures = control_measures if answer == "No" else None
            else:
                new_answer = Answer(
                    form_id=form_id,
                    question_id=question['id'],
                    question=question['question'],
                    answer=answer,
                    control_measures=control_measures if answer == "No" else None,
                )
                db.session.add(new_answer)

        db.session.commit()
        return redirect(url_for('view_form', form_id=form_id))

    return render_template(
        'edit_form.html',
        form_id=form_id,
        primary_questions=PRIMARY_QUESTIONS,
        primary_answers=primary_answers,
        questions=QUESTIONS,
        answers=answers
    )



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)

