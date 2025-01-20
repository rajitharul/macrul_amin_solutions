from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///forms.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class GenerationDetails(db.Model):
    form_id = db.Column(db.Integer, primary_key=True)
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

class CheckboxDetails(db.Model):
    form_id = db.Column(db.Integer, db.ForeignKey('generation_details.form_id'), primary_key=True)
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

@app.route('/edit/<int:form_id>', methods=['GET', 'POST'])
def edit_form(form_id):
    gen_details = GenerationDetails.query.get_or_404(form_id)
    checkbox_details = CheckboxDetails.query.get_or_404(form_id)

    if request.method == 'POST':
        # Update generation details
        gen_details.floors_above_ground = request.form['floors_above_ground']
        gen_details.floors_below_ground = request.form['floors_below_ground']
        gen_details.car_parking_floors = request.form['car_parking_floors']
        gen_details.floor_area_per_floor = request.form['floor_area_per_floor']
        gen_details.total_floor_area = request.form['total_floor_area']
        gen_details.ground_floor_area = request.form['ground_floor_area']
        gen_details.construction_details = request.form['construction_details']
        gen_details.occupancy = request.form['occupancy']
        gen_details.max_employees = request.form['max_employees']
        gen_details.max_other_occupants = request.form['max_other_occupants']
        gen_details.total_people_present = request.form['total_people_present']
        gen_details.sleeping_occupants = request.form['sleeping_occupants']
        gen_details.disabled_employees = request.form['disabled_employees']
        gen_details.disabled_occupants = request.form['disabled_occupants']
        gen_details.remote_occupants = request.form['remote_occupants']
        gen_details.young_persons = request.form['young_persons']
        gen_details.specific_groups = request.form['specific_groups']
        gen_details.past_fires = request.form['past_fires']
        gen_details.fire_loss_cost = request.form['fire_loss_cost']
        gen_details.additional_details = request.form['additional_details']
        gen_details.fire_legislation = request.form['fire_legislation']
        gen_details.enforced_by = request.form['enforced_by']
        gen_details.other_legislation = request.form['other_legislation']

        # Update checkbox details
        checkbox_details.electrical_origin = request.form['electrical_origin']
        checkbox_details.fixed_inspection = request.form['fixed_inspection']
        checkbox_details.appliance_testing = request.form['appliance_testing']
        checkbox_details.personal_appliances = request.form['personal_appliances']
        checkbox_details.trailing_leads = request.form['trailing_leads']
        checkbox_details.observations_7_02 = request.form['observations_7_02']
        checkbox_details.smoking = request.form['smoking']
        checkbox_details.smoking_prohibited = request.form['smoking_prohibited']
        checkbox_details.smoking_area = request.form['smoking_area']
        checkbox_details.observations_8_02 = request.form['observations_8_02']

        db.session.commit()
        return redirect(url_for('view_forms'))

    return render_template('edit_form.html', gen_details=gen_details, checkbox_details=checkbox_details)

@app.route('/view')
def view_forms():
    gen_details = GenerationDetails.query.all()
    checkbox_details = CheckboxDetails.query.all()
    return render_template('view_forms.html', gen_details=gen_details, checkbox_details=checkbox_details)

if __name__ == '__main__':
    app.run(debug=True)
