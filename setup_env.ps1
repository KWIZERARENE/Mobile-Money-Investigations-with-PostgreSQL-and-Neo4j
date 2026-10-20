# Virtual Environment Setup Script
if (-not (Test-Path -Path ".venv")) {
    python -m venv .venv
}

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Install requirements
pip install -r requirements/requirements.txt

# Verify installations
pip list | Select-String -Pattern "psycopg|neo4j|numpy|matplotlib"
