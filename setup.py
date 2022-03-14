from setuptools import setup

setup(name='webapp',
      version='1.0',
      description='Python Distribution Utilities',
      packages=['webapp'],
      install_requires=[
        "numpy",
        "flask_sqlalchemy",
        "flask_login",
        "flask",
        ]
      )
