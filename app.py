import os
import io
import hashlib
from flask import Flask, request, jsonify, send_file, render_template, session, redirect, url_for
from flask_bcrypt import Bcrypt
from flask_session import Session # type: ignore
from Crypto.Cipher import AES, DES
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Random import get_random_bytes


# Flask App Initialization
app = Flask(__name__)
bcrypt = Bcrypt(app)

# Configuration
app.secret_key = 'secret_key'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['UPLOAD_FOLDER'] = './uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
Session(app)

# AES Helper Class
class AESCipher:
    def __init__(self, key):
        self.key = hashlib.sha256(key.encode()).digest()

    def encrypt(self, data):
        cipher = AES.new(self.key, AES.MODE_EAX)
        ciphertext, tag = cipher.encrypt_and_digest(data)
        return cipher.nonce + tag + ciphertext

    def decrypt(self, data):
        nonce = data[:16]
        tag = data[16:32]
        ciphertext = data[32:]
        cipher = AES.new(self.key, AES.MODE_EAX, nonce=nonce)
        return cipher.decrypt_and_verify(ciphertext, tag)

class DESCipher:
    def __init__(self, key):
        self.key = hashlib.md5(key.encode()).digest()[:8]  # DES key must be 8 bytes

    def encrypt(self, data):
        cipher = DES.new(self.key, DES.MODE_EAX)
        ciphertext, tag = cipher.encrypt_and_digest(data)
        return cipher.nonce + tag + ciphertext

    def decrypt(self, data):
        nonce = data[:8]
        tag = data[8:24]
        ciphertext = data[24:]
        cipher = DES.new(self.key, DES.MODE_EAX, nonce=nonce)
        return cipher.decrypt_and_verify(ciphertext, tag)

class RSACipher:
    def __init__(self):
        # Generate RSA key pair (2048 bits)
        self.key = RSA.generate(2048)
        self.public_key = self.key.publickey()
        self.cipher_rsa_encrypt = PKCS1_OAEP.new(self.public_key)
        self.cipher_rsa_decrypt = PKCS1_OAEP.new(self.key)

    def encrypt(self, data):
        # Generate a random AES key
        aes_key = get_random_bytes(16)  # 16 bytes for AES-128
        cipher_aes = AES.new(aes_key, AES.MODE_EAX)
        ciphertext, tag = cipher_aes.encrypt_and_digest(data)

        # Encrypt the AES key with RSA
        encrypted_aes_key = self.cipher_rsa_encrypt.encrypt(aes_key)

        # Combine encrypted AES key, nonce, tag, and ciphertext
        return encrypted_aes_key + cipher_aes.nonce + tag + ciphertext

    def decrypt(self, data):
        # Extract RSA-encrypted AES key and AES-encrypted data
        encrypted_aes_key = data[:256]  # 256 bytes for RSA (2048 bits)
        nonce = data[256:272]           # AES nonce (16 bytes)
        tag = data[272:288]             # AES tag (16 bytes)
        ciphertext = data[288:]         # Remaining data is AES ciphertext

        # Decrypt the AES key with RSA
        aes_key = self.cipher_rsa_decrypt.decrypt(encrypted_aes_key)

        # Decrypt the AES-encrypted data
        cipher_aes = AES.new(aes_key, AES.MODE_EAX, nonce=nonce)
        return cipher_aes.decrypt_and_verify(ciphertext, tag)


# User Storage
users = {}

# Routes
@app.route('/')
def home():
    if 'username' in session:
        return render_template('front.html', username=session['username'])
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
        if username in users:
            return "User already exists!", 400
        users[username] = password
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and bcrypt.check_password_hash(users[username], password):
            session['username'] = username
            return redirect(url_for('home'))
        return "Invalid credentials!", 401
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/encrypt', methods=['POST'])
def encrypt_file():
    if 'username' not in session:
        return redirect(url_for('login'))

    file = request.files['file']
    encryption_type = request.form['encryption_type']
    key = request.form.get('key', '')  # RSA doesn't need a user-provided key
    cipher = None

    try:
        data = file.read()

        if encryption_type == 'AES':
            cipher = AESCipher(key)
            encrypted_data = cipher.encrypt(data)
            type_spec = 'AES-'
        elif encryption_type == 'DES':
            cipher = DESCipher(key)
            encrypted_data = cipher.encrypt(data)
            type_spec = 'DES-'
        elif encryption_type == 'RSA':
            cipher = RSACipher()
            session['rsa_private_key'] = cipher.key.export_key().decode()  # Save private key for decryption
            encrypted_data = cipher.encrypt(data)
            type_spec = 'RSA-'

        return send_file(
            io.BytesIO(encrypted_data),
            as_attachment=True,
            download_name= type_spec + file.filename + '.enc',
            mimetype='application/octet-stream'
        )
    except Exception as e:
        return f"Encryption failed: {str(e)}", 500


@app.route('/decrypt', methods=['POST'])
def decrypt_file():
    if 'username' not in session:
        return redirect(url_for('login'))

    file = request.files['file']
    encryption_type = request.form['encryption_type']
    key = request.form.get('key', '')
    cipher = None

    try:
        data = file.read()

        if encryption_type == 'AES':
            cipher = AESCipher(key)
            decrypted_data = cipher.decrypt(data)
        elif encryption_type == 'DES':
            cipher = DESCipher(key)
            decrypted_data = cipher.decrypt(data)
        elif encryption_type == 'RSA':
            private_key_data = session.get('rsa_private_key')
            if not private_key_data:
                return "Decryption failed: RSA private key not found", 400

            private_key = RSA.import_key(private_key_data)
            cipher = RSACipher()
            cipher.key = private_key
            decrypted_data = cipher.decrypt(data)

        original_filename = file.filename.rsplit('.enc', 1)[0]
        return send_file(
            io.BytesIO(decrypted_data),
            as_attachment=True,
            download_name=original_filename,
            mimetype='application/octet-stream'
        )
    except Exception as e:
        return f"Decryption failed: {str(e)}", 500


if __name__ == '__main__':
    app.run(debug=True)
