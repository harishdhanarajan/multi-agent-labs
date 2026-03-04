# Python Database & SFTP Utility Project

This project provides modular utilities in Python for:

- Connecting to a MySQL database with configurable parameters
- Performing basic arithmetic operations
- Flexible SFTP uploads/downloads using Paramiko with a configuration system
- Simple utility functions (greeting, string reverse)

The modules are designed to be reusable in Python scripts or be extended for more complex applications.

---

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [How to Use](#how-to-use)
  - [Database Connection](#database-connection)
  - [Arithmetic Calculator](#arithmetic-calculator)
  - [SFTP File Transfers](#sftp-file-transfers)
  - [Utility Functions](#utility-functions)
- [Module and Function Reference](#module-and-function-reference)
  - [app.py](#apppy)
  - [calculator.py](#calculatorpy)
  - [db_config.py](#db_configpy)
  - [sftp_config.py](#sftp_configpy)
  - [sftp_client.py](#sftp_clientpy)
  - [utility_functions.py](#utility_functionspy)
  - [utils.py](#utilspy)

---

## Features

- **MySQL Connection:** Establish and manage database connections with error handling.
- **Configurable:** Load DB and SFTP connection settings from environment variables or provide explicitly.
- **Calculator:** Perform addition, subtraction, multiplication, and division (with error for division by zero).
- **SFTP Support:** Upload, download, and list files from an SFTP server using key or password authentication.
- **Utility Functions:** Greet users and reverse strings for demonstration or extension.
- **Tested:** Unit tests included for core modules.

---

## Requirements

- Python 3.7+
- [`mysql-connector-python`](https://pypi.org/project/mysql-connector-python/)
- [`paramiko`](https://pypi.org/project/paramiko/)

Install dependencies with:

