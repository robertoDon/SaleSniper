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
from components.valuation_web import get_valuation_data
from components.tamsamsom_web import get_tamsamsom_data

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

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    data = None
    if request.method == 'POST':
        arquivo = request.files.get('file')
        if arquivo and arquivo.filename:
            data = get_dashboard_data(arquivo)
        else:
            data = {'error': 'Nenhum arquivo enviado. Por favor, envie um arquivo Excel (.xlsx).'}
    return render_template('dashboard.html', data=data, user=current_user.id)

@app.route('/segmentacao', methods=['GET', 'POST'])
@login_required
def segmentacao():
    data = None
    if request.method == 'POST':
        arquivo = request.files.get('file')
        campo = request.form.get('campo', 'ltv')
        tipo = request.form.get('tipo', '80/20')
        # Percentuais opcionais (apenas para 80/20 ou customizadas)
        percentuais = None
        if tipo == '80/20':
            pct = request.form.get('percentual', '')
            if pct.isdigit():
                percentuais = int(pct)
        elif tipo == '20/30/30/20':
            # Pode receber 4 valores separados por vírgula
            tiers = request.form.get('tiers', '')
            if tiers:
                try:
                    percentuais = [int(x.strip()) for x in tiers.split(',') if x.strip()]
                    if len(percentuais) != 4:
                        percentuais = None
                except ValueError:
                    percentuais = None
        if arquivo and arquivo.filename:
            data = get_segmentacao_data(arquivo, campo, tipo, percentuais)
        else:
            data = {'error': 'Nenhum arquivo enviado. Por favor, envie um arquivo Excel (.xlsx).'}
    return render_template('segmentacao.html', data=data, user=current_user.id)

@app.route('/metas_funil', methods=['GET', 'POST'])
@login_required
def metas_funil():
    data = None
    if request.method == 'POST':
        segmento = request.form.get('segmento', 'Software por Recorrência')
        tipo_obj = request.form.get('tipo_obj', 'Clientes')
        val_obj_raw = request.form.get('val_obj', '0').replace(',', '.')
        ticket_medio_raw = request.form.get('ticket_medio', '0').replace(',', '.')
        n_vend_raw = request.form.get('n_vend', '1')

        try:
            val_obj = float(val_obj_raw)
        except ValueError:
            val_obj = 0.0
        try:
            ticket_medio = float(ticket_medio_raw)
        except ValueError:
            ticket_medio = 0.0
        try:
            n_vend = int(n_vend_raw)
        except ValueError:
            n_vend = 1

        data = get_metas_funil_data(segmento, tipo_obj, val_obj, ticket_medio, n_vend)
    return render_template('metas_funil.html', data=data, user=current_user.id)

@app.route('/churn', methods=['GET', 'POST'])
@login_required
def churn():
    data = None
    if request.method == 'POST':
        arquivo = request.files.get('file')
        if arquivo and arquivo.filename:
            data = get_churn_data(arquivo)
        else:
            data = {'error': 'Nenhum arquivo enviado. Por favor, envie um arquivo CSV.'}
    return render_template('churn.html', data=data, user=current_user.id)

@app.route('/valuation', methods=['GET', 'POST'])
@login_required
def valuation():
    data = None
    if request.method == 'POST':
        data = get_valuation_data(request.form)
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