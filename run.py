#!/usr/bin/env python3

import sqlalchemy as sa
import sqlalchemy.orm as so
from app import app, db
from app.models import User, Post

@app.shell_context_processor
def make_shell_context():
# # --- DEBUGGING-AUSGABEN HIER ---
#     print(f"DEBUG: 'sa' exists inside make_shell_context: {sa is not None}")
#     print(f"DEBUG: 'so' exists inside make_shell_context: {so is not None}")
#     # Falls das immer noch einen NameError wirft, ist SQLAlchemy selbst das Problem.
#     # Versuchen wir, auf die Attribute zuzugreifen, um sicherzustellen, dass es Objekte sind.
#     try:
#         print(f"DEBUG: sa version: {sa.__version__}")
#         print(f"DEBUG: so exists: {'orm' in dir(sa)}")
#     except Exception as e:
#         print(f"DEBUG: Error accessing sqlalchemy attributes: {e}")
#     # --- ENDE DEBUGGING ---
    return {'sa': sa, 'so': so, 'db': db, 'User': User, 'Post': Post}

if __name__ == '__main__':
    app.run()
