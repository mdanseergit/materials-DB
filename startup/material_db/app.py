from flask import Flask, render_template, request, redirect, send_file
from models import db, Material
import pandas as pd
import os

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['UPLOAD_FOLDER'] = 'uploads'

db.init_app(app)

with app.app_context():
    db.create_all()
@app.route('/')
def index():
    materials = Material.query.all()
    return render_template('index.html', materials=materials)
@app.route('/add', methods=['POST'])
def add_material():
    material = Material(
        name=request.form['name'],
        force=request.form['force'],
        stress=request.form['stress'],
        strain=request.form['strain'],
        elasticity=request.form['elasticity']
    )
    db.session.add(material)
    db.session.commit()
    return redirect('/')
@app.route('/upload', methods=['GET', 'POST'])
def upload_excel():
    if request.method == 'POST':
        file = request.files.get('file')
        if not file or file.filename == '':
            return "No file selected"

        import pandas as pd

        # Read Excel directly from memory
        df = pd.read_excel(file)

        # Loop through each row and save to DB
        for _, row in df.iterrows():
            material = Material(
                name=row['name'],
                force=row['force'],
                stress=row['stress'],
                strain=row['strain'],
                elasticity=row['elasticity']
            )
            db.session.add(material)
        db.session.commit()

        return redirect('/')
    
    return render_template('upload.html')

@app.route('/download')
def download_excel():
    import pandas as pd
    from flask import send_file
    import io

    # Get all data from database
    materials = Material.query.all()

    # Convert to DataFrame
    data = [{
        'name': m.name,
        'force': m.force,
        'stress': m.stress,
        'strain': m.strain,
        'elasticity': m.elasticity
    } for m in materials]

    df = pd.DataFrame(data)

    # Save Excel to memory
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Materials')
    output.seek(0)

    # Send file to user
    return send_file(
        output,
        download_name="materials_data.xlsx",
        as_attachment=True
    )

if __name__ == '__main__':
    app.run(debug=True)
