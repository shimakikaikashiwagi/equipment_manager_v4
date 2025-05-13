from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_migrate import Migrate
from models import db, ConstructionMachine, User  # models.pyからインポート
from flask import request, redirect, url_for

# Flaskアプリケーションのインスタンス作成
app = Flask(__name__)

# 設定
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///equipment.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "your_secret_key"

# DB初期化とMigrate
db.init_app(app)
migrate = Migrate(app, db)

# LoginManagerの設定
login_manager = LoginManager(app)
login_manager.login_view = "login"

# ログインユーザー取得
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ログイン処理
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('index'))
        flash('ログインに失敗しました')
    return render_template('login.html')

# トップページ
@app.route('/')
@login_required
def index():
    return render_template('index.html')

# ログアウト処理
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# 機材一覧ページ
@app.route('/machine_list')
@login_required
def machine_list():
    type_param = request.args.get('type')  # 'construction'など
    machines = []

    if type_param == 'construction':
        machines = ConstructionMachine.query.all()

    return render_template('machine_list.html', type=type_param, machines=machines)

# 建設機械の新規登録ページ
@app.route('/construction_machines/add', methods=['GET', 'POST'])
@login_required
def add_construction_machine():
    if request.method == 'POST':
        try:
            machine_type = request.form['machine_type']
            manufacturer = request.form['manufacturer']
            rental_number = request.form['rental_number']
            location = request.form['location']
        except KeyError as e:
            flash(f"リクエストデータに '{e.args[0]}' が見つかりません。")
            return redirect(url_for('add_construction_machine'))
        
        # その他の処理...
        new_machine = ConstructionMachine(
            name=machine_type,
            manufacturer=manufacturer,
            serial_number=rental_number,
            location=location,
            is_active=True
        )
        try:
            db.session.add(new_machine)
            db.session.commit()
            flash('建設機械を登録しました。')
            return redirect(url_for('machine_list', type='construction'))
        except Exception as e:
            db.session.rollback()
            flash(f'エラーが発生しました: {str(e)}')

    return render_template('add_construction_machine.html')

# 使用中状態の切り替え（ON/OFF）
@app.route('/machine/<int:machine_id>/toggle', methods=['POST'])
@login_required
def toggle_active(machine_id):
    machine = ConstructionMachine.query.get_or_404(machine_id)
    machine.is_active = not machine.is_active
    db.session.commit()
    flash('状態が変更されました。')
    return redirect(url_for('machine_list', type='construction'))

@app.route('/machine/<int:machine_id>/delete', methods=['POST'])
@login_required
def delete_machine(machine_id):
    machine = ConstructionMachine.query.get_or_404(machine_id)
    try:
        db.session.delete(machine)
        db.session.commit()
        flash('機械を削除しました。')
    except Exception as e:
        db.session.rollback()
        flash(f'削除中にエラーが発生しました: {str(e)}')
    return redirect(url_for('machine_list', type='construction'))

@app.route('/update_location/<int:machine_id>', methods=['POST'])
def update_location(machine_id):
    new_location = request.form.get('location')
    machine = ConstructionMachine.query.get(machine_id)
    if machine:
        machine.location = new_location
        db.session.commit()
        flash('場所が変更されました。')  # フラッシュメッセージ
    return redirect(url_for('machine_list', type='construction'))


# アプリケーション起動
if __name__ == '__main__':
    with app.app_context():  # アプリケーションコンテキストを使用
        db.create_all()  # テーブル作成
        if not User.query.filter_by(username='admin').first():
            user = User(username='admin')
            user.set_password('password')
            db.session.add(user)
            db.session.commit()

    app.run(debug=True)
