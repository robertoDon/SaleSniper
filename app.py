from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'scr')))

from services.auth import carregar_usuarios, salvar_usuario, autenticar
from components.dashboard import get_dashboard_data
from components.segmentacao import get_segmentacao_data
from components.metas_funil import get_metas_funil_data
from components.churn import get_churn_data
from components.valuation import get_valuation_data
from components.tamsamsom import get_tamsamsom_data

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change to a secure key

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, username):
        self.id = username

@login_manager.user_loader
def load_user(user_id):
    usuarios = carregar_usuarios()
    if user_id in usuarios:
        return User(user_id)
    return None

@app.route('/')
@login_required
def index():
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        senha = request.form['senha']
        usuarios = carregar_usuarios()
        if autenticar(usuario, senha, usuarios):
            user = User(usuario)
            login_user(user)
            return redirect(url_for('index'))
        flash('Usuário ou senha inválidos.')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    data = get_dashboard_data()
    return render_template('dashboard.html', data=data, user=current_user.id)

@app.route('/segmentacao')
@login_required
def segmentacao():
    data = get_segmentacao_data()
    return render_template('segmentacao.html', data=data, user=current_user.id)

@app.route('/metas_funil')
@login_required
def metas_funil():
    data = get_metas_funil_data()
    return render_template('metas_funil.html', data=data, user=current_user.id)

@app.route('/churn')
@login_required
def churn():
    data = get_churn_data()
    return render_template('churn.html', data=data, user=current_user.id)

@app.route('/valuation')
@login_required
def valuation():
    data = get_valuation_data()
    return render_template('valuation.html', data=data, user=current_user.id)

@app.route('/tamsamsom')
@login_required
def tamsamsom():
    data = get_tamsamsom_data()
    return render_template('tamsamsom.html', data=data, user=current_user.id)

@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    if current_user.id != 'admin':
        return redirect(url_for('index'))
    usuarios = carregar_usuarios()
    if request.method == 'POST':
        novo_user = request.form['novo_user']
        nova_senha = request.form['nova_senha']
        if novo_user and nova_senha:
            salvar_usuario(novo_user, nova_senha)
            flash(f'Usuário {novo_user} salvo.')
            return redirect(url_for('admin'))
        flash('Preencha todos os campos.')
    return render_template('admin.html', usuarios=usuarios, user=current_user.id)

if __name__ == '__main__':
    app.run(debug=True)