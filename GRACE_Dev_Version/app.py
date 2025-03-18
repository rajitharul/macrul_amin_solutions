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
from flask import flash
import os
import shutil
from datetime import datetime

from sqlalchemy.orm import aliased
from PIL import Image, ImageDraw, ImageFont
import platform
import os
import fitz  # PyMuPDF
import signal
from questions import QUESTIONS,PRIMARY_QUESTIONS,PRIMARY_HOUSING_QUESTIONS,HOUSING_QUESTIONS
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///forms.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# The secret key you'll compare with incoming requests
SERVER_SECRET_KEY = "adminmacrul"

@app.route("/shutdown", methods=["POST"])
def shutdown_endpoint():
    """
    A shutdown endpoint. Expects JSON in the form:
    {
        "secret_key": "..."
    }
    """
    data = request.get_json(silent=True)
    if not data or 'secret_key' not in data:
        return jsonify({"error": "No secret key provided"}), 400

    # Compare the received key to the server's key
    if data["secret_key"] != SERVER_SECRET_KEY:
        return jsonify({"error": "Invalid secret key"}), 401

    # If valid, shut down the server
    os.kill(os.getpid(), signal.SIGTERM)  # More reliable method
    return jsonify({"message": "Server is shutting down..."}), 200



def fill_blanks_with_coordinates(form_id,fill_values):
    input_pdf = "risk_assestment_matrix.pdf"
    coordinates = [
    (109, 415),  # x=100, y=200
    (251, 415),  # x=200, y=200
    (352, 415),  # x=300, y=200
    ]

    output_pdf_path = f"downloads/risk_assestment_matrix_output{form_id}.pdf"
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
            page.insert_text((x, y), text, fontsize=10, color=(0, 0, 0))

    # Save the modified PDF
    pdf_document.save(output_pdf_path)
    pdf_document.close()



def get_answer_by_form_id(form_id):
    # Query each question separately by form_id and question_id
    address = db.session.query(PrimaryAnswer.answer).filter_by(form_id=form_id, question_id="0.02").first()
    assessment_date = db.session.query(PrimaryAnswer.answer).filter_by(form_id=form_id, question_id="0.07").first()
    next_assessment_date = db.session.query(PrimaryAnswer.answer).filter_by(form_id=form_id, question_id="0.09").first()
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
    responsible_person = db.Column(db.String(100), nullable=True)  # New column
    target_date = db.Column(db.Date, nullable=True)  # New column for date


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


@app.route('/form/<form_id>/delete', methods=['POST'])
@login_required
def delete_form(form_id):
    try:
        # Delete associated records from Answer table
        Answer.query.filter_by(form_id=form_id).delete()
        
        # Delete associated records from PrimaryAnswer table
        PrimaryAnswer.query.filter_by(form_id=form_id).delete()
        
        # Delete the Form record
        form = Form.query.filter_by(form_id=form_id).first()
        if form:
            db.session.delete(form)
        
        # Commit database changes
        db.session.commit()
        
        # Define all directories to check
        downloads_dir = 'downloads'
        property_cover_dir = os.path.join('downloads', 'property_cover_page')
        second_page_dir = os.path.join('downloads', 'second_page')
        uploads_dir = os.path.join('uploads', form_id)
        
        # Function to safely delete files containing form_id in their name
        def delete_matching_files(directory):
            if os.path.exists(directory) and os.path.isdir(directory):
                for filename in os.listdir(directory):
                    if form_id in filename:
                        file_path = os.path.join(directory, filename)
                        if os.path.exists(file_path) and os.path.isfile(file_path):
                            try:
                                os.remove(file_path)
                                print(f"Deleted file: {file_path}")
                            except Exception as e:
                                print(f"Error deleting file {file_path}: {e}")
        
        # Delete files from main downloads directory
        delete_matching_files(downloads_dir)
        
        # Delete files from property_cover_page directory
        delete_matching_files(property_cover_dir)
        
        # Delete files from second_page directory
        delete_matching_files(second_page_dir)
        
        # Delete the entire uploads folder for this form
        if os.path.exists(uploads_dir) and os.path.isdir(uploads_dir):
            try:
                shutil.rmtree(uploads_dir)
                print(f"Deleted directory: {uploads_dir}")
            except Exception as e:
                print(f"Error deleting uploads folder {uploads_dir}: {e}")
        
        flash('Form and all associated files deleted successfully', 'success')
        return redirect(url_for('index'))
    
    except Exception as e:
        db.session.rollback()
        print(f"Error during form deletion: {str(e)}")
        flash(f'Error deleting form: {str(e)}', 'error')
        return redirect(url_for('index'))
    


@app.route('/form/new', methods=['GET', 'POST'])
@login_required
def create_form():
    # First, check how many forms currently exist
    forms_count = Form.query.count()
    if forms_count >= 10:
        flash("You have reached the maximum of 10 forms. Please delete an existing form before creating a new one.", "error")
        return redirect(url_for('home'))  # or wherever you list all forms

    if request.method == 'POST':
        form_id = request.form['form_id']
        form_type = request.form['form_type']
        property_name = request.form.get('property_name', '')

        new_form = Form(
            form_id=form_id,
            form_type=form_type,
            property_name=property_name
        )
        db.session.add(new_form)
        db.session.commit()

        return redirect(url_for('fill_form', form_id=form_id))

    # If GET request, generate the next form_id
    last_form = Form.query.order_by(Form.id.desc()).first()
    if last_form:
        new_form_id = str(int(last_form.form_id) + 1)
    else:
        new_form_id = '1'

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
            responsible_person = request.form.get(f"responsible_person-{question['id']}")
            target_date_str = request.form.get(f"target_date-{question['id']}")  # Get target date as string

            # ✅ Convert string to Python date object (if not empty)
            target_date = None
            if target_date_str:
                try:
                    target_date = datetime.strptime(target_date_str, "%Y-%m-%d").date()
                except ValueError:
                    flash(f"Invalid date format for question {question['id']}. Please use YYYY-MM-DD.", "error")
                    return redirect(url_for('fill_form', form_id=form_id))


            new_answer = Answer(
                form_id=form_id,
                question_id=question["id"],
                question=question["question"],
                answer=answer,
                control_measures=control_measures if answer == "No" else None,
                responsible_person=responsible_person if answer == "No" else None,
                target_date=target_date if answer == "No" else None
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
        
    form = Form.query.filter_by(form_id=form_id).first()
    if not form:
        return "Form not found", 404

    # Determine question sets based on form type
    if form.form_type == 'housing':
        cover_page_path = "cover_page_housing.pdf"
    else:
        cover_page_path = "cover_page_non_housing.pdf"

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


        # Generate HTML content
    html_content_action_plan = render_template(
        'form_download_action_plan.html',
        form_id=form_id,
        primary_answers=primary_answers,
        answers=answers,
        current_date=datetime.now().strftime("%Y-%m-%d")
    )


    # Define paths for the PDFs
    generated_pdf_filename = f"{form_id}_generated.pdf"
    generated_actiona_plan_pdf_filename = f"{form_id}_generated_action_plan.pdf"

    merged_pdf_filename = f"{form_id}_merged.pdf"
    final_pdf_filename = f"{form_id}_final.pdf"
    generated_pdf_path = os.path.join("downloads", generated_pdf_filename)
    generated_action_plan_pdf_path = os.path.join("downloads", generated_actiona_plan_pdf_filename)

    merged_pdf_path = os.path.join("downloads", merged_pdf_filename)
    final_pdf_path = os.path.join("downloads", final_pdf_filename)
    os.makedirs("downloads", exist_ok=True)

    # Convert HTML to PDF
    pdfkit.from_string(html_content, generated_pdf_path)

    # Convert HTML to PDF
    pdfkit.from_string(html_content_action_plan, generated_action_plan_pdf_path)


    # Path to the additional PDFs
    
    risk_assessment_matrix_path = f"downloads/risk_assestment_matrix_output{form_id}.pdf"  # Ensure this file exists in your project directory
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
    
    # Append the generated PDF
    if os.path.exists(generated_action_plan_pdf_path):
        merger.append(generated_action_plan_pdf_path)


    # Append reference pictures if they exist
    if os.path.exists(reference_pictures_path):
        merger.append(reference_pictures_path)
    

    # Append final_attatchment.pdf.pdf
    if os.path.exists("final_attatchment.pdf"):
        merger.append("final_attatchment.pdf")


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
        # Update property name
        form.property_name = request.form.get('property_name', '')

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

        # Process additional question answers
        for question in additional_questions:
            answer = request.form.get(f"answer-{question['id']}")
            control_measures = request.form.get(f"control-measures-{question['id']}")
            responsible_person = request.form.get(f"responsible_person-{question['id']}")
            target_date_str = request.form.get(f"target_date-{question['id']}")

            # Convert target_date string to date object (if not empty)
            target_date = None
            if target_date_str:
                try:
                    target_date = datetime.strptime(target_date_str, "%Y-%m-%d").date()
                except ValueError:
                    flash(f"Invalid date format for question {question['id']}. Use YYYY-MM-DD.", "error")
                    return redirect(url_for('edit_form', form_id=form_id))

            if question['id'] in existing_answers:
                # Update existing answer
                existing_answers[question['id']].answer = answer or ''
                existing_answers[question['id']].control_measures = control_measures if answer == "No" else None
                existing_answers[question['id']].responsible_person = responsible_person if answer == "No" else None
                existing_answers[question['id']].target_date = target_date if answer == "No" else None
            else:
                # Create new answer if not exists
                new_answer = Answer(
                    form_id=form_id,
                    question_id=question['id'],
                    question=question['question'],
                    answer=answer or '',
                    control_measures=control_measures if answer == "No" else None,
                    responsible_person=responsible_person if answer == "No" else None,
                    target_date=target_date if answer == "No" else None
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
        form=form,  # Add the form object to the context
        primary_questions=primary_questions,
        primary_answers=primary_answers,
        questions=additional_questions,
        answers=existing_answers,
        existing_images=existing_images,
        existing_cover_image=existing_cover_image
    )

@app.route('/form/<form_id>/duplicate')
@login_required
def duplicate_form(form_id):
    try:
        # Get the original form
        original_form = Form.query.filter_by(form_id=form_id).first()
        if not original_form:
            flash('Original form not found', 'error')
            return redirect(url_for('index'))

        # Check if we've reached the maximum number of forms
        forms_count = Form.query.count()
        if forms_count >= 10:
            flash("You have reached the maximum of 10 forms. Please delete an existing form before creating a new one.", "error")
            return redirect(url_for('index'))

        # Generate new form ID
        last_form = Form.query.order_by(Form.id.desc()).first()
        new_form_id = str(int(last_form.form_id) + 1)

        # Create new form
        new_form = Form(
            form_id=new_form_id,
            form_type=original_form.form_type,
            property_name=f"{original_form.property_name} (Copy)" if original_form.property_name else None
        )
        db.session.add(new_form)

        # Copy PrimaryAnswers
        primary_answers = PrimaryAnswer.query.filter_by(form_id=form_id).all()
        for pa in primary_answers:
            new_pa = PrimaryAnswer(
                form_id=new_form_id,
                question_id=pa.question_id,
                question=pa.question,
                answer=pa.answer
            )
            db.session.add(new_pa)

        # Copy Answers
        answers = Answer.query.filter_by(form_id=form_id).all()
        for ans in answers:
            new_ans = Answer(
                form_id=new_form_id,
                question_id=ans.question_id,
                question=ans.question,
                answer=ans.answer,
                control_measures=ans.control_measures,
                responsible_person=ans.responsible_person,
                target_date=ans.target_date
            )
            db.session.add(new_ans)

        # Create new empty folders for the duplicated form
        new_upload_dir = os.path.join("uploads", new_form_id)
        new_cover_image_dir = os.path.join(new_upload_dir, "cover_image")
        
        # Create the directories
        os.makedirs(new_upload_dir, exist_ok=True)
        os.makedirs(new_cover_image_dir, exist_ok=True)

        # Commit all changes
        db.session.commit()
        flash('Form duplicated successfully', 'success')
        return redirect(url_for('index'))

    except Exception as e:
        db.session.rollback()
        flash(f'Error duplicating form: {str(e)}', 'error')
        return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)

