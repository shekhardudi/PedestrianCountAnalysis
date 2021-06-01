echo " Running Pedestrian Count Analysis"
echo "Creating infrastructure using terraform"

terraform init
terraform apply

echo "Starting Processes"
python main.py

