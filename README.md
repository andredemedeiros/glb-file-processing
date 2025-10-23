---

## 💻 Running on Windows

### 🪟 1. Temporarily allow script execution

```powershell
Set-ExecutionPolicy Unrestricted -Scope Process
```

> ⚠️ This command is only necessary **if PowerShell blocks the activation** of your virtual environment.

---

### 🐍 2. Activate the virtual environment

```powershell
.\.venv\Scripts\activate
```

---

### 📦 3. Install dependencies

```bash
pip install -r requirements.txt
```

> If the `requirements.txt` file doesn’t exist yet, install manually and generate it:

```bash
pip install package1 package2 ...
pip freeze > requirements.txt
```

---

### 🚀 4. Run the project

```bash
python main.py
```

---

## 🧠 Tips

* Check if Python and `pip` are properly configured:

  ```bash
  python --version
  pip --version
  ```
* To deactivate the virtual environment:

  ```bash
  deactivate
  ```

---