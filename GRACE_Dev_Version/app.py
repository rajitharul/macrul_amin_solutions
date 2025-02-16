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


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///forms.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


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
    {"id": "7.00", "question": "ELECTRONIC SOURCES OF IGNITION (Clause 13 and Annex B)", "control_measures": "N/A"},
    {"id": "7.01", "question": "Are reasonable measures taken to prevent fires of electrical origin?", "control_measures": "If there are no reasonable measures, tick NO and add recommendations of what action should be required here. Example 1: Combustible storage should be a safe separation distance of ½ metre or more from an electrical appliance. Example 2: Electrical intake should be enclosed into a 30-minute fire-resisting enclosure. Example 3: Combustible or flammable storage should be prohibited from the electrical intake room and managed regularly to be kept sterile at all times as recommended in the Home Office good practice fire guides. Example 4: Electrical equipment should be switched off when not in use and at the end of the working day. If YES or N/A delete control measure."},
    {"id": "7.02", "question": "More specifically:", "control_measures": "N/A"},
    {"id": "7.02a", "question": "Are fixed installations periodically inspected and tested?", "control_measures": "Introduce a programme of inspection and tests by a competent electrician to the current EICR certificate."},
    {"id": "7.02b", "question": "Is portable appliance testing carried out?", "control_measures": "Consider having portable electrical appliances tested yearly by a competent person to reduce the risk of electronic sources of ignition."},
    {"id": "7.02c", "question": "Is there suitable control over the use of personal electrical appliances?", "control_measures": "Consider having personal portable electrical appliances tested by a competent person."},
    {"id": "7.02d", "question": "Is there suitable limitation of trailing leads and adapters?", "control_measures": "Provide one electrical socket for each electrical appliance and appoint a competent contractor to carry out any required installation work."},
    {"id": "8.00", "question": "SMOKING (Clause 13 and Annex B)", "control_measures": "N/A"},
    {"id": "8.01", "question": "Are reasonable measures taken to prevent fires as a result of smoking?", "control_measures": "Introduce a safe smoking policy in designated smoking areas and enforce prohibiting smoking elsewhere."},
    {"id": "8.02", "question": "More specifically:", "control_measures": "N/A"},
    {"id": "8.02a", "question": "Is smoking prohibited in the building?", "control_measures": "Enforce the prohibition of smoking in the premises."},
    {"id": "8.02b", "question": "Is smoking prohibited in appropriate areas?", "control_measures": "Introduce a safe smoking policy in designated smoking areas and enforce prohibiting smoking elsewhere."},
    {"id": "8.02c", "question": "Are there suitable arrangements for those who wish to smoke?", "control_measures": "Introduce a safe smoking policy in designated smoking areas and enforce prohibiting smoking elsewhere."},
    {"id": "8.02d", "question": "Did the smoking policy appear to be observed at the time of inspection?", "control_measures": "Evidence of covert smoking was seen at the back of the premises (used cigarette filters) close to fire exit 8. Ensure all staff are aware this is unacceptable and smoking or vaping should only be performed in designated smoking areas."},
    {"id": "9.00", "question": "ARSON (Clause 13 and Annex B)", "control_measures": "N/A"},
    {"id": "9.01", "question": "Does basic security against arson by outsiders appear reasonable?", "control_measures": "Have a security specialist advise on additional precautions to avoid the risk of arson."},
    {"id": "9.02", "question": "Is there an absence of unnecessary fire load in close proximity to the premises or available for ignition by outsiders?", "control_measures": "Remove or relocate any fire load in close proximity to the premises and control access for ignition by outsiders."},
    {"id": "10.00", "question": "PORTABLE HEATERS, HEATING AND VENTILATION SYSTEMS (Clause 13 and Annex B)", "control_measures": "N/A"},
    {"id": "10.01", "question": "Is there satisfactory control over the use of portable heaters?", "control_measures": "Ban the use of portable heaters in the workplace and adjust fixed heating accordingly."},
    {"id": "10.02", "question": "Are fixed heating and ventilation installations subject to regular maintenance?", "control_measures": "Arrange for heating and ventilation system to be maintained by a competent contractor."},
    {"id": "11.00", "question": "COOKING (Clause 13 and Annex B)", "control_measures": "N/A"},
    {"id": "11.01", "question": "Are reasonable measures taken to prevent fires as a result of cooking?", "control_measures": "Maintain safe separation distance between appliances and flammable/combustible materials."},
    {"id": "11.02", "question": "More specifically, are filters cleaned or changed and ductwork cleaned regularly?", "control_measures": "Grease filters and clean ductwork should have maintenance on a regular basis to reduce the risk of fire."},
    {"id": "12.00", "question": "LIGHTNING (Clause 13 and Annex B)", "control_measures": "N/A"},
    {"id": "12.01", "question": "Does the building have a lightning protection system?", "control_measures": "Provide suitable lightning protection system to building in accordance with BS EN 62305-1:2011."},
    {"id": "13.00", "question": "HOUSEKEEPING (Clause 13 and Annex B)", "control_measures": "N/A"},
    {"id": "13.01", "question": "Is the overall standard of housekeeping adequate?", "control_measures": "Ensure a programme is introduced to improve housekeeping."},
    {"id": "13.02", "question": "More specifically:", "control_measures": "N/A"},
    {"id": "13.02a", "question": "Do combustible materials appear to be separated from ignition sources?", "control_measures": "Maintain safe separation distance of ½ metre between appliance and combustible storage."},
    {"id": "13.02b", "question": "Is unnecessary accumulation or inappropriate storage of combustible materials or waste avoided?", "control_measures": "External bin waste or internal storage should be managed to a higher standard and checked on regular intervals."},
    {"id": "14.00", "question": "HAZARDS INTRODUCED BY OUTSIDE CONTRACTORS AND BUILDING WORKS (Clause 13 and Annex B)", "control_measures": "N/A"},
    {"id": "14.01", "question": "Is there satisfactory control over works carried out in the building?", "control_measures": "Impose appropriate fire safety conditions on outside contractors."},
    {"id": "14.02", "question": "More specifically:", "control_measures": "N/A"},
    {"id": "14.02a", "question": "Where appropriate, are fire safety conditions imposed on outside contractors?", "control_measures": "Introduce a safe system of work for contractors who carry out work within the workplace."},
    {"id": "14.02b", "question": "Where appropriate, is a permit to work system used (e.g. for 'hot work')?", "control_measures": "Introduce a hot work permit system."},
    {"id": "14.02c", "question": "Are suitable precautions taken by in-house maintenance personnel who carry out works?", "control_measures": "Introduce a permit to work system for in-house maintenance workers who carry out 'hot work' involving processes such as welding or flame cutting."},
    {"id": "15.00", "question": "DANGEROUS SUBSTANCES (Clause 13)", "control_measures": "N/A"},
    {"id": "15.01", "question": "Are the general fire precautions adequate to address the hazards associated with dangerous substances used or stored within the premises?", "control_measures": "Reduce the quantity of dangerous substances to a minimum. Ensure that any release of a dangerous substance which may give rise to risk is suitably collected, safely contained, removed to a safe place, or otherwise rendered safe, as appropriate. Avoid ignition sources including electrostatic discharges. Arrange a DSEAR risk assessment by a competent contractor and reviews should be made regularly, especially when there is a significant change in use of substances or quantities."},
    {"id": "16.00", "question": "OTHER SIGNIFICANT FIRE HAZARDS THAT WARRANT CONSIDERATION", "control_measures": "N/A"},
    {"id": "16.01", "question": "Hazards: List and detail any other significant hazards here if applicable?", "control_measures": "N/A"},
    {"id": "17.00", "question": "MEANS OF ESCAPE (Clause 15c and Annex C)", "control_measures": "N/A"},
    {"id": "17.01", "question": "Is the design and maintenance of the means of escape considered adequate?", "control_measures": "Improve the means of escape in as follows."},
    {"id": "17.02", "question": "More Specifically:", "control_measures": "N/A"},
    {"id": "17.02a", "question": "Do staircase and exit capacities appear to be adequate for the number of occupants?", "control_measures": "Increase the width of the escape corridors to 1.2 metres."},
    {"id": "17.02b", "question": "Are there reasonable distances of travel:", "control_measures": "N/A"},
    {"id": "17.02b1", "question": "Where there is escape in a single direction?", "control_measures": "Provide a pass door in the following locations: [add locations]. Provide external fire escape in the following location: [add location]. Provide an additional exit to the escape corridor from the inner room: [add location]."},
    {"id": "17.02b2", "question": "Where there are alternative means of escape?", "control_measures": "Provide external fire escape in the following location: [add location]. Provide an additional exit to the escape corridor from the inner room: [add location]."},
    {"id": "17.02c", "question": "Is there adequate provision of exits?", "control_measures": "Provide additional escape exits in the following locations: [add location]."},
    {"id": "17.02d", "question": "Do fire exits open in the direction of escape, where necessary?", "control_measures": "Re-hang and recess the door to [add location] to open in the direction of escape."},
    {"id": "17.02e", "question": "Are there satisfactory arrangements for escape where revolving or sliding doors are used as exits?", "control_measures": "Provide pass final exit doors adjacent to revolving or sliding doors in the following locations: [add locations]."},
    {"id": "17.02f", "question": "Are the arrangements provided for securing exits satisfactory?", "control_measures": "Reduce the securing devices on final exit doors to a single device provided with a suitable sign on how to operate."},
    {"id": "17.02g", "question": "Is a suitable standard of protection designed for escape routes?", "control_measures": "Repair or replace damaged partitions to the required fire resisting rating including 1.8m (England & Wales) or 2.0m (Scotland) rule to external staircases."},
    {"id": "17.02h", "question": "Are there reasonable arrangements for means of escape for disabled people?", "control_measures": "Train fire marshals in how to use evac chairs provided/place in safe refuge such as fire rated staircase enclosure/relocate such workers or visitors to ground floor accommodation only. Provide evacuation lifts or fire lifts used to evacuate disabled people from upper floors. Provide a suitable refuge within the staircase enclosure in the following locations. Ensure communication equipment in refuge is tested regularly as required."},
    {"id": "17.03", "question": "Are the escape routes available for use and suitably maintained?", "control_measures": "Make sure escape routes are clear and ready for immediate use at any time."},
    {"id": "17.04", "question": "More Specifically:", "control_measures": "N/A"},
    {"id": "17.04a", "question": "Are fire-resisting doors maintained in sound condition and self-closing, where necessary?", "control_measures": "The following fire doors have gaps between door and frame. Provide self-closing devices to the following doors. The following doors have damage. Installations and maintenance should be actioned by a 3rd party accredited and competent contractor and must comply with the manufacturer recommendations or BS 8214:2016."},
    {"id": "17.04b", "question": "Is the fire-resisting construction protecting escape routes in sound condition?", "control_measures": "Arrange a competent contractor to survey and complete required works."},
    {"id": "17.04c", "question": "Are all escape routes clear of obstructions?", "control_measures": "Clear internal or external storage."},
    {"id": "17.04d", "question": "Are all fire exits easily and immediately openable?", "control_measures": "Remove one of the two securing devices from the final exit door from the [add location]. Install suitable interlocks on doors normally kept closed for security reasons in the following locations: [add locations]. Provide a panic bolt/latch and appropriate sign on the final exit door from [add location]."},
    {"id": "18.00", "question": "MEASURES TO LIMIT FIRE SPREAD AND DEVELOPMENT (Clause 15g)", "control_measures": "N/A"},
    {"id": "18.01", "question": "Is it considered that there is:", "control_measures": "N/A"},
    {"id": "18.01a", "question": "Compartmentation of a reasonable standard?", "control_measures": "Repair or replace damaged compartment walls, floors, or ceilings to the required fire-resisting rating."},
    {"id": "18.01b", "question": "Reasonable limitation of linings that may promote fire spread?", "control_measures": "Replace furniture that is damaged/perished as they are a fire hazard. Reduce risk by removing, covering or treating large areas of flammable wall and ceiling linings to reduce the rate of flame spread."},
    {"id": "18.02", "question": "As far as can be reasonably ascertained, are fire dampers provided necessary to protect critical means of escape against passage of fire, smoke, and products of combustion in the early stages of a fire?", "control_measures": "Have a survey actioned by a fire damper competent contractor."},
    {"id": "19.00", "question": "EMERGENCY ESCAPE LIGHTING (Clause 15e)", "control_measures": "N/A"},
    {"id": "19.01", "question": "Has a reasonable standard of emergency escape lighting system been provided?", "control_measures": "Provide emergency lighting to illuminate internal and external escape routes and points of emphasis."},
    {"id": "20.00", "question": "FIRE SAFETY SIGNS AND NOTICES (Clause 15d)", "control_measures": "N/A"},
    {"id": "20.01", "question": "Is there a reasonable standard of fire safety signs and notices?", "control_measures": "Provide green moving person signs with appropriate directional arrows to indicate the secondary escape routes in the following locations: [add locations]."},
    {"id": "21.00", "question": "MEANS OF GIVING WARNING IN CASE OF FIRE (Clause 15b)", "control_measures": "N/A"},
    {"id": "21.01", "question": "Is a reasonable fire detection and fire alarm system provided?", "control_measures": "Install an electrical fire alarm system conforming to BS 5839. Install a fire control panel that can be seen from the outside through an entrance to the building. Install a fire control repeater panel linked to the existing system on an external wall. Provide additional fire alarm call points linked into the existing system in the following locations: [add location]."},
    {"id": "21.02", "question": "Is there remote transmission of alarm signals?", "control_measures": "Install an auto-dialler device to inform an alarm receiving centre of a fire alarm activation via a secure telephone line."},
    {"id": "21.03", "question": "Is a zone plan of the fire alarm system displayed?", "control_measures": "Consider providing a zone plan of the system adjacent to the fire control panel."},
    {"id": "21.04", "question": "Has the premises had false alarms experience?", "control_measures": "Reduce false alarms by replacing smoke detector with a heat detector in the kitchen."},
    {"id": "22.00", "question": "MANUAL FIRE EXTINGUISHING APPLIANCES (Clause 15f)", "control_measures": "N/A"},
    {"id": "22.01", "question": "Is there reasonable provision of manual fire extinguishing appliances?", "control_measures": "Replace the non-standard fire extinguishers with BS/LPC approved extinguishers in the following locations."},
    {"id": "22.02", "question": "What type(s) of appliances are provided:", "control_measures": "N/A"},
    {"id": "22.02a", "question": "Portable fire extinguishers:", "control_measures": "Add portable fire extinguishers."},
    {"id": "22.02b", "question": "Hose reels:", "control_measures": "Remove hose reels and replace with modern portable extinguishers."},
    {"id": "22.02c", "question": "Fire blankets:", "control_measures": "Add fire blankets in the kitchen."},
    {"id": "22.03", "question": "Are all fire extinguishing appliances readily accessible?", "control_measures": "Remove obstructions in the following places."},
    {"id": "23.00", "question": "RELEVANT AUTOMATIC FIRE EXTINGUISHING SYSTEMS (Clause 15h)", "control_measures": "N/A"},
    {"id": "23.01", "question": "Type of fixed system(s):", "control_measures": "N/A"},
    {"id": "23.01a", "question": "Sprinkler system?", "control_measures": "Install sprinkler system if required and reasonably practicable due to life risk."},
    {"id": "23.01b", "question": "Misting system?", "control_measures": "Install misting system if required and reasonably practicable due to life risk."},
    {"id": "23.01c", "question": "Kitchen suppression system?", "control_measures": "Install kitchen suppression system if required and reasonably practicable due to life risk."},
    {"id": "23.01d", "question": "Inert gas flooding system?", "control_measures": "Install gas flooding system if required and reasonably practicable due to life risk."},
    {"id": "24.00", "question": "OTHER RELEVANT FIXED SYSTEMS AND EQUIPMENT (Clause 15i)", "control_measures": "N/A"},
    {"id": "24.01", "question": "Type of other fixed system(s) installed:", "control_measures": "Provide a system of roof ventilators, activated by automatic fire detectors and subdivide roof into appropriate smoke reservoirs."},
    {"id": "24.02", "question": "Is there suitable provision of firefighters' switch(es) for high voltage isolation of luminous tube signs, etc.?", "control_measures": "Install isolation device and inform fire authority that neon signs are installed so it can be logged on IRS."},
    {"id": "24.03", "question": "Are there appropriately sited facilities for electrical isolation of any photovoltaic (PV) cells, with appropriate signage, to assist the fire and rescue service?", "control_measures": "Install isolation device on solar panels and inform fire authority so it can be logged on IRS."},
    {"id": "25.00", "question": "PROCEDURES AND ARRANGEMENTS (Clause 16)", "control_measures": "N/A"},
    {"id": "25.01", "question": "Safety assistance:", "control_measures": "The competent person(s) appointed under Article 18 of the Fire Safety Order to assist the responsible person in undertaking the preventive and protection measures (i.e. relevant general fire precautions) is # ADD Fire Safety Manager's NAME HERE#."},
    {"id": "25.02", "question": "Fire safety at the premises is managed by:", "control_measures": "The fire safety at the premises is managed by #ADD Fire Safety Manager or Contractor's name HERE#."},
    {"id": "25.03", "question": "Is there a suitable record of the fire safety arrangements?", "control_measures": "Review fire emergency plan to detail required fire safety arrangements."},
    {"id": "25.04", "question": "Are procedures in the event of fire appropriate and properly documented, where appropriate?", "control_measures": "Formulate and document fire procedures for the premises."},
    {"id": "25.04a", "question": "Are there adequate procedures for investigating fire alarm signals?", "control_measures": "Make arrangements for investigating fire alarm signals."},
    {"id": "25.04b", "question": "Are there suitable arrangements for summoning the fire and rescue service?", "control_measures": "Ensure that the plan provides clear instructions on procedures for liaising with the fire brigade on arrival."},
    {"id": "25.04c", "question": "Are there suitable arrangements to meet the fire and rescue service on arrival and provide them with relevant information, including that relating to hazards to firefighters?", "control_measures": "Ensure that the plan gives clear instructions on any special risks on the premises."},
    {"id": "25.04d", "question": "Are there suitable arrangements for ensuring that the premises have been evacuated?", "control_measures": "Ensure that there are suitable arrangements for ensuring that the premises have been evacuated."},
    {"id": "25.04e", "question": "Is there a suitable fire assembly point(s)?", "control_measures": "Ensure that there are suitable fire assembly points."},
    {"id": "25.04f", "question": "Are there adequate procedures for evacuation of any disabled people who are likely to be present?", "control_measures": "Ensure that there are adequate PEEPs or GEEPs for the evacuation of any disabled people who are likely to be present."},
    {"id": "25.05", "question": "Are there persons nominated and trained to use fire extinguishing appliances?", "control_measures": "Nominate persons to be trained to use fire extinguishing appliances."},
    {"id": "25.06", "question": "Are there persons nominated to assist with evacuation of disabled people?", "control_measures": "Nominate persons to assist with evacuation of disabled people."},
    {"id": "25.07", "question": "Are there persons nominated to assist with evacuation of disabled people?", "control_measures": "Nominate persons to assist with evacuation of disabled people."},
    {"id": "25.08", "question": "Is there appropriate liaison with the fire and rescue service (i.e., by fire and rescue service crews visiting for familiarization visits)?", "control_measures": "Arrange for the local fire and rescue service to carry out pre-fire inspections of the premises."},
    {"id": "25.09", "question": "Are routine in-house inspections of fire precautions undertaken (e.g., in the course of health and safety inspections)?", "control_measures": "Ensure that all required routine fire inspections are carried out."},
    {"id": "26.00", "question": "TRAINING AND DRILLS (Clause 16h)", "control_measures": "N/A"},
    {"id": "26.01", "question": "Are all staff given adequate fire safety instruction and training on induction?", "control_measures": "Introduce an appropriate induction training presentation for the workplace."},
    {"id": "26.01a", "question": "Are they trained on induction?", "control_measures": "Arrange induction training for all new staff."},
    {"id": "26.01b", "question": "Are they given periodic refresher training?", "control_measures": "Arrange periodic training for all staff on fire awareness."},
    {"id": "26.01c", "question": "Are they given additional training to cover any specific roles and responsibilities?", "control_measures": "Arrange additional training for staff with specific roles."},
    {"id": "26.01d", "question": "Is the content of the training provided considered adequate?", "control_measures": "Add content to existing training as follows: [add details]."},
    {"id": "26.02", "question": "Are fire drills carried out at appropriate intervals?", "control_measures": "Arrange fire drills for every six months for the building occupiers. Ensure out-of-hour workers also participate in additional fire drills every six months."},
    {"id": "26.03", "question": "When the employees of another employer work in the premises, is appropriate information on the fire risks and fire safety measures provided?", "control_measures": "Provide other employees staff with information, instruction, or training on the fire safety measures on the premises."},
    {"id": "27.00", "question": "TESTING AND MAINTENANCE (Clause 16j)", "control_measures": "N/A"},
    {"id": "27.01", "question": "Is there adequate maintenance of the premises?", "control_measures": "Ensure that checks, inspections, and maintenance are carried out at appropriate intervals."},
    {"id": "27.02", "question": "Is weekly testing and periodic servicing of fire detection and alarm system undertaken?", "control_measures": "Senior fire marshal to ensure that weekly fire alarm tests and periodic servicing are carried out and recorded by competent persons."},
    {"id": "27.03", "question": "Is monthly and annual testing routines for emergency lighting?", "control_measures": "Senior fire marshal to ensure that monthly and annual emergency lighting tests are carried out and recorded by competent persons."},
    {"id": "27.04", "question": "Is annual maintenance of fire extinguishing appliances undertaken?", "control_measures": "Ensure that monthly checks and annual maintenance of portable fire-fighting appliances are carried out and recorded by competent persons."},
    {"id": "27.05", "question": "Is periodic inspection of external escape staircases and gangways undertaken?", "control_measures": "Arrange the periodic inspection of external escape staircase and gangways."},
    {"id": "27.06", "question": "Are six-monthly inspection and annual testing of rising mains undertaken?", "control_measures": "Arrange six-monthly inspection and annual pressure testing of dry riser."},
    {"id": "27.07", "question": "Are weekly and monthly testing, six-monthly inspection, and annual testing of fire-fighting lift(s) provided for the use by firefighters or evacuation of disabled people (evacuation lifts)?", "control_measures": "Arrange weekly and monthly testing, six-monthly inspection, and annual testing of fire-fighting or evacuation lifts."},
    {"id": "27.08", "question": "Are weekly testing and periodic inspection of sprinkler installations undertaken?", "control_measures": "Arrange periodic testing for sprinkler system by a competent person."},
    {"id": "27.09", "question": "Are routine checks of final exit doors and/or security fastenings undertaken?", "control_measures": "Arrange routine checks of final exit doors and security fastenings."},
    {"id": "27.10", "question": "Is an annual inspection of the lightning protection system undertaken?", "control_measures": "Arrange the annual inspection of the lightning protection system."},
    {"id": "27.11", "question": "Other relevant inspections or tests?", "control_measures": "Ensure that periodic inspections of Inergen/FM200/Argonite total flooding/local application system are carried out and recorded by competent persons."},
    {"id": "28.00", "question": "RECORDS (Clause 16k)", "control_measures": "N/A"},
    {"id": "28.01", "question": "Are there appropriate records of:", "control_measures": "N/A"},
    {"id": "28.01a", "question": "Fire drills?", "control_measures": "Provide and maintain a register of records for fire drills."},
    {"id": "28.01b", "question": "Fire Training?", "control_measures": "Provide and maintain a register of records for fire training."},
    {"id": "28.01c", "question": "Fire alarm tests?", "control_measures": "Provide and maintain a register of records for fire alarm tests."},
    {"id": "28.01d", "question": "False alarms?", "control_measures": "Provide and maintain a register of records for false alarms."},
    {"id": "28.01e", "question": "Emergency escape lighting tests?", "control_measures": "Provide and maintain a register of records for emergency lighting tests."},
    {"id": "28.01f", "question": "Maintenance and testing of other fixed fire protection systems?", "control_measures": "Provide and maintain a register of records for fixed fire system tests."},
    {"id": "28.01g", "question": "Is the fire emergency plan for the premises adequate?", "control_measures": "Review and add more relevant detail to the fire emergency plan."},
    {"id": "29.09", "question": "Is the fire emergency plan available to the enforcing authority?", "control_measures": "Ensure that the fire emergency plan is readily available for enforcing authority inspection."},
    {"id": "29.10", "question": "Are Personal Emergency Evacuation Plans (PEEPS) required and in place?", "control_measures": "Ensure that Personal Emergency Evacuation Plans are compiled in accordance with Home Office guidance and are readily available for enforcing authority inspection."}
]

HOUSING_QUESTIONS = [
    {"id": "7.00", "question": "ELECTRONIC SOURCES OF IGNITION (Clause 13 and Annex B)", "control_measures": "N/A"},
    {"id": "7.01", "question": "Are reasonable measures taken to prevent fires of electrical origin?", "control_measures": "Maintain safe separation distance of ½ metre between appliance and combustible materials. Enclose electrical intake in 30 or 60 minute fire resisting enclosure. Prohibit any combustible or flammable storage in electrical intake room. Ensure that sources of heat do not arise from faulty or overloaded electrical equipment. Ensure that all electrical fuses and circuit breakers etc. of the correct rating and suitable for the purpose. Switch equipment off at the end of the working day."},
    {"id": "7.02", "question": "More specifically:", "control_measures": "N/A"},
    {"id": "7.02a", "question": "Are fixed installations periodically inspected and tested?", "control_measures": "Introduce a programme of inspection and tests by a competent electrician to the current EICR certificate."},
    {"id": "7.02b", "question": "Is portable appliance testing carried out?", "control_measures": "Have workplace portable electrical appliances tested by a competent person."},
    {"id": "8.00", "question": "SMOKING (Clause 13 and Annex B)", "control_measures": "N/A"},
    {"id": "8.01", "question": "Are reasonable measures taken to prevent fires as a result of smoking?", "control_measures": "Introduce a safe smoking policy in designated smoking areas and enforce prohibiting smoking elsewhere."},
    {"id": "8.02", "question": "More specifically:", "control_measures": "N/A"},
    {"id": "8.02a", "question": "Is smoking prohibited in appropriate areas?", "control_measures": "Introduce a safe smoking policy in designated smoking areas and enforce prohibiting smoking elsewhere."},
    {"id": "8.02b", "question": "Are there suitable arrangements for those who wish to smoke?", "control_measures": "Introduce a safe smoking policy in designated smoking areas and enforce prohibiting smoking elsewhere."},
    {"id": "8.02c", "question": "Did the smoking policy appear to be observed at the time of inspection?", "control_measures": "Introduce a safe smoking policy in designated smoking areas and enforce prohibiting smoking elsewhere."},
    {"id": "8.02d", "question": "Are 'No smoking' signs provided in the common areas?", "control_measures": "Add 'No smoking' signage at main entrance and other areas if required."},
    {"id": "9.00", "question": "ARSON (Clause 13 and Annex B)", "control_measures": "N/A"},
    {"id": "9.01", "question": "Does basic security against arson by outsiders appear reasonable?", "control_measures": "Have a security specialist advise on additional precautions to avoid the risk of arson."},
    {"id": "9.02", "question": "Is there an absence of unnecessary fire load in close proximity to the premises or available for ignition by outsiders?", "control_measures": "Remove or relocate any fire load in close proximity to the premises and control access for ignition by outsiders."},
    {"id": "10.00", "question": "PORTABLE HEATERS, HEATING AND VENTILATION SYSTEMS (Clause 13 and Annex B)", "control_measures": "N/A"},
    {"id": "10.01", "question": "Is there satisfactory control over the use of portable heaters?", "control_measures": "Ban the use of portable heaters in the workplace and adjust fixed heating accordingly."},
    {"id": "10.02", "question": "Are fixed heating and ventilation installations subject to regular maintenance?", "control_measures": "Arrange for heating and ventilation system to be maintained by a competent contractor."},
    {"id": "11.00", "question": "COOKING (Clause 13 and Annex B)", "control_measures": "N/A"},
    {"id": "11.01", "question": "Are reasonable measures taken to prevent fires as a result of cooking?", "control_measures": "Maintain safe separation distance between appliances and flammable/combustible materials. Introduce safe working practices."},
    {"id": "12.00", "question": "LIGHTNING (Clause 13 and Annex B)", "control_measures": "N/A"},
    {"id": "12.01", "question": "Does the building have a lightning protection system?", "control_measures": "Provide suitable lightning protection system to building in accordance with BS EN 62305-1:2011."},
    {"id": "13.00", "question": "HOUSEKEEPING (Clause 13 and Annex B)", "control_measures": "N/A"},
    {"id": "13.01", "question": "Is the overall standard of housekeeping adequate?", "control_measures": "Ensure a programme is introduced to improve housekeeping."},
    {"id": "13.02", "question": "More specifically:", "control_measures": "N/A"},
    {"id": "13.02a", "question": "Do combustible materials appear to be separated from ignition sources?", "control_measures": "Maintain safe separation distance of ½ metre between appliance and combustible storage."},
    {"id": "13.02b", "question": "Is unnecessary accumulation or inappropriate storage of combustible materials or waste?", "control_measures": "Remove and manage unnecessary waste or storage."},
    {"id": "13.02c", "question": "Are gas and electricity intake/meter cupboards adequately secured and kept clear of combustible materials?", "control_measures": "Manage plant area access and inform staff and/or residents that they must be kept clear at all times due to the likelihood of ignition."},

    {"id": "14.00", "question": "HAZARDS INTRODUCED BY OUTSIDE CONTRACTORS AND BUILDING WORKS (Clause 13 and Annex B)", "control_measures": "N/A"},
    {"id": "14.01", "question": "Is there satisfactory control over works carried out in the building?", "control_measures": "Impose appropriate fire safety conditions on outside contractors."},
    {"id": "15.00", "question": "DANGEROUS SUBSTANCES (Clause 13)", "control_measures": "N/A"},
    {"id": "15.01", "question": "Are the general fire precautions adequate to address the hazards associated with dangerous substances used or stored within the premises?", "control_measures": "Reduce the quantity of dangerous substances to a minimum. Manage out collation of any dangerous substances."},
    {"id": "16.00", "question": "OTHER SIGNIFICANT FIRE HAZARDS THAT WARRANT CONSIDERATION", "control_measures": "N/A"},
    {"id": "16.01", "question": "Hazards: List and detail any other significant hazards here:", "control_measures": "N/A"},
    {"id": "17.00", "question": "MEANS OF ESCAPE (Clause 15c and Annex C)", "control_measures": "N/A"},
    {"id": "17.01", "question": "Is the design and maintenance of the means of escape considered adequate?", "control_measures": "Improve the means of escape in as follows:"},
    {"id": "17.02", "question": "More Specifically:", "control_measures": "N/A"},
    {"id": "17.02a", "question": "Are there reasonable distances of travel?", "control_measures": "N/A"},
    {"id": "17.02a1", "question": "Where there is escape in a single direction?", "control_measures": "Provide a pass door in the following locations: [add locations]. Provide external fire escape in the following location: [add location]. Provide an additional exit to the escape corridor from the inner room: [add location]."},
    {"id": "17.02a2", "question": "Where there are alternative means of escape?", "control_measures": "Provide external fire escape in the following location: [add location]. Provide an additional exit to the escape corridor from the inner room: [add location]."},
    {"id": "17.02b", "question": "Is there adequate provision of exits?", "control_measures": "Provide additional escape exits in the following locations: [add location]."},
    {"id": "17.02c", "question": "Do fire exits open in the direction of escape, where necessary?", "control_measures": "Re-hang and recess the door to [add location] to open in the direction of escape."},
    {"id": "17.02d", "question": "Are the arrangements provided for securing exits satisfactory?", "control_measures": "Reduce the securing devices on final exit doors to a single device provided with a suitable sign on how to operate."},
    {"id": "17.02e", "question": "Is the fire-resisting construction (including any glazing) protecting escape routes and staircases of a suitable standard and maintained in sound condition?", "control_measures": "Repair or replace damaged partitions to the required fire-resisting rating including 1.8m (England & Wales) or 2.0m (Scotland) rule to external staircases."},
    {"id": "17.02f", "question": "Is the fire resistance of doors to staircases and the common areas considered adequate, and are the doors maintained in sound condition?", "control_measures": "The following staircase and common area fire doors require attention. Fire door maintenance or installations should be actioned by a 3rd party accredited and competent contractor and must comply with manufacturer recommendations or BS 8214:2016."},
    {"id": "17.02g", "question": "Are suitable self-closing devices fitted to fire doors in the common areas?", "control_measures": "Install BS EN 1154 self-closing devices to the following common area fire doors. Installations and maintenance should be actioned by a 3rd party accredited and competent contractor and must comply with manufacturer recommendations or BS 8214:2016."},
    {"id": "17.02h", "question": "Is the fire resistance of doors to meter cupboards/store rooms/plant rooms in common areas considered adequate, and are they adequately secured and/or fitted with suitable self-closing devices?", "control_measures": "The following common area plant room fire doors require attention. Fire door maintenance or installations should be actioned by a 3rd party accredited and competent contractor and must comply with manufacturer recommendations or BS 8214:2016."},
    {"id": "17.02i", "question": "Is the fire resistance of flat entrance doors considered adequate, and are the doors maintained in sound condition?", "control_measures": "The following flat entrance fire doors require attention. Fire door maintenance or installations should be actioned by a 3rd party accredited and competent contractor and must comply with manufacturer recommendations or BS 8214:2016."},
    {"id": "17.02j", "question": "Are suitable self-closing devices fitted to flat entrance fire doors and, where fitted, maintained in good working order?", "control_measures": "Install BS EN 1154 self-closing devices to the following flat entrance fire doors. Installations and maintenance should be actioned by a 3rd party accredited and competent contractor and must comply with manufacturer recommendations or BS 8214:2016."},
    {"id": "17.02k", "question": "Are there adequate smoke control provisions to protect the common escape routes, where necessary?", "control_measures": "Consider advice from a competent smoke control engineer."},
    {"id": "17.02l", "question": "Are all escape routes clear of obstructions?", "control_measures": "Clear internal or external storage."},
    {"id": "17.02m", "question": "Are all fire exits easily and immediately openable?", "control_measures": "Remove one of the two securing devices from the final exit door from the [add location]. Install suitable interlocks on doors normally kept closed for security reasons in the following locations: [add locations]. Provide a panic bolt/latch and appropriate sign on the final exit door from [add location]."},
    {"id": "17.02n", "question": "Are there reasonable arrangements for means of escape for disabled people?", "control_measures": "Improve escape options for disabled people. Move residence with mobility issues to the ground floor. Provide PEEPs or GEEPs where necessary."},
    {"id": "18.00", "question": "MEASURES TO LIMIT FIRE SPREAD AND DEVELOPMENT (Clause 15g)", "control_measures": "N/A"},
    {"id": "18.01", "question": "Is it considered that there is/are:", "control_measures": "N/A"},
    {"id": "18.01a", "question": "Adequate levels of compartmentation between floors and between flats and the common escape routes?", "control_measures": "Action a compartmentation survey by a competent contractor."},
    {"id": "18.01b", "question": "Reasonable limitation of linings that may promote fire spread?", "control_measures": "Remove the combustible construction and replace it with fire-resisting or non-combustible alternatives."},
    {"id": "18.01c", "question": "As far as can be reasonably ascertained, reasonable fire separation within any roof space?", "control_measures": "Have a roof compartmentation survey actioned by a competent contractor."},
    {"id": "18.01d", "question": "Adequately fire-protected service risers and/or ducts in common areas, that will restrict the spread of fire and smoke?", "control_measures": "Have service risers and/or ducts inspected by a competent contractor."},
    {"id": "18.02", "question": "As far as can be reasonably ascertained, are fire dampers provided necessary to protect critical means of escape against passage of fire, smoke, and products of combustion in the early stages of a fire?", "control_measures": "Have an invasive survey actioned by a fire damper competent specialist."},
    {"id": "19.00", "question": "EMERGENCY ESCAPE LIGHTING (Clause 15e)", "control_measures": "N/A"},
    {"id": "19.01", "question": "Has a reasonable standard of emergency escape lighting system been provided?", "control_measures": "Provide emergency lighting to illuminate internal and external escape routes and points of emphasis."},
    {"id": "20.00", "question": "FIRE SAFETY SIGNS AND NOTICES (Clause 15d)", "control_measures": "N/A"},
    {"id": "20.01", "question": "Is there a reasonable standard of fire safety signs and notices?", "control_measures": "Provide green moving person signs with appropriate directional arrows to indicate the secondary escape routes in the following locations: [add locations]."},
    {"id": "21.00", "question": "MEANS OF GIVING WARNING IN CASE OF FIRE (Clause 15b)", "control_measures": "N/A"},
    {"id": "21.01", "question": "Is a reasonable fire detection and fire alarm system provided in common areas, where necessary?", "control_measures": "See Sleeping Accommodation Home Office Fire guide P57 for recommended minimum fire alarm standards. Install an electrical fire alarm system conforming to BS 5839. Provide additional fire alarm call points linked into the existing system in the following locations: [add location]."},
    {"id": "21.02", "question": "If there is a communal fire detection and fire alarm system, does it extend into the dwellings?", "control_measures": "Actions required: [specify actions]."},
    {"id": "21.03", "question": "Where appropriate, has a fire alarm zone plan been provided?", "control_measures": "Provide a fire alarm zone plan of the system adjacent to the main fire control panel."},
    {"id": "21.04", "question": "Where appropriate, are there adequate arrangements for silencing and resetting an alarm condition?", "control_measures": "Consider how alarms will be reset when required, especially in a non-staffed premises."},
    {"id": "22.00", "question": "MANUAL FIRE EXTINGUISHING APPLIANCES (Clause 15f)", "control_measures": "N/A"},
    {"id": "22.01", "question": "Is there reasonable provision of manual fire extinguishing appliances?", "control_measures": "Are extinguishers required in common areas? Replace the non-standard fire extinguishers with BS/LPC approved extinguishers in the following locations."},
    {"id": "22.02", "question": "Are all fire extinguishing appliances readily accessible?", "control_measures": "Remove obstructions in the following places."},
    {"id": "23.00", "question": "RELEVANT AUTOMATIC FIRE EXTINGUISHING SYSTEMS (Clause 15h)", "control_measures": "N/A"},
    {"id": "23.01", "question": "Type of fixed system(s):", "control_measures": "N/A"},
    {"id": "23.01a", "question": "Sprinkler system?", "control_measures": "Install sprinkler system if required and reasonably practicable due to life risk."},
    {"id": "23.01b", "question": "Misting system?", "control_measures": "Install misting system if required and reasonably practicable due to life risk."},
    {"id": "24.00", "question": "OTHER RELEVANT FIXED SYSTEMS AND EQUIPMENT (Clause 15i)", "control_measures": "N/A"},
    {"id": "24.01", "question": "Type of other fixed system(s) installed:", "control_measures": "Provide a system of roof ventilators, activated by automatic fire detectors."},
    {"id": "24.02", "question": "Are there appropriately sited facilities for electrical isolation of any photovoltaic (PV) cells, with appropriate signage, to assist the fire and rescue service?", "control_measures": "Install isolation device on solar panels and inform fire authority so it can be logged on IRS."},
    {"id": "25.00", "question": "PROCEDURES AND ARRANGEMENTS (Clause 16)", "control_measures": "N/A"},
    {"id": "25.01", "question": "Safety assistance:", "control_measures": "The competent person(s) appointed under Article 18 of the Fire Safety Order to assist the responsible person in undertaking the preventive and protection measures (i.e. relevant general fire precautions) is # ADD NAME HERE#."},
    {"id": "25.02", "question": "Fire safety at the premises is managed by:", "control_measures": "The fire safety at the premises is managed by #ADD MANAGEMENT PERSON OR CONTRACTOR HERE#."},
    {"id": "25.03", "question": "Is there a suitable record of the fire safety arrangements?", "control_measures": "Review fire emergency plan to detail required fire safety arrangements."},
    {"id": "25.04", "question": "Evacuation strategy:", "control_measures": "The evacuation strategy for this sleeping risk premises is: Stay put / Simultaneous evacuation / Other (please specify)."},
    {"id": "25.05", "question": "Are procedures in the event of a fire appropriate and properly documented, where appropriate?", "control_measures": "Add more required detail into the fire emergency plan (FEP)."},
    {"id": "25.06", "question": "Are routine in-house inspections of fire precautions undertaken (e.g. in the course of health and safety inspections)?", "control_measures": "Ensure that all required routine fire inspections are carried out."},
    {"id": "26.00", "question": "TRAINING AND DRILLS (Clause 16h)", "control_measures": "N/A"},
    {"id": "26.01", "question": "Are all staff given adequate fire safety instruction and training on induction?", "control_measures": "Introduce an appropriate induction training presentation for the workplace."},
    {"id": "26.02", "question": "When the employees of another employer work in the premises, is appropriate information on the fire risks and fire safety measures provided?", "control_measures": "Provide other employees staff with information, instruction or training on the fire safety measures on the premises."},
    {"id": "27.00", "question": "TESTING AND MAINTENANCE (Clause 16j)", "control_measures": "N/A"},
    {"id": "27.01", "question": "Is there adequate maintenance of the premises?", "control_measures": "Ensure that checks, inspections, and maintenance are carried out at appropriate intervals."},
    {"id": "27.02", "question": "Is weekly testing and periodic servicing of fire detection and alarm system undertaken?", "control_measures": "Ensure that weekly fire alarm test and periodic servicing are carried out and recorded by competent persons."},
    {"id": "27.03", "question": "Is monthly and annual testing routines for emergency lighting?", "control_measures": "Ensure that monthly, six-monthly, and annual emergency lighting is carried out and recorded by competent persons."},
    {"id": "27.04", "question": "Is annual maintenance of fire extinguishing appliances undertaken?", "control_measures": "Ensure that monthly checks and annual maintenance of portable fire fighting appliances are carried out and recorded by competent persons."},
    {"id": "27.05", "question": "Are six-monthly inspection and annual testing of rising mains undertaken?", "control_measures": "Arrange six-monthly inspection and annual pressure testing of dry riser."},
    {"id": "27.06", "question": "Are weekly and monthly testing, six-monthly inspection and annual testing of fire-fighting lift(s) provided for the use by firefighters or evacuation of disabled people (evacuation lifts)?", "control_measures": "Arrange weekly and monthly testing, six-monthly inspection, and annual testing of fire-fighting or evacuation lifts."},
    {"id": "27.07", "question": "Other relevant inspections or tests?", "control_measures": "Ensure that periodic inspections of sprinkler or ventilation systems are carried out and recorded by competent persons."},
    {"id": "28.00", "question": "RECORDS (Clause 16k)", "control_measures": "N/A"},
    {"id": "28.01", "question": "Are there appropriate records of:", "control_measures": "N/A"},
    {"id": "28.01a", "question": "Fire alarm tests (where relevant)?", "control_measures": "Provide and maintain a register of records for fire alarm tests."},
    {"id": "28.01b", "question": "Emergency escape lighting tests?", "control_measures": "Provide and maintain a register of records for emergency lighting tests."},
    {"id": "28.01c", "question": "Maintenance and testing of other fire protection equipment?", "control_measures": "Provide and maintain a register of records for fixed fire system tests."},
    {"id": "29.00", "question": "PREMISES INFORMATION BOX (Clause 15c)", "control_measures": "N/A"},
    {"id": "29.01", "question": "Is there a suitably located premises information box for the fire and rescue service?", "control_measures": "Provide premises information box with details to assist the fire and rescue service."},
    {"id": "29.02", "question": "Are there arrangements to keep the premises information box up to date?", "control_measures": "Regularly check and update the premises information box."},
    {"id": "29.09", "question": "Is the fire emergency plan available to the enforcing authority?", "control_measures": "Ensure that fire emergency plan is readily available for enforcing authority inspection."},
    {"id": "29.10", "question": "Are Personal Emergency Evacuation Plans (PEEPS) required and in place?", "control_measures": "Ensure that Personal Emergency Evacuation Plans are compiled in accordance with DCLG guidance and are readily available for enforcing authority inspection."},
    {"id": "30.00", "question": "ENGAGEMENT WITH RESIDENTS (Clause 16l)", "control_measures": "N/A"},
    {"id": "30.01", "question": "Has information on fire procedures been disseminated to residents?", "control_measures": "Provide a clear fire action document for all residents."},
    {"id": "30.02", "question": "Is fire safety information disseminated to residents?", "control_measures": "Provide clear fire safety information for all residents."}
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

