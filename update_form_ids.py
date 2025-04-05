from app import app, db, Form, Answer, PrimaryAnswer
import os
import shutil

def update_march_to_february():
    with app.app_context():
        try:
            # Find all forms from March 2025
            march_forms = Form.query.filter(
                Form.form_id.like('202503%')
            ).all()

            if not march_forms:
                print("No forms found from March 2025")
                return

            print(f"Found {len(march_forms)} forms to update")

            # Keep track of the sequence number for February
            feb_seq = 1

            for form in march_forms:
                old_form_id = form.form_id
                # Create new February form ID with sequential numbering
                new_form_id = f'20250228{feb_seq:03d}'
                print(f"Updating form {old_form_id} to {new_form_id}")

                # Update form ID in Form table
                form.form_id = new_form_id

                # Update form ID in Answer table
                Answer.query.filter_by(form_id=old_form_id).update({'form_id': new_form_id})

                # Update form ID in PrimaryAnswer table
                PrimaryAnswer.query.filter_by(form_id=old_form_id).update({'form_id': new_form_id})

                # Update uploads folder if it exists
                old_upload_path = os.path.join('uploads', old_form_id)
                if os.path.exists(old_upload_path):
                    new_upload_path = os.path.join('uploads', new_form_id)
                    # Create parent directory if it doesn't exist
                    os.makedirs(os.path.dirname(new_upload_path), exist_ok=True)
                    # Move the folder
                    shutil.move(old_upload_path, new_upload_path)
                    print(f"Moved uploads folder from {old_upload_path} to {new_upload_path}")

                feb_seq += 1

            # Commit all changes
            db.session.commit()
            print("Successfully updated all form IDs")

        except Exception as e:
            db.session.rollback()
            print(f"Error updating form IDs: {str(e)}")
            raise

if __name__ == '__main__':
    update_march_to_february()
