from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from datetime import datetime

# Crear la carpeta instance si no existe
instance_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')
os.makedirs(instance_path, exist_ok=True)

app = Flask(__name__, template_folder='app/templates', static_folder='app/static')
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(instance_path, "petlandia.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app', 'static', 'img', 'products')

# Asegurar que el directorio de uploads existe
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Modelos
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(200))
    stock = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    product = db.relationship('Product', backref='cart_items')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Rutas de autenticación
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user, remember=request.form.get('remember'))
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        
        flash('Usuario o contraseña incorrectos', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# Rutas principales
@app.route('/')
def index():
    products = Product.query.all()
    return render_template('index.html', products=products)

# Rutas del panel de administración
@app.route('/admin')
@login_required
def admin():
    if not current_user.is_admin:
        flash('Acceso no autorizado', 'danger')
        return redirect(url_for('index'))
    products = Product.query.all()
    return render_template('admin/dashboard.html', products=products)

@app.route('/admin/product/add', methods=['POST'])
@login_required
def add_product():
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'No autorizado'}), 403

    try:
        name = request.form.get('name')
        description = request.form.get('description')
        price = float(request.form.get('price'))
        stock = int(request.form.get('stock'))
        
        product = Product(
            name=name,
            description=description,
            price=price,
            stock=stock
        )

        if 'image' in request.files:
            file = request.files['image']
            if file.filename:
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                product.image_url = url_for('static', filename=f'img/products/{filename}')

        db.session.add(product)
        db.session.commit()
        
        flash('Producto agregado correctamente', 'success')
        return redirect(url_for('admin'))
    except Exception as e:
        flash(f'Error al agregar el producto: {str(e)}', 'danger')
        return redirect(url_for('admin'))

@app.route('/admin/product/<int:product_id>', methods=['GET', 'DELETE'])
@login_required
def manage_product(product_id):
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'No autorizado'}), 403

    product = Product.query.get_or_404(product_id)
    
    if request.method == 'GET':
        return jsonify({
            'id': product.id,
            'name': product.name,
            'description': product.description,
            'price': product.price,
            'stock': product.stock,
            'image_url': product.image_url
        })
    
    elif request.method == 'DELETE':
        try:
            # Primero eliminamos todos los items del carrito que referencian a este producto
            CartItem.query.filter_by(product_id=product_id).delete()
            
            # Luego eliminamos la imagen si existe
            if product.image_url:
                image_path = os.path.join(app.root_path, 'static', product.image_url.split('/static/')[-1])
                if os.path.exists(image_path):
                    os.remove(image_path)
            
            # Finalmente eliminamos el producto
            db.session.delete(product)
            db.session.commit()
            return jsonify({'success': True})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': str(e)})

@app.route('/admin/product/edit', methods=['POST'])
@login_required
def edit_product():
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'No autorizado'}), 403

    try:
        product_id = request.form.get('product_id')
        product = Product.query.get_or_404(product_id)
        
        product.name = request.form.get('name')
        product.description = request.form.get('description')
        product.price = float(request.form.get('price'))
        product.stock = int(request.form.get('stock'))
        
        if 'image' in request.files:
            file = request.files['image']
            if file.filename:
                # Eliminar imagen anterior si existe
                if product.image_url:
                    old_image_path = os.path.join(app.root_path, 'static', product.image_url.split('/static/')[-1])
                    if os.path.exists(old_image_path):
                        os.remove(old_image_path)
                
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                product.image_url = url_for('static', filename=f'img/products/{filename}')
        
        db.session.commit()
        flash('Producto actualizado correctamente', 'success')
        return redirect(url_for('admin'))
    except Exception as e:
        flash(f'Error al actualizar el producto: {str(e)}', 'danger')
        return redirect(url_for('admin'))

# Rutas del carrito
@app.route('/cart/add/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    try:
        product = Product.query.get_or_404(product_id)
        cart_item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()
        
        if cart_item:
            cart_item.quantity += 1
        else:
            cart_item = CartItem(user_id=current_user.id, product_id=product_id)
            db.session.add(cart_item)
        
        db.session.commit()
        
        cart_count = CartItem.query.filter_by(user_id=current_user.id).count()
        return jsonify({'success': True, 'cartCount': cart_count})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/cart/update/<int:product_id>', methods=['POST'])
@login_required
def update_cart_item(product_id):
    try:
        data = request.get_json()
        change = data.get('change', 0)
        
        cart_item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first_or_404()
        
        new_quantity = cart_item.quantity + change
        if new_quantity > 0:
            cart_item.quantity = new_quantity
            db.session.commit()
            return jsonify({'success': True})
        elif new_quantity == 0:
            db.session.delete(cart_item)
            db.session.commit()
            return jsonify({'success': True})
        
        return jsonify({'success': False, 'message': 'Cantidad inválida'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/cart/remove/<int:product_id>', methods=['POST'])
@login_required
def remove_from_cart(product_id):
    try:
        cart_item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first_or_404()
        db.session.delete(cart_item)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/cart')
@login_required
def view_cart():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    total = sum(item.product.price * item.quantity for item in cart_items)
    return render_template('cart.html', cart_items=cart_items, total=total)

@app.route('/checkout')
@login_required
def checkout():
    # Por implementar
    flash('Funcionalidad de checkout en desarrollo', 'info')
    return redirect(url_for('view_cart'))

# Crear las tablas de la base de datos
def init_db():
    with app.app_context():
        db.create_all()
        # Crear usuario admin si no existe
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                email='admin@petlandia.com',
                is_admin=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()

if __name__ == '__main__':
    init_db()
    app.run(debug=True) 