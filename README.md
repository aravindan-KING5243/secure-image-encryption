# Secure Image Encryption Project

## Introduction

With the rise of digital communication, ensuring the confidentiality of sensitive data, such as images, has become critical. The **Secure Image Encryption Project** leverages advanced cryptographic techniques to secure image files during storage and transmission. This project demonstrates the use of symmetric and asymmetric encryption methods, creating a robust system for user authentication, file encryption, and decryption.

---

## Objectives

1. **Secure Image Encryption and Decryption**: Implement advanced cryptographic algorithms to encrypt and decrypt image files.
2. **User Authentication**: Provide a secure login and registration system to restrict access to authorized users.
3. **File Handling in Browser**: Allow users to upload, encrypt, decrypt, and download files seamlessly.
4. **In-Memory File Processing**: Avoid server-side file persistence, improving security and performance.

---

## Key Features

### Encryption Techniques
- **AES (Advanced Encryption Standard)**: A symmetric encryption algorithm for fast and secure image encryption.
- **DES (Data Encryption Standard)**: Another symmetric encryption algorithm for compatibility and demonstration purposes.
- **RSA (Rivest-Shamir-Adleman)**: An asymmetric encryption algorithm used for secure key exchange and user authentication.

### User Management
- **Registration**: Allows users to create accounts with hashed passwords (using bcrypt).
- **Login**: Validates user credentials for secure access to encryption and decryption functionalities.
- **Session Management**: Ensures that only authenticated users can access file operations.

### File Handling
- **Upload**: Users can upload image files via a web interface.
- **Encrypt**: Files are encrypted in memory and immediately served for download as `.enc` files.
- **Decrypt**: Encrypted files are decrypted in memory and served for download.

---

## System Architecture

### Backend
- **Framework**: Flask
- **Libraries**:
  - `pycryptodome`: For cryptographic operations (AES, DES, RSA).
  - `bcrypt`: For password hashing.
  - `io`: For in-memory file handling.
- **Endpoints**:
  - `/register`: Registers a new user.
  - `/login`: Authenticates users.
  - `/encrypt`: Encrypts uploaded files.
  - `/decrypt`: Decrypts uploaded files.

### Frontend
- **HTML**: Provides a simple interface for file upload and download.
- **JavaScript**: Handles form submission and responses from the server.

---

## Implementation Details

### Cryptographic Operations
- **AES Encryption/Decryption**:
  - Uses a 256-bit key derived from a user-provided password.
  - Operates in EAX mode for authenticated encryption.
- **RSA Key Management**:
  - A 2048-bit RSA key pair is generated and stored at the server startup.
  - Public key is used for encrypting data or keys, while the private key decrypts them.

### File Handling
- **Upload and Processing**:
  - Files are uploaded through the web interface and read directly into memory.
  - Encrypted or decrypted data is returned to the user as a downloadable file.
- **In-Memory Processing**:
  - `io.BytesIO` is used to avoid saving files to the disk, enhancing security and performance.

### User Authentication
- Passwords are hashed using bcrypt before storage.
- Sessions are managed to restrict access to authorized users.

---

## User Interface

The web interface is minimalistic and user-friendly, featuring:
1. **File Upload**: Input fields for file selection and encryption key.
2. **Action Buttons**: Options to encrypt or decrypt the uploaded file.
3. **File Download**: Automatic prompt to download the processed file.

---

## Project Workflow

1. **User Registration**:
   - User submits a username and password.
   - Password is hashed and stored securely.

2. **Login**:
   - User provides credentials.
   - If valid, a session is created.

3. **File Encryption**:
   - User uploads an image and provides a key.
   - The image is encrypted using AES and served as a `.enc` file for download.

4. **File Decryption**:
   - User uploads an encrypted file and provides a key.
   - The file is decrypted and served for download.

---

## Challenges and Solutions

### Challenge 1: Secure Key Management
**Solution**: Used a hybrid encryption approach where AES keys are used for file encryption and RSA keys for secure key exchange.

### Challenge 2: Avoid File Persistence
**Solution**: Utilized Python's `io.BytesIO` for in-memory file processing.

### Challenge 3: User Authentication
**Solution**: Implemented bcrypt for password hashing and session-based authentication.

---

## Future Enhancements

1. **Desktop GUI Integration**:
   - Replace the web interface with a user-friendly desktop application using PyQt or Tkinter.

2. **Multi-Algorithm Support**:
   - Extend the system to allow users to choose encryption algorithms (AES, DES, RSA).

3. **Integrity Verification**:
   - Add HMAC (Hash-based Message Authentication Code) to ensure file integrity.

4. **Cloud Integration**:
   - Securely integrate cloud storage (e.g., AWS S3, Google Drive) for encrypted file uploads and downloads.

---

## Installation and Usage

### Prerequisites
- Python 3.7 or later
- Pip (Python package installer)

### Steps

```bash
# Clone the repository
git clone https://github.com/your-username/secure-image-encryption.git
cd secure-image-encryption

# Set up a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py

# Access the application
# Open your browser and navigate to http://127.0.0.1:5000
