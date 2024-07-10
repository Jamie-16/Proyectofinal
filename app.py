from flask import Flask, render_template, request, redirect, url_for, flash, get_flashed_messages
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, current_user, login_user, logout_user, login_required, UserMixin

#utilizamos sqlalchemy
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # Cambia esto por una clave secreta real
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Girlythings.db'
db = SQLAlchemy(app)
#encriptacion de contraseñas
bcrypt = Bcrypt(app)
#definicion de funciones para el login
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Definir modelos para las tablas
#integrar los usuarios a la base de datos
class User(db.Model, UserMixin):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    def get_id(self):
        return str(self.user_id)
#integrar la categoria de cada post a la base de datos
class Category(db.Model):
    category_id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(50), unique=True, nullable=False)
#integrar los post a la base de datos
class Post(db.Model):
    post_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    body = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.category_id'), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    image_path = db.Column(db.String(255))

    # Definir relación con User
    user = db.relationship('User', backref=db.backref('posts', lazy=True))

    # Relación con Category
    category = db.relationship('Category', backref=db.backref('posts', lazy=True))



#pendiente
    def can_edit(self):
        return current_user.is_authenticated and self.user_id == current_user.user_id

    def can_delete(self):
        return current_user.is_authenticated and self.user_id == current_user.user_id

#integramos los comentarios a la base de datos
class Comment(db.Model):
    comment_id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.post_id'), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

#relacionamos los comentarios con el usuario y los post

    # Definir relación con User
    user = db.relationship('User', backref=db.backref('comments', lazy=True))

    # Relación con Post
    post = db.relationship('Post', backref=db.backref('comments', lazy=True))


#validacion del login

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('register'))

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(username=username, email=email, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created!', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user, remember='remember' in request.form)
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')

    return render_template('login.html')

@app.route("/")
@login_required
def home():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template('index.html', posts=posts)

@app.route("/makeup")
@login_required
def makeup():
    posts = Post.query.filter_by(category_id=1).all()
    return render_template('makeup.html', posts=posts)

@app.route("/outfits")
@login_required
def outfits():
    posts = Post.query.filter_by(category_id=3).all()
    return render_template('outfits.html', posts=posts)

@app.route("/hair")
@login_required
def hair():
    posts = Post.query.filter_by(category_id=2).all()
    return render_template('hair.html', posts=posts)

@app.route('/create_post', methods=['GET', 'POST'])
@login_required
def create_post():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        category_id = request.form['category_id']
        image_file = request.files['image']  # Obtener el archivo de imagen subid
        user_id = current_user.user_id  # Obtener el ID del usuario actual

        if not title or not body or not category_id or not image_file:
            flash('All fields are required!', 'danger')
        else:
            # Guardar la imagen en el sistema de archivos
            image_filename = image_file.filename
            image_path = f'static/uploads/{image_filename}'
            image_file.save(image_path)
            # Crear el nuevo post con la ruta de la imagen
            new_post = Post(title=title, body=body, user_id=user_id, category_id=category_id, image_path=image_path)
            db.session.add(new_post)
            db.session.commit()
            flash('Post created successfully!', 'success')
            return redirect(url_for('create_post'))

    categories = Category.query.all()
    return render_template('create_post.html', categories=categories)

@app.route("/post/<int:post_id>", methods=['GET', 'POST'])
@login_required
def view_post(post_id):
    post = Post.query.get_or_404(post_id)
    comments = Comment.query.filter_by(post_id=post_id).all()
    username = post.user.username

    if request.method == 'POST':
        body = request.form['body']
        rating = int(request.form['rating'])
        user_id = current_user.user_id

        new_comment = Comment(body=body, rating=rating, user_id=user_id, post_id=post_id)
        db.session.add(new_comment)
        db.session.commit()
        flash('Comment added successfully!', 'success')
        return redirect(url_for('view_post', post_id=post_id))

    return render_template('post.html', post=post, comments=comments, username=username)

@app.route('/add_comment/<int:post_id>', methods=['POST'])
def add_comment(post_id):
    if request.method == 'POST':
        body = request.form['body']
        rating = int(request.form['rating'])
        user_id = current_user.user_id

        # Verificar que el usuario no esté comentando en su propia publicación
        post = Post.query.get_or_404(post_id)
        if post.user_id == user_id:
            flash('No puedes comentar en tu propia publicación.', 'danger')
            return redirect(url_for('view_post', post_id=post_id))

        # Verificar que el usuario no haya comentado más de una vez en la misma publicación
        existing_comment = Comment.query.filter_by(user_id=user_id, post_id=post_id).first()
        if existing_comment:
            flash('Ya has comentado en esta publicación.', 'danger')
            return redirect(url_for('view_post', post_id=post_id))

        # Crea un nuevo comentario y lo guarda en la base de datos
        new_comment = Comment(body=body, rating=rating, user_id=user_id, post_id=post_id)
        db.session.add(new_comment)
        db.session.commit()

        flash('Comentario agregado correctamente!', 'success')

        # Redirige de vuelta a la misma página del post después de agregar el comentario
        return redirect(url_for('view_post', post_id=post_id))

    # En caso de que no sea un método POST, podría manejarlo de otra manera según tus necesidades
    # Puedes agregar una lógica para manejar errores aquí si lo necesitas

    # Normalmente no deberías llegar aquí si todo está configurado correctamente para el método POST
    return redirect(url_for('home'))  # o redirige a otra página si es necesario

@app.route("/edit_post/<int:post_id>", methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    if not post.can_edit():
        flash('No tienes permiso para editar esta publicación.', 'danger')
        return redirect(url_for('home'))

    if request.method == 'POST':
        post.title = request.form['title']
        post.body = request.form['body']
        post.category_id = request.form['category_id']
        image_file = request.files['image']

        if image_file:
            image_filename = image_file.filename
            image_path = f'static/uploads/{image_filename}'
            image_file.save(image_path)
            post.image_path = image_path

        db.session.commit()
        flash('Publicación actualizada correctamente.', 'success')
        return redirect(url_for('view_post', post_id=post_id))

    categories = Category.query.all()
    return render_template('edit_post.html', post=post, categories=categories)
@app.route("/delete_post/<int:post_id>", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)

    if not post.can_delete():
        flash('No tienes permiso para eliminar esta publicación.', 'danger')
        return redirect(url_for('home'))

    # Eliminar comentarios asociados a la publicación
    comments = Comment.query.filter_by(post_id=post_id).all()
    for comment in comments:
        db.session.delete(comment)

    db.session.delete(post)
    db.session.commit()
    flash('Publicación eliminada correctamente.', 'success')
    return redirect(url_for('home'))


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("Tablas creadas en la base de datos")
    app.run(debug=True)
