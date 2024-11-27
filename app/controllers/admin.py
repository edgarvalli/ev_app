import hashlib
from functools import wraps
from app.tools.evschema.database import Database
from flask import Blueprint, request, render_template, redirect, session, current_app

admin_login_app = Blueprint('admin login', __name__, url_prefix='/admin')

def handle_request_error(message):
    return redirect('/admin/login?error=' + message, code=302)

def middleware_auth(func):
    @wraps(func)
    def auth(*args, **kvargs):
        if session.get('is_allowed', None) is None:
            return redirect('/admin/login')
        return func(*args, **kvargs)

    return auth

@admin_login_app.route('/')
@middleware_auth
def admin_index():
    return 'Admi index'

@admin_login_app.route('/login')
def admin_login():
    if session.get('is_allowed', None) is None:
        return render_template('login_admin.html')
    else:
        return redirect('/admin')

@admin_login_app.route('/singin', methods=['POST'])
def login_singin():
    
    username = request.form.get('username', None)
    password:str = request.form.get('password', None)
    
    # Se revisa los campos obligatorios
    
    if username is None:
        return handle_request_error('Debe de enviar el valor Usuario')
    if password is None:
        return handle_request_error('Debe de enviar el valor Contraseña')
    db = Database()
    db.config.parse_from_dict(current_app.config)
    # Se verifica en la base de datos
    query = f"SELECT id,username,password,fullname,email,phone FROM users WHERE username='{username}' AND active=1"
    user = db.query(query=query).fetchone()
    
    if user is None:
        return handle_request_error(f'El usuario "{username}" no existe')
    
    userpass = user.get('password', None)
    password = hashlib.sha1(password.encode()).hexdigest()
    
    if password != userpass:
        return handle_request_error('La contraseña no es correcta')
    
    
    session['user_fullname'] = user.get('fullname', '')
    session['user_email'] = user.get('email', '')
    session['user_phone'] = user.get('phone', '')
    session['is_allowed'] = True
    
    if user.get('is_admin', 0) == 1:
        session['is_admin'] = True
    
    
    return redirect('/')

@admin_login_app.route('/singout')
def admin_singout():
    session.clear()
    return redirect('/admin/login')