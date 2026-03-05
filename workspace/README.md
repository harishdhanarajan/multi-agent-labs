# Python Database & SFTP Utility Project

This project provides modular Python utilities for:

- Connecting to a MySQL database with configurable parameters
- Performing basic arithmetic operations (addition, subtraction, multiplication, division)
- SFTP file uploads/downloads using Paramiko with a configuration system
- Common utility functions (greeting, string reversal, etc.)

All modules are designed to be reusable in different Python scripts or as extensible components for larger applications.

---

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [How to Use](#how-to-use)
  - [A. Database Connection](#a-database-connection)
  - [B. Arithmetic Calculator](#b-arithmetic-calculator)
  - [C. SFTP File Transfers](#c-sftp-file-transfers)
  - [D. Utility Functions](#d-utility-functions)
- [Module and Function Reference](#module-and-function-reference)
  - [calculator.py](#calculatorpy)
  - [add_numbers.py](#add_numberspy)
  - [db_config.py](#db_configpy)
  - [app.py](#apppy)
  - [sftp_config.py](#sftp_configpy)
  - [sftp_client.py](#sftp_clientpy)
  - [utility_functions.py](#utility_functionspy)
  - [utils.py](#utilspy)

---

## Features

- **MySQL Connection:** Establish and manage MySQL database connections with error handling. Configurable via environment variables or code.
- **Configurable:** DB/SFTP connection settings are controlled by environment or config objects.
- **Calculator:** Addition, subtraction, multiplication, and division with user-friendly output.
- **SFTP Support:** Upload, download, and list files from an SFTP server (key-based or password authentication).
- **Utility Functions:** Greeting messages and string reversal demonstration functions.
- **Unit Tested:** Core modules are covered by tests.

---

## Requirements

- Python 3.7+
- [`mysql-connector-python`](https://pypi.org/project/mysql-connector-python/)
- [`paramiko`](https://pypi.org/project/paramiko/)

Install dependencies with:

