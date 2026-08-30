# Ride Request & Management System (Sprint 1)

# Setup & Local Installation:
Create an instance in EC2 AND OPEN Putty and Conduct the following steps:

•	To make space: sudo apt clean && sudo apt autoremove –y
•	Clone the app:  git clone https://github.com/adeshpillay-n12763144/Adesh_Github_Assignment.git

•	Username: adeshpillay-n12763144
•	Password: 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

•	Move into the folder: cd Adesh_Github_Assignment
•	Create an virtual env: python3 –m venv venv
•	Activate the env: source venv/bin/activate
•	MongoDB Services: sudo apt update sudo apt install -y mongodb sudo systemctl start mongodb
•	Install requirements and Gunicorn: pip install –r requirements.txt and pip install gunicorn
•	Launch app on port 80: sudo ./venv/bin/gunicorn – bind 0.0.0.0:80 app:app > app.log 2>$1 &



Architecture Summary:
Backend/frontend technologies: using python flask with basic html and css for stylying.

Database: MongoDB  managing users, rides, and logs collections.

Workflow: features implementated are for sprint 1 only which basic CRUD functions.

Known Limitations:
Real-time driver GPS tracking is planned for Sprint 2 and not included in v1.0.0.
Cancellation is currently restricted strictly to pending rides; refund processing is handled manually.
Have to install python and mongodb in the putty before HOSTING to EC2 instances.


Live Application:http://3.107.185.92/
