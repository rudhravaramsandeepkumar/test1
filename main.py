from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
from datetime import datetime

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pharmacy.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)


# ---------------- Models ---------------- #

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120))
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    role = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class MedicineType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type_name = db.Column(db.String(120))
    description = db.Column(db.String(200))


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    description = db.Column(db.String(200))
    price = db.Column(db.Float)
    medicine_type_id = db.Column(db.Integer, db.ForeignKey('medicine_type.id'))
    stock = db.Column(db.Integer)
    image_url = db.Column(db.String(200))
    requires_prescription = db.Column(db.Boolean)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    total_amount = db.Column(db.Float)
    status = db.Column(db.String(50))
    prescription_file = db.Column(db.String(200))


class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    quantity = db.Column(db.Integer)
    price = db.Column(db.Float)


# ---------------- API Routes ---------------- #

@app.route('/')
def home():
    return "Online Pharmacy API is running!"


# ---- Users ----
@app.route('/users', methods=['POST'])
def create_user():
    data = request.json
    user = User(**data)
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "User created"}), 201


@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([{k: v for k, v in u.__dict__.items() if not k.startswith('_')} for u in users])


@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = User.query.get(user_id)
    data = request.json
    for key, value in data.items():
        setattr(user, key, value)
    db.session.commit()
    return jsonify({"message": "User updated"})


@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted"})


# ---- Medicine Types ----
@app.route('/types', methods=['POST'])
def add_type():
    data = request.json
    mtype = MedicineType(**data)
    db.session.add(mtype)
    db.session.commit()
    return jsonify({"message": "Medicine type added"}), 201


@app.route('/types', methods=['GET'])
def get_types():
    types = MedicineType.query.all()
    return jsonify([{k: v for k, v in t.__dict__.items() if not k.startswith('_')} for t in types])


@app.route('/types/<int:type_id>', methods=['PUT'])
def update_type(type_id):
    mtype = MedicineType.query.get(type_id)
    data = request.json
    for key, value in data.items():
        setattr(mtype, key, value)
    db.session.commit()
    return jsonify({"message": "Medicine type updated"})


@app.route('/types/<int:type_id>', methods=['DELETE'])
def delete_type(type_id):
    mtype = MedicineType.query.get(type_id)
    db.session.delete(mtype)
    db.session.commit()
    return jsonify({"message": "Medicine type deleted"})


# ---- Products ----
@app.route('/products', methods=['POST'])
def add_product():
    data = request.json
    product = Product(**data)
    db.session.add(product)
    db.session.commit()
    return jsonify({"message": "Product added"}), 201


@app.route('/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    return jsonify([{k: v for k, v in p.__dict__.items() if not k.startswith('_')} for p in products])


@app.route('/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    product = Product.query.get(product_id)
    data = request.json
    for key, value in data.items():
        setattr(product, key, value)
    db.session.commit()
    return jsonify({"message": "Product updated"})


@app.route('/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    product = Product.query.get(product_id)
    db.session.delete(product)
    db.session.commit()
    return jsonify({"message": "Product deleted"})


# ---- Orders ----
@app.route('/orders', methods=['POST'])
def place_order():
    data = request.json
    order = Order(
        user_id=data['user_id'],
        total_amount=data['total_amount'],
        status="Pending",
        prescription_file=data.get('prescription_file', '')
    )
    db.session.add(order)
    db.session.commit()
    for item in data['items']:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item['product_id'],
            quantity=item['quantity'],
            price=item['price']
        )
        db.session.add(order_item)
    db.session.commit()
    return jsonify({"message": "Order placed", "order_id": order.id}), 201


@app.route('/orders', methods=['GET'])
def get_orders():
    orders = Order.query.all()
    return jsonify([{k: v for k, v in o.__dict__.items() if not k.startswith('_')} for o in orders])


@app.route('/orders/<int:order_id>', methods=['PUT'])
def update_order(order_id):
    order = Order.query.get(order_id)
    data = request.json
    for key, value in data.items():
        setattr(order, key, value)
    db.session.commit()
    return jsonify({"message": "Order updated"})


@app.route('/orders/<int:order_id>', methods=['DELETE'])
def delete_order(order_id):
    order = Order.query.get(order_id)
    db.session.delete(order)
    db.session.commit()
    return jsonify({"message": "Order deleted"})


# ---- Prescription Upload ----
@app.route('/upload-prescription', methods=['POST'])
def upload_prescription():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    file = request.files['file']
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)
    return jsonify({"message": "Uploaded successfully", "path": filepath}), 200


@app.route('/upload-prescriptiontest2', methods=['POST'])
def upload_prescription1():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    file.save(filepath)
    return jsonify({"message": "Uploaded successfully", "path": filepath}), 200


<<<<<<< HEAD
@app.route('/upload-prescriptiontest3', methods=['POST'])
=======
@app.route('/upload-prescriptiontest4', methods=['POST'])
>>>>>>> 260551b7c2bc5109f6a8c6f46feb2a40f2e83a8c
def upload_prescription1():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    file.save(filepath)
    return jsonify({"message": "Uploaded successfully", "path": filepath}), 200


# ---------------- Init ---------------- #

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
