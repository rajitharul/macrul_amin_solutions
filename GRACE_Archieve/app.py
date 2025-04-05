from flask import Flask, render_template, request, send_file, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import pdfkit

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///forms.db'  # Database location
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class FormData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    floors_above_ground = db.Column(db.String(100))
    floors_below_ground = db.Column(db.String(100))
    car_parking_floors = db.Column(db.String(100))
    floor_area_per_floor = db.Column(db.String(100))
    total_floor_area = db.Column(db.String(100))
    ground_floor_area = db.Column(db.String(100))
    construction_details = db.Column(db.String(500))
    occupancy = db.Column(db.String(100))
    max_employees = db.Column(db.String(100))
    max_other_occupants = db.Column(db.String(100))
    total_people_present = db.Column(db.String(100))
    sleeping_occupants = db.Column(db.String(100))
    disabled_employees = db.Column(db.String(100))
    disabled_occupants = db.Column(db.String(100))
    remote_occupants = db.Column(db.String(100))
    young_persons = db.Column(db.String(100))
    specific_groups = db.Column(db.String(500))
    past_fires = db.Column(db.String(100))
    fire_loss_cost = db.Column(db.String(100))
    additional_details = db.Column(db.String(500))
    fire_legislation = db.Column(db.String(500))
    enforced_by = db.Column(db.String(100))
    other_legislation = db.Column(db.String(500))
    
    # New fields for fire safety measures
    electrical_origin = db.Column(db.String(50))
    fixed_inspection = db.Column(db.String(50))
    appliance_testing = db.Column(db.String(50))
    personal_appliances = db.Column(db.String(50))
    trailing_leads = db.Column(db.String(50))
    observations_7_02 = db.Column(db.String(500))
    smoking = db.Column(db.String(50))
    smoking_prohibited = db.Column(db.String(50))
    smoking_area = db.Column(db.String(50))
    observations_8_02 = db.Column(db.String(500))

# Route for the home page (Form)
@app.route('/new_form')
def index():
    return render_template('form.html')

@app.route('/submit', methods=['POST'])
def submit():
    # Collecting data from the form
    data = {
        "floors_above_ground": request.form.get("floors_above_ground"),
        "floors_below_ground": request.form.get("floors_below_ground"),
        "car_parking_floors": request.form.get("car_parking_floors"),
        "floor_area_per_floor": request.form.get("floor_area_per_floor"),
        "total_floor_area": request.form.get("total_floor_area"),
        "ground_floor_area": request.form.get("ground_floor_area"),
        "construction_details": request.form.get("construction_details"),
        "occupancy": request.form.get("occupancy"),
        "max_employees": request.form.get("max_employees"),
        "max_other_occupants": request.form.get("max_other_occupants"),
        "total_people_present": request.form.get("total_people_present"),
        "sleeping_occupants": request.form.get("sleeping_occupants"),
        "disabled_employees": request.form.get("disabled_employees"),
        "disabled_occupants": request.form.get("disabled_occupants"),
        "remote_occupants": request.form.get("remote_occupants"),
        "young_persons": request.form.get("young_persons"),
        "specific_groups": request.form.get("specific_groups"),
        "past_fires": request.form.get("past_fires"),
        "fire_loss_cost": request.form.get("fire_loss_cost"),
        "additional_details": request.form.get("additional_details"),
        "fire_legislation": request.form.get("fire_legislation"),
        "enforced_by": request.form.get("enforced_by"),
        "other_legislation": request.form.get("other_legislation"),
        
        # New fields for fire safety measures
        "electrical_origin": request.form.get("electrical_origin"),
        "fixed_inspection": request.form.get("fixed_inspection"),
        "appliance_testing": request.form.get("appliance_testing"),
        "personal_appliances": request.form.get("personal_appliances"),
        "trailing_leads": request.form.get("trailing_leads"),
        "observations_7_02": request.form.get("observations_7_02"),
        "smoking": request.form.get("smoking"),
        "smoking_prohibited": request.form.get("smoking_prohibited"),
        "smoking_area": request.form.get("smoking_area"),
        "observations_8_02": request.form.get("observations_8_02")
    }

    # Save the form data to the database
    new_form = FormData(**data)
    db.session.add(new_form)
    db.session.commit()

    return redirect(url_for('view_forms'))

# Route to view all saved forms
@app.route('/')
def view_forms():
    forms = FormData.query.all()
    return render_template('view_forms.html', forms=forms)

# Route to edit a saved form
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_form(id):
    form = FormData.query.get_or_404(id)
    
    if request.method == 'POST':
        form.floors_above_ground = request.form['floors_above_ground']
        form.floors_below_ground = request.form['floors_below_ground']
        form.car_parking_floors = request.form['car_parking_floors']
        form.floor_area_per_floor = request.form['floor_area_per_floor']
        form.total_floor_area = request.form['total_floor_area']
        form.ground_floor_area = request.form['ground_floor_area']
        form.construction_details = request.form['construction_details']
        form.occupancy = request.form['occupancy']
        form.max_employees = request.form['max_employees']
        form.max_other_occupants = request.form['max_other_occupants']
        form.total_people_present = request.form['total_people_present']
        form.sleeping_occupants = request.form['sleeping_occupants']
        form.disabled_employees = request.form['disabled_employees']
        form.disabled_occupants = request.form['disabled_occupants']
        form.remote_occupants = request.form['remote_occupants']
        form.young_persons = request.form['young_persons']
        form.specific_groups = request.form['specific_groups']
        form.past_fires = request.form['past_fires']
        form.fire_loss_cost = request.form['fire_loss_cost']
        form.additional_details = request.form['additional_details']
        form.fire_legislation = request.form['fire_legislation']
        form.enforced_by = request.form['enforced_by']
        form.other_legislation = request.form['other_legislation']
        
        db.session.commit()
        return redirect(url_for('view_forms'))
    
    return render_template('edit_form.html', form=form)

@app.route('/generate_pdf/<int:id>')
def generate_pdf(id):
    form = FormData.query.get_or_404(id)

    data = {
        "floors_above_ground": form.floors_above_ground,
        "floors_below_ground": form.floors_below_ground,
        "car_parking_floors": form.car_parking_floors,
        "floor_area_per_floor": form.floor_area_per_floor,
        "total_floor_area": form.total_floor_area,
        "ground_floor_area": form.ground_floor_area,
        "construction_details": form.construction_details,
        "occupancy": form.occupancy,
        "max_employees": form.max_employees,
        "max_other_occupants": form.max_other_occupants,
        "total_people_present": form.total_people_present,
        "sleeping_occupants": form.sleeping_occupants,
        "disabled_employees": form.disabled_employees,
        "disabled_occupants": form.disabled_occupants,
        "remote_occupants": form.remote_occupants,
        "young_persons": form.young_persons,
        "specific_groups": form.specific_groups,
        "past_fires": form.past_fires,
        "fire_loss_cost": form.fire_loss_cost,
        "additional_details": form.additional_details,
        "fire_legislation": form.fire_legislation,
        "enforced_by": form.enforced_by,
        "other_legislation": form.other_legislation,
        "electrical_origin": form.electrical_origin,  # New field added here
        "fixed_inspection": form.fixed_inspection,  # New field added here
        "appliance_testing": form.appliance_testing,  # New field added here
        "personal_appliances": form.personal_appliances,  # New field added here
        "trailing_leads": form.trailing_leads,  # New field added here
        "observations_7_02": form.observations_7_02,  # New field added here
        "smoking": form.smoking,  # New field added here
        "smoking_prohibited": form.smoking_prohibited,  # New field added here
        "smoking_area": form.smoking_area,  # New field added here
        "observations_8_02": form.observations_8_02,  # New field added here
    }

    save_html(data)

    input_file = 'building_data_report.html'
    output_file = 'building_data_report.pdf'
    config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')
    pdfkit.from_file(input_file, output_file, configuration=config)

    return send_file(
        output_file,
        as_attachment=True,
        download_name="Building_Data_Report.pdf"
    )


def save_html(data):
    html = """
    <html>
    <head>
        <title>Building Data Report</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 20px;
                line-height: 1.6;
            }
            h2 {
                color: #2c3e50;
                text-align: center;
                background-color: #ecf0f1;
                padding: 10px;
                border-radius: 5px;
                border: 1px solid #bdc3c7;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
            }
            th, td {
                border: 1px solid #bdc3c7;
                padding: 8px;
                text-align: left;
            }
            th {
                background-color: #34495e;
                color: white;
            }
            tr:nth-child(even) {
                background-color: #f9f9f9;
            }
            tr:hover {
                background-color: #f1c40f;
                color: white;
            }
        </style>
    </head>
    <body>
    """

    # General Details Table
    html += "<h2>General Details</h2>"
    html += "<table>"
    html += "<tr><th>Type</th><th>Values</th></tr>"

    for key, value in data.items():
        html += f"<tr><td>{key}</td><td>{value}</td></tr>"

    html += "</table>"

    # New Fields Table
    html += "<h2>Electrical and Smoking Details</h2>"
    html += "<table>"
    html += "<tr><th>Description</th><th>Yes</th><th>No</th><th>N/A</th><th>Control Measures</th></tr>"

    new_fields = {
        "electrical_origin": "Electrical Origin",
        "fixed_inspection": "Fixed Inspection",
        "appliance_testing": "Appliance Testing",
        "personal_appliances": "Personal Appliances",
        "trailing_leads": "Trailing Leads",
        "observations_7_02": "Observations (7.02)",
        "smoking": "Smoking",
        "smoking_prohibited": "Smoking Prohibited",
        "smoking_area": "Smoking Area",
        "observations_8_02": "Observations (8.02)"
    }

    for field, description in new_fields.items():
        value = data.get(field, None)
        yes_tick = "✔" if value == "yes" else ""
        no_tick = "✔" if value == "no" else ""
        na_tick = "✔" if value == "n/a" else ""
        
        # Add the row for each field with the ticks
        html += f"<tr><td>{description}</td><td>{yes_tick}</td><td>{no_tick}</td><td>{na_tick}</td><td>{value if value else ''}</td></tr>"

    html += "</table>"
    html += "</body></html>"

    # Write the file with utf-8 encoding
    with open("building_data_report.html", "w", encoding="utf-8") as file:
        file.write(html)

if __name__ == "__main__":
    with app.app_context():  # Ensure we are within the application context
        db.create_all()  # Create the database
    app.run(debug=True)