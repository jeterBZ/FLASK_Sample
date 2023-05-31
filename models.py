from extension import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    @staticmethod
    def init_db():
        temp = [
            ('0', 'admin', 'admin', 'admin@example.com'),
            ('1', 'guest', 'guest', 'guest@example.com')
        ]
        for elem in temp:
            user = User()
            user.id = elem[0]
            user.username = elem[1]
            user.set_password(elem[2])
            user.email = elem[3]
            db.session.add(user)
        db.session.commit()
    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)
