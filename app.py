"""
HimGaon Dairy — Pure Milk, Pure Pahad
Complete E-Commerce Website with Order Management
Copyright © 2025 Sagar Kohli. All Rights Reserved.
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from functools import wraps
import os
import secrets

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(32))

# Database configuration - PERSISTENT SQL DATABASE
if os.environ.get('DATABASE_URL'):
    database_url = os.environ.get('DATABASE_URL')
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///himgaon_dairy.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ==================== DATABASE MODELS ====================

class Product(db.Model):
    """Product model - Data persists in SQL database"""
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name_en = db.Column(db.String(100), nullable=False)
    name_hi = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description_en = db.Column(db.Text, nullable=True)
    description_hi = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(500), nullable=True)
    stock = db.Column(db.Integer, default=0)
    category = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Product {self.name_en}>'


class Order(db.Model):
    """Order model - All orders stored permanently in SQL"""
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.String(20), unique=True, nullable=False)
    customer_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.Text, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='Pending')
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    admin_notes = db.Column(db.Text, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Order {self.order_id}>'


class OrderItem(db.Model):
    """Order items - Linked to orders"""
    __tablename__ = 'order_items'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    product_name_en = db.Column(db.String(100), nullable=False)
    product_name_hi = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    product = db.relationship('Product', backref='order_items')


# ==================== HELPER FUNCTIONS ====================

def generate_unique_order_id():
    """Generate unique order ID like HGD2025001"""
    prefix = "HGD"  # HimGaon Dairy
    year = datetime.now().year

    last_order = Order.query.order_by(Order.id.desc()).first()

    if last_order and last_order.order_id:
        try:
            last_num = int(last_order.order_id[-3:])
            new_num = last_num + 1
        except:
            new_num = 1
    else:
        new_num = 1

    return f"{prefix}{year}{new_num:03d}"


def admin_required(f):
    """Decorator for admin authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            flash('कृपया लॉगिन करें / Please login to access admin panel', 'danger')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function


# ==================== USER ROUTES ====================

@app.route('/')
def index():
    """Homepage"""
    products = Product.query.all()
    lang = session.get('language', 'en')
    return render_template('index.html', products=products, lang=lang)


@app.route('/set-language/<lang>')
def set_language(lang):
    """Set language preference"""
    if lang in ['en', 'hi']:
        session['language'] = lang
    return redirect(request.referrer or url_for('index'))


@app.route('/add-to-cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    """Add product to cart"""
    product = Product.query.get_or_404(product_id)
    quantity = int(request.form.get('quantity', 1))

    if quantity > product.stock:
        return jsonify({'success': False, 'message': 'स्टॉक उपलब्ध नहीं / Insufficient stock'}), 400

    if 'cart' not in session:
        session['cart'] = []

    cart = session['cart']
    found = False

    for item in cart:
        if item['product_id'] == product_id:
            new_quantity = item['quantity'] + quantity
            if new_quantity > product.stock:
                return jsonify({'success': False, 'message': 'उपलब्ध स्टॉक से अधिक / Exceeds stock'}), 400
            item['quantity'] = new_quantity
            found = True
            break

    if not found:
        cart.append({
            'product_id': product_id,
            'name_en': product.name_en,
            'name_hi': product.name_hi,
            'price': product.price,
            'quantity': quantity,
            'image_url': product.image_url
        })

    session['cart'] = cart
    session.modified = True

    return jsonify({'success': True, 'message': 'कार्ट में जोड़ा / Added to cart', 'cart_count': len(cart)})


@app.route('/cart')
def cart():
    """Shopping cart"""
    cart_items = session.get('cart', [])
    total = sum(item['price'] * item['quantity'] for item in cart_items)
    lang = session.get('language', 'en')
    return render_template('cart.html', cart_items=cart_items, total=total, lang=lang)


@app.route('/update-cart/<int:product_id>', methods=['POST'])
def update_cart(product_id):
    """Update cart quantity"""
    quantity = int(request.form.get('quantity', 1))
    product = Product.query.get_or_404(product_id)

    if quantity > product.stock:
        return jsonify({'success': False, 'message': 'उपलब्ध स्टॉक से अधिक / Exceeds stock'}), 400

    cart = session.get('cart', [])
    for item in cart:
        if item['product_id'] == product_id:
            if quantity <= 0:
                cart.remove(item)
            else:
                item['quantity'] = quantity
            break

    session['cart'] = cart
    session.modified = True
    return jsonify({'success': True})


@app.route('/remove-from-cart/<int:product_id>', methods=['POST'])
def remove_from_cart(product_id):
    """Remove item from cart"""
    cart = session.get('cart', [])
    cart = [item for item in cart if item['product_id'] != product_id]
    session['cart'] = cart
    session.modified = True
    return jsonify({'success': True})


@app.route('/checkout')
def checkout():
    """Checkout page"""
    cart_items = session.get('cart', [])
    if not cart_items:
        flash('आपकी कार्ट खाली है / Your cart is empty', 'warning')
        return redirect(url_for('index'))

    total = sum(item['price'] * item['quantity'] for item in cart_items)
    lang = session.get('language', 'en')
    return render_template('checkout.html', cart_items=cart_items, total=total, lang=lang)


@app.route('/place-order', methods=['POST'])
def place_order():
    """Place order - Saves to SQL database permanently"""
    cart_items = session.get('cart', [])

    if not cart_items:
        flash('आपकी कार्ट खाली है / Your cart is empty', 'warning')
        return redirect(url_for('index'))

    customer_name = request.form.get('customer_name', '').strip()
    email = request.form.get('email', '').strip()
    phone = request.form.get('phone', '').strip()
    address = request.form.get('address', '').strip()

    if not all([customer_name, email, phone, address]):
        flash('सभी फ़ील्ड आवश्यक हैं / All fields are required', 'danger')
        return redirect(url_for('checkout'))

    total_amount = sum(item['price'] * item['quantity'] for item in cart_items)
    unique_order_id = generate_unique_order_id()

    order = Order(
        order_id=unique_order_id,
        customer_name=customer_name,
        email=email,
        phone=phone,
        address=address,
        total_amount=total_amount,
        status='Pending'
    )

    try:
        db.session.add(order)
        db.session.flush()

        for item in cart_items:
            product = Product.query.get(item['product_id'])

            if product.stock < item['quantity']:
                db.session.rollback()
                flash(f'{product.name_hi} / {product.name_en} के लिए स्टॉक अपर्याप्त', 'danger')
                return redirect(url_for('cart'))

            order_item = OrderItem(
                order_id=order.id,
                product_id=product.id,
                product_name_en=product.name_en,
                product_name_hi=product.name_hi,
                quantity=item['quantity'],
                price=item['price']
            )
            db.session.add(order_item)
            product.stock -= item['quantity']

        db.session.commit()
        session['cart'] = []
        session.modified = True

        flash(f'ऑर्डर सफल! Order ID: {unique_order_id}', 'success')
        return redirect(url_for('order_confirmation', order_unique_id=unique_order_id))

    except Exception as e:
        db.session.rollback()
        flash('ऑर्डर त्रुटि / Order error. Please try again.', 'danger')
        return redirect(url_for('checkout'))


@app.route('/order-confirmation/<order_unique_id>')
def order_confirmation(order_unique_id):
    """Order confirmation page"""
    order = Order.query.filter_by(order_id=order_unique_id).first_or_404()
    lang = session.get('language', 'en')
    return render_template('confirmation.html', order=order, lang=lang)


@app.route('/track-order', methods=['GET', 'POST'])
def track_order():
    """Track order by Order ID and Phone Number"""
    lang = session.get('language', 'en')
    order = None

    if request.method == 'POST':
        order_id = request.form.get('order_id', '').strip().upper()
        phone = request.form.get('phone', '').strip()

        if order_id and phone:
            order = Order.query.filter_by(order_id=order_id, phone=phone).first()

            if not order:
                flash('ऑर्डर नहीं मिला / Order not found. Please check Order ID and Phone Number.', 'danger')

    return render_template('track_order.html', order=order, lang=lang)


# ==================== ADMIN ROUTES ====================

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username == 'admin' and password == 'himgaon2025':
            session['admin_logged_in'] = True
            session['admin_username'] = username
            flash('लॉगिन सफल / Login successful', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('अमान्य क्रेडेंशियल्स / Invalid credentials', 'danger')

    return render_template('admin/login.html')


@app.route('/admin/logout')
def admin_logout():
    """Admin logout"""
    session.pop('admin_logged_in', None)
    session.pop('admin_username', None)
    flash('लॉगआउट सफल / Logged out successfully', 'success')
    return redirect(url_for('admin_login'))


@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    """Admin dashboard"""
    total_products = Product.query.count()
    total_orders = Order.query.count()
    pending_orders = Order.query.filter_by(status='Pending').count()
    accepted_orders = Order.query.filter_by(status='Accepted').count()
    low_stock_products = Product.query.filter(Product.stock < 10).all()
    recent_orders = Order.query.order_by(Order.order_date.desc()).limit(5).all()

    return render_template('admin/dashboard.html', 
                         total_products=total_products,
                         total_orders=total_orders,
                         pending_orders=pending_orders,
                         accepted_orders=accepted_orders,
                         low_stock_products=low_stock_products,
                         recent_orders=recent_orders)


@app.route('/admin/products')
@admin_required
def admin_products():
    """Manage products"""
    products = Product.query.all()
    return render_template('admin/products.html', products=products)


@app.route('/admin/products/add', methods=['GET', 'POST'])
@admin_required
def admin_add_product():
    """Add new product"""
    if request.method == 'POST':
        name_en = request.form.get('name_en', '').strip()
        name_hi = request.form.get('name_hi', '').strip()
        price = request.form.get('price', 0, type=float)
        description_en = request.form.get('description_en', '').strip()
        description_hi = request.form.get('description_hi', '').strip()
        image_url = request.form.get('image_url', '').strip()
        stock = request.form.get('stock', 0, type=int)
        category = request.form.get('category', '').strip()

        if not name_en or not name_hi or price <= 0 or stock < 0:
            flash('अमान्य इनपुट / Invalid input', 'danger')
            return redirect(url_for('admin_add_product'))

        product = Product(
            name_en=name_en, name_hi=name_hi, price=price,
            description_en=description_en, description_hi=description_hi,
            image_url=image_url, stock=stock, category=category
        )

        try:
            db.session.add(product)
            db.session.commit()
            flash('उत्पाद जोड़ा गया / Product added successfully', 'success')
            return redirect(url_for('admin_products'))
        except:
            db.session.rollback()
            flash('त्रुटि / Error adding product', 'danger')

    return render_template('admin/add_product.html')


@app.route('/admin/products/edit/<int:product_id>', methods=['GET', 'POST'])
@admin_required
def admin_edit_product(product_id):
    """Edit product"""
    product = Product.query.get_or_404(product_id)

    if request.method == 'POST':
        product.name_en = request.form.get('name_en', '').strip()
        product.name_hi = request.form.get('name_hi', '').strip()
        product.price = request.form.get('price', 0, type=float)
        product.description_en = request.form.get('description_en', '').strip()
        product.description_hi = request.form.get('description_hi', '').strip()
        product.image_url = request.form.get('image_url', '').strip()
        product.stock = request.form.get('stock', 0, type=int)
        product.category = request.form.get('category', '').strip()

        try:
            db.session.commit()
            flash('उत्पाद अपडेट किया गया / Product updated successfully', 'success')
            return redirect(url_for('admin_products'))
        except:
            db.session.rollback()
            flash('त्रुटि / Error updating product', 'danger')

    return render_template('admin/edit_product.html', product=product)


@app.route('/admin/products/delete/<int:product_id>', methods=['POST'])
@admin_required
def admin_delete_product(product_id):
    """Delete product"""
    product = Product.query.get_or_404(product_id)

    try:
        db.session.delete(product)
        db.session.commit()
        flash('उत्पाद हटाया गया / Product deleted successfully', 'success')
    except:
        db.session.rollback()
        flash('त्रुटि / Error deleting product', 'danger')

    return redirect(url_for('admin_products'))


@app.route('/admin/orders')
@admin_required
def admin_orders():
    """View all orders"""
    status_filter = request.args.get('status', 'all')

    if status_filter == 'all':
        orders = Order.query.order_by(Order.order_date.desc()).all()
    else:
        orders = Order.query.filter_by(status=status_filter).order_by(Order.order_date.desc()).all()

    return render_template('admin/orders.html', orders=orders, status_filter=status_filter)


@app.route('/admin/orders/<int:order_id>')
@admin_required
def admin_order_detail(order_id):
    """View order details"""
    order = Order.query.get_or_404(order_id)
    return render_template('admin/order_detail.html', order=order)


@app.route('/admin/orders/<int:order_id>/accept', methods=['POST'])
@admin_required
def admin_accept_order(order_id):
    """Accept order"""
    order = Order.query.get_or_404(order_id)
    admin_notes = request.form.get('admin_notes', '').strip()

    order.status = 'Accepted'
    order.admin_notes = admin_notes
    order.updated_at = datetime.utcnow()

    try:
        db.session.commit()
        flash(f'ऑर्डर स्वीकार किया गया / Order {order.order_id} accepted successfully', 'success')
    except:
        db.session.rollback()
        flash('त्रुटि / Error accepting order', 'danger')

    return redirect(url_for('admin_order_detail', order_id=order_id))


@app.route('/admin/orders/<int:order_id>/reject', methods=['POST'])
@admin_required
def admin_reject_order(order_id):
    """Reject order and restore stock"""
    order = Order.query.get_or_404(order_id)
    admin_notes = request.form.get('admin_notes', '').strip()

    try:
        for item in order.items:
            product = Product.query.get(item.product_id)
            if product:
                product.stock += item.quantity

        order.status = 'Rejected'
        order.admin_notes = admin_notes
        order.updated_at = datetime.utcnow()

        db.session.commit()
        flash(f'ऑर्डर अस्वीकार किया गया / Order {order.order_id} rejected and stock restored', 'warning')
    except:
        db.session.rollback()
        flash('त्रुटि / Error rejecting order', 'danger')

    return redirect(url_for('admin_order_detail', order_id=order_id))


@app.route('/admin/orders/<int:order_id>/deliver', methods=['POST'])
@admin_required
def admin_deliver_order(order_id):
    """Mark order as delivered"""
    order = Order.query.get_or_404(order_id)

    order.status = 'Delivered'
    order.updated_at = datetime.utcnow()

    try:
        db.session.commit()
        flash(f'ऑर्डर डिलीवर किया गया / Order {order.order_id} marked as delivered', 'success')
    except:
        db.session.rollback()
        flash('त्रुटि / Error updating order', 'danger')

    return redirect(url_for('admin_order_detail', order_id=order_id))


# ==================== DATABASE INITIALIZATION ====================

def init_db():
    """Initialize database with products"""
    with app.app_context():
        db.create_all()
        
        if Product.query.count() == 0:
            products = [
                Product(
                    name_en="Fresh Cow Milk",
                    name_hi="ताजा गाय का दूध",
                    price=60.0,
                    description_en="Pure cow milk from Pithoragarh hills, 1 liter",
                    description_hi="पिथौरागढ़ की पहाड़ियों से शुद्ध गाय का दूध, 1 लीटर",
                    image_url="https://images.unsplash.com/photo-1563636619-e9143da7973b?w=500",
                    stock=50,
                    category="milk"
                ),
                Product(
                    name_en="Buffalo Milk",
                    name_hi="भैंस का दूध",
                    price=70.0,
                    description_en="Rich buffalo milk from local farms, 1 liter",
                    description_hi="स्थानीय फार्म से भैंस का दूध, 1 लीटर",
                    image_url="https://images.unsplash.com/photo-1550583724-b2692b85b150?w=500",
                    stock=40,
                    category="milk"
                ),
                Product(
                    name_en="Buttermilk (Chaach)",
                    name_hi="छाछ",
                    price=30.0,
                    description_en="Traditional Uttarakhandi buttermilk, 1 liter",
                    description_hi="पारंपरिक उत्तराखंडी छाछ, 1 लीटर",
                    image_url="https://images.unsplash.com/photo-1623065422902-30a2d299bbe4?w=500",
                    stock=60,
                    category="buttermilk"
                ),
                Product(
                    name_en="Fresh Dahi (Curd)",
                    name_hi="ताजा दही",
                    price=50.0,
                    description_en="Homemade fresh dahi from Pithoragarh, 500g",
                    description_hi="पिथौरागढ़ से घर का बना ताजा दही, 500 ग्राम",
                    image_url="https://images.unsplash.com/photo-1571212515416-26996e2fd0ae?w=500",
                    stock=45,
                    category="dahi"
                ),
                Product(
                    name_en="Pure Desi Ghee",
                    name_hi="शुद्ध देसी घी",
                    price=650.0,
                    description_en="100% pure cow ghee from Uttarakhand, 1 kg",
                    description_hi="उत्तराखंड से 100% शुद्ध गाय का घी, 1 किलो",
                    image_url="https://images.unsplash.com/photo-1587048411932-a04b46f98efe?w=500",
                    stock=30,
                    category="ghee"
                ),
                Product(
                    name_en="Mountain Butter",
                    name_hi="पहाड़ी मक्खन",
                    price=200.0,
                    description_en="Hand-churned butter from Pithoragarh, 500g",
                    description_hi="पिथौरागढ़ से हाथ से मथा मक्खन, 500 ग्राम",
                    image_url="https://images.unsplash.com/photo-1589985270826-4b7bb135bc9d?w=500",
                    stock=35,
                    category="butter"
                ),
                Product(
                    name_en="Free Range Eggs",
                    name_hi="देसी अंडे",
                    price=80.0,
                    description_en="Fresh free-range eggs from mountain farms, 6 pieces",
                    description_hi="पहाड़ी फार्म से ताजे देसी अंडे, 6 पीस",
                    image_url="https://images.unsplash.com/photo-1582722872445-44dc5f7e3c8f?w=500",
                    stock=100,
                    category="eggs"
                )
            ]
            
            db.session.bulk_save_objects(products)
            db.session.commit()
            print("✅ Database initialized with HimGaon Dairy products")
        else:
            print("✅ Database already contains products")


# Initialize database on startup (works with Gunicorn too)
with app.app_context():
    init_db()


# ==================== MAIN ====================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)
