from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class GenerationDetails(db.Model):
    __tablename__ = 'generation_details'
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


class CheckboxForm(db.Model):
    __tablename__ = 'checkbox_form'
    form_id = db.Column(db.Integer, primary_key=True)
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
