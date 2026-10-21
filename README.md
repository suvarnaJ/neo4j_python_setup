
# Python + Neo4j Setup

A starter project demonstrating a Python connection to Neo4j Aura.

## Prerequisites
- Python 3
- Git
- Visual Studio Code
- Neo4j Aura database

## Setup on Windows

1. Clone the repository and enter its directory.
2. Create and activate a virtual environment:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. Install dependencies:

   ```powershell
   python -m pip install -r requirements.txt
   ```

4. Copy `.env.example` to `.env`.
5. Add your actual Neo4j Aura credentials to `.env`.
6. Run the connectivity test:

   ```powershell
   python src/main.py
   ```

## Expected result

The program verifies Neo4j connectivity and executes a
read-only test query.

## Security

Never commit `.env`, passwords, or other credentials.
