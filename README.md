# Rap-steam Protocol

Rap-steam Protocol is a Django-based application designed to manage school and address data within an educational system. The application allows for importing school data from CSV files and later managing it through the Django admin panel. The project aims to simplify the processing and analysis of data related to educational institutions.

## Features

- **CSV Data Import:** The application allows importing school data from a CSV file using the `load_schools_from_csv` function.
- **School Management:** Users can manage school and address data through the Django admin panel.
- **Database:** The application uses an SQLite database to store school, address, and configuration data.
- **Extensibility:** The project is designed to easily add new features, such as support for new data types, generating reports, or integrating with external services.

## Installation

To run the project locally, follow these steps:

### Step 1: Clone the repository

```bash
git clone https://github.com/iAttaquer/Rap-steam-Protocol.git
cd Rap-steam-Protocol
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

The application will be available at: http://127.0.0.1:8000/.
