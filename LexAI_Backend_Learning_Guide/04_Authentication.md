# 04. Authentication

Handled by `Flask-Login` and `Flask-Bcrypt`. Passwords are mathematically hashed so they are never stored in plain text. Routes are protected using `@login_required`.