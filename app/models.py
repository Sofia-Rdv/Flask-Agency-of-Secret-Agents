from app import db


# --- МОДЕЛЬ ДАННЫХ ---
class Agent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    codename = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    access_level = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f'<Agent {self.codename}>'