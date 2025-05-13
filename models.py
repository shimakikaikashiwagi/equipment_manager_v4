from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

db = SQLAlchemy()

# Userモデル
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

    def set_password(self, password):
        """パスワードをハッシュ化して保存する"""
        self.password = generate_password_hash(password)

    def check_password(self, password):
        """入力されたパスワードが正しいか確認する"""
        return check_password_hash(self.password, password)


# ConstructionMachineモデル
class ConstructionMachine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)           # 機械名
    manufacturer = db.Column(db.String(100), nullable=True)     # メーカー名（任意）
    serial_number = db.Column(db.String(100), unique=True, nullable=False)  # シリアル番号（必須）
    location = db.Column(db.String(100), nullable=True)         # 場所（任意）
    is_active = db.Column(db.Boolean, default=True)             # 使用中かどうか
    image_path = db.Column(db.String(200), nullable=True)       # 画像ファイルパス（任意）

    def __repr__(self):
        return f'<ConstructionMachine {self.name}>'
