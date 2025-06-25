# Secure Password Manager

A modern, secure, and user-friendly password manager for Windows, built with Python and Tkinter (CustomTkinter). Store, generate, and manage your passwords with strong encryption and a beautiful dark-themed interface.

---

## Features

- **Strong Password Generation** (up to 20 characters, customizable character sets)
- **Encrypted Storage** (Fernet encryption, per-user isolation)
- **User Authentication** (bcrypt password hashing, admin login)
- **Search & Export** (search by title/name, export to CSV/JSON)
- **Modern Dark Theme** (particle animation, stylish buttons, responsive layout)
- **Password Visibility Toggle** (show/hide, copy to clipboard)
- **Error Handling & Visual Feedback** (success/error messages)
- **Fast Startup** (optimized EXE build with PyInstaller)

---

## Screenshots

> ![image](https://github.com/user-attachments/assets/33466753-5900-4337-ae6d-b33383cc85e5)
> ![image](https://github.com/user-attachments/assets/1c12f50c-372c-46bf-b220-88419f47f58f)


---

## Installation

### 1. Download the Installer
- Download the latest `SecurePasswordManager_Setup.exe` from [Releases](https://github.com/yourusername/yourrepo/releases).
- Run the installer and follow the prompts.

### 2. Or Build from Source
- Clone this repo:
  ```sh
  git clone https://github.com/mroneibs/Secure-Password-Manager.git
  cd Secure-Password-Manager
  ```
- Install Python 3.10+ and pip.
- Install dependencies:
  ```sh
  pip install -r requirements.txt
  ```
- Run the app:
  ```sh
  python password_manager_gui.py
  ```

---

## Building the EXE (for Windows)

1. Make sure all dependencies are installed:
   ```sh
   pip install -r requirements.txt
   pip install pyinstaller pillow pywin32-ctypes
   ```
2. Run the build script:
   ```sh
   build.bat
   ```
3. The EXE will be in `dist/Password Manager/`.

---

## Usage

- **First Run:** Set your admin password (default: `admin` / `admin123`).
- **Add Passwords:** Use the "Add New Password" button.
- **Change Admin Password:** Use the "Change Admin Password" button in the main screen.
- **Search/Export:** Use the search bar and export options.
- **Copy/Show Passwords:** Use the buttons next to each entry.

---

## Security Notes
- All passwords are encrypted with your admin password (Fernet/AES).
- Only the correct admin password can decrypt your vault.
- Passwords are never stored in plain text.
- If you forget your admin password, your data cannot be recovered (unless exported previously).

---

## License

This project is licensed under the MIT License. See [LICENSE.txt](LICENSE.txt) for details.


---

## Contributing
Pull requests and suggestions are welcome! Please open an issue first to discuss changes. 
