echo " Running Pedestrian Count Analysis"

echo "configure AWS"

aws configure

echo "Create virtual environment"
python3 -m venv .venv

echo "Creating infrastructure using terraform"

terraform init
terraform apply

echo "Activating Virtual environment"

source .venv/bin/activate

echo "Installing Requirements"
pip install -r requirements.txt

echo "Starting Processes"
python main.py