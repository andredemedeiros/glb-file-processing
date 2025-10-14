Windows execution

Set-ExecutionPolicy Unrestricted -Scope Process

.\.venv\Scripts\activate

pip install ...

pip freeze > requirements.txt
