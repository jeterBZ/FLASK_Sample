from extension import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(120), index=True, unique=True)
    payment_info = db.Column(db.String(120))
    is_host = db.Column(db.Boolean, default=False)

    @staticmethod
    def init_db():
        temp = [
            ('0', 'admin', 'admin', 'admin@example.com', 'VISA', False),
            ('1', 'guest', 'guest', 'guest@example.com', 'VISA', False)
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
    
class Event(db.Model):
    __tablename__ = 'event'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140))
    description = db.Column(db.String(500))
    genra = db.Column(db.String(50))
    location = db.Column(db.String(120))
    address = db.Column(db.String(120))
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    host_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Order(db.Model):
    __tablename__ = 'order'

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
    booking_time = db.Column(db.DateTime)
    cost = db.Column(db.Float)
    is_cancelled = db.Column(db.Boolean, default=False)


class Review(db.Model):
    __tablename__ = 'review'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
    text = db.Column(db.String(500))
    rating = db.Column(db.Integer)


class BroadcastMessage(db.Model):
    __tablename__ = 'broadcast_message'

    id = db.Column(db.Integer, primary_key=True)
    host_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    content = db.Column(db.String(500))
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))


class Seat(db.Model):
    __tablename__ = 'seat'

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=True)
    row_number = db.Column(db.Integer)
    seat_no = db.Column(db.Integer)
    status = db.Column(db.String(10))
    price = db.Column(db.Float)