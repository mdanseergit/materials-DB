from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Material(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    force = db.Column(db.Float)
    stress = db.Column(db.Float)
    strain = db.Column(db.Float)
    elasticity = db.Column(db.Float)

    def __repr__(self):
        return f"<Material {self.name}>"
