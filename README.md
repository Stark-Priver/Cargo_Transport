# USSD-based Crop Transport Service with Admin Dashboard

This project provides a USSD (Unstructured Supplementary Service Data) interface for users to request transportation services for their crops. It also includes a backend API for an admin web dashboard to manage and track these transport orders. The application is built with Flask (Python) and uses a MySQL database for data storage.

## Features

*   **USSD Interface:**
    *   Request crop transportation by specifying crop type, quantity, pickup location, and destination.
    *   Track the status of an existing transport order using a tracking number.
    *   View contact information for the service.
*   **Backend API for Admin Dashboard:**
    *   `GET /api/orders`: Retrieve all transport orders.
    *   `PUT /api/orders/<track_number>/status`: Update the status of a specific order.
*   **Database:**
    *   Uses MySQL to store order information.
    *   Automatically creates necessary tables (`orders`, `transporters`, `locations`, `crops`, `system_settings`) on application startup if they don't exist.
    *   Manages relationships between orders, crops, locations, and transporters using foreign keys.

## Database Schema Details

The application uses the following tables:

*   **`orders`**: Stores details of each transport order.
    *   `track_number` (VARCHAR, PK): Unique tracking number.
    *   `phone_number` (VARCHAR): Customer's phone number.
    *   `crop_id` (INT, FK to `crops`): ID of the crop being transported.
    *   `quantity` (INT): Number of bags/units.
    *   `pickup_location_id` (INT, FK to `locations`): ID of the pickup location.
    *   `destination_location_id` (INT, FK to `locations`): ID of the destination location.
    *   `transporter_id` (INT, FK to `transporters`): ID of the assigned transporter.
    *   `status` (VARCHAR): Current status of the order (e.g., "Ombi limepokelewa", "Mizigo iko njiani").
    *   `created_at` (DATETIME): Timestamp of order creation.
    *   `status_updated_at` (DATETIME): Timestamp of last status update.
    *   (Older denormalized fields like `crop`, `pickup_location`, `transporter_name` are temporarily kept for backward compatibility during transition).

*   **`transporters`**: Manages transporter information.
    *   `id` (INT, PK, Auto-Increment)
    *   `name` (VARCHAR)
    *   `phone` (VARCHAR, Unique)
    *   `rating` (VARCHAR)
    *   `vehicle_details` (TEXT)
    *   `notes` (TEXT)
    *   `created_at`, `updated_at` (DATETIME)

*   **`locations`**: Manages pickup and destination locations.
    *   `id` (INT, PK, Auto-Increment)
    *   `name` (VARCHAR)
    *   `type` (ENUM('pickup', 'destination', 'both'))
    *   `region` (VARCHAR)
    *   `is_active` (BOOLEAN)
    *   `created_at`, `updated_at` (DATETIME)
    *   Unique constraint on (`name`, `type`).

*   **`crops`**: Manages types of crops available for transport.
    *   `id` (INT, PK, Auto-Increment)
    *   `name` (VARCHAR, Unique)
    *   `description` (TEXT)
    *   `is_active` (BOOLEAN)
    *   `created_at`, `updated_at` (DATETIME)

*   **`system_settings`**: Stores system-wide configuration parameters.
    *   `setting_key` (VARCHAR, PK)
    *   `setting_value` (TEXT)
    *   `description` (TEXT)
    *   `updated_at` (DATETIME)

## Project Structure

```
.
├── app.py            # Main Flask application with USSD logic and Admin APIs
├── cargoweb/         # Placeholder for the Admin Web Dashboard frontend (React/TS)
├── README.md         # This file
└── requirements.txt  # (Will be generated if not present) Python dependencies
```

## Prerequisites

*   Python 3.8+
*   Flask
*   mysql-connector-python
*   A running MySQL Server instance
## Setup and Installation

1.  **Clone the Repository:**
    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```

2.  **Create a Virtual Environment (recommended):**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install Dependencies:**
    It's good practice to have a `requirements.txt` file. If one doesn't exist, you can create it after installing packages manually:
    ```bash
    pip install Flask mysql-connector-python
    # pip freeze > requirements.txt # To generate requirements.txt
    ```
    If a `requirements.txt` is provided:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables:**
    The application uses environment variables for configuration. Create a `.env` file in the project root or set these variables in your environment:

    ```env
    # Flask Configuration
    SECRET_KEY='your_very_secret_flask_key_here' # Change this!
    FLASK_ENV='development' # or 'production'
    # FLASK_APP='app.py' # Usually not needed if named app.py or wsgi.py

    # MySQL Database Configuration
    MYSQL_HOST='localhost'        # Your MySQL host
    MYSQL_USER='your_mysql_user'  # Your MySQL username
    MYSQL_PASSWORD='your_mysql_password' # Your MySQL password
    MYSQL_DB='transport_db'       # The database name to use/create
    MYSQL_PORT='3306'             # Your MySQL port (default is 3306)
    ```
    **Note:** Ensure the MySQL database (`transport_db` or your chosen name) exists on your MySQL server. The application will create the `orders` table within this database if it doesn't exist.

5.  **Database Setup:**
    *   Ensure your MySQL server is running.
    *   Create the database specified in `MYSQL_DB` if it doesn't already exist.
        ```sql
        CREATE DATABASE IF NOT EXISTS transport_db; -- Or your chosen DB name
        ```
    *   The `orders` table will be created automatically by the application on its first run if it's not found in the database.

6.  **Run the Flask Application:**
    ```bash
    flask run
    ```
    Or directly:
    ```bash
    python app.py
    ```
    The application will typically run on `http://127.0.0.1:5000/`.

## USSD Workflow

The USSD service is accessible via a callback URL, typically `http://your_domain_or_ip/`, which would be configured with a USSD provider like Africa's Talking.

1.  **Main Menu:** User dials the USSD code.
    *   `CON Karibu Huduma ya Usafirishaji wa Mazao`
        *   `1. Omba Usafiri` (Request Transport)
        *   `2. Fuatilia Ombi` (Track Order)
        *   `3. Mawasiliano` (Contact Info)
        *   `0. Toka` (Exit)

2.  **Omba Usafiri (Request Transport):**
    *   User selects crop type.
    *   User enters quantity (in bags).
    *   User selects pickup location from a predefined list.
    *   User selects destination location from a predefined list.
    *   Order is confirmed, a tracking number is generated, and transporter details are provided.
    *   `END UTHIBITISHO - OMBI LIMEPOKELEWA!...`

3.  **Fuatilia Ombi (Track Order):**
    *   User enters their tracking number.
    *   Order status and details are displayed.
    *   `END HALI YA OMBI: TRK...`

4.  **Mawasiliano (Contact Info):**
    *   Displays contact details for the service.
    *   `END MAWASILIANO YETU...`

## Admin Web Dashboard API Endpoints

These endpoints are intended to be used by the `cargoweb/` admin dashboard frontend.

### Order Management
*   #### Get All Orders (`GET /api/orders`)
    *   **Description:** Retrieves a list of all transport orders, joined with crop, location, and transporter details. Sorted by creation date descending.
    *   **Response:** `200 OK` with a JSON array of order objects. Each order object includes:
        *   `track_number`, `phone_number`, `quantity`, `status`, `created_at`, `status_updated_at`
        *   `crop_details`: { `id`, `name` } (or old `crop` name if `crop_id` is null)
        *   `pickup_location_details`: { `id`, `name` } (or old `pickup_location` name)
        *   `destination_location_details`: { `id`, `name` } (or old `destination_location` name)
        *   `transporter_details`: { `id`, `name`, `phone`, `rating` } (or old transporter fields)
*   #### Update Order Status (`PUT /api/orders/<string:track_number>/status`)
    *   **Description:** Updates the status of a specific order.
    *   **Request Body (JSON):** `{ "status": "New Status String" }`
    *   **Response:** `200 OK` with the updated order object (JSON, including joined details as above). `400`, `404`, `500` for errors.

### Transporter Management (`/api/transporters`)
*   #### Create Transporter (`POST /`)
    *   **Request Body (JSON):** `{ "name": "...", "phone": "...", "rating": "...", "vehicle_details": "...", "notes": "..." }` (name and phone required)
    *   **Response:** `201 Created` with `{ "message": "Transporter created successfully", "id": <new_id> }`. `400`, `409` (duplicate phone), `500` for errors.
*   #### Get All Transporters (`GET /`)
    *   **Response:** `200 OK` with a JSON array of transporter objects.
*   #### Get Transporter by ID (`GET /<int:transporter_id>`)
    *   **Response:** `200 OK` with the transporter object. `404` if not found.
*   #### Update Transporter (`PUT /<int:transporter_id>`)
    *   **Request Body (JSON):** `{ "name": "...", "phone": "...", ... }` (any fields to update)
    *   **Response:** `200 OK` with `{ "message": "Transporter updated successfully" }`. `400`, `404`, `409` (duplicate phone), `500` for errors.
*   #### Delete Transporter (`DELETE /<int:transporter_id>`)
    *   **Response:** `200 OK` with `{ "message": "Transporter deleted successfully" }`. `404`, `409` (if referenced in orders and not handled by `ON DELETE SET NULL`), `500` for errors.

### Location Management (`/api/locations`)
*   #### Create Location (`POST /`)
    *   **Request Body (JSON):** `{ "name": "...", "type": "pickup|destination|both", "region": "...", "is_active": true|false }` (name required, type defaults to 'both', is_active to true)
    *   **Response:** `201 Created` with `{ "message": "Location created successfully", "id": <new_id> }`. `400`, `409` (duplicate name/type), `500` for errors.
*   #### Get All Locations (`GET /`)
    *   **Query Parameters (Optional):** `?type=pickup|destination|both` (Filters by type; 'pickup' includes 'pickup' and 'both', 'destination' includes 'destination' and 'both')
    *   **Response:** `200 OK` with a JSON array of location objects.
*   #### Get Location by ID (`GET /<int:location_id>`)
    *   **Response:** `200 OK` with the location object. `404` if not found.
*   #### Update Location (`PUT /<int:location_id>`)
    *   **Request Body (JSON):** `{ "name": "...", "type": "...", ... }` (any fields to update)
    *   **Response:** `200 OK` with `{ "message": "Location updated successfully" }`. `400`, `404`, `409` (duplicate name/type), `500` for errors.
*   #### Delete Location (`DELETE /<int:location_id>`)
    *   **Response:** `200 OK` with `{ "message": "Location deleted successfully" }`. `404`, `409` (if referenced in orders), `500` for errors.

### Crop Management (`/api/crops`)
*   #### Create Crop (`POST /`)
    *   **Request Body (JSON):** `{ "name": "...", "description": "...", "is_active": true|false }` (name required, is_active defaults to true)
    *   **Response:** `201 Created` with `{ "message": "Crop created successfully", "id": <new_id> }`. `400`, `409` (duplicate name), `500` for errors.
*   #### Get All Crops (`GET /`)
    *   **Query Parameters (Optional):** `?active=true|false`
    *   **Response:** `200 OK` with a JSON array of crop objects.
*   #### Get Crop by ID (`GET /<int:crop_id>`)
    *   **Response:** `200 OK` with the crop object. `404` if not found.
*   #### Update Crop (`PUT /<int:crop_id>`)
    *   **Request Body (JSON):** `{ "name": "...", "description": "...", ... }` (any fields to update)
    *   **Response:** `200 OK` with `{ "message": "Crop updated successfully" }`. `400`, `404`, `409` (duplicate name), `500` for errors.
*   #### Delete Crop (`DELETE /<int:crop_id>`)
    *   **Response:** `200 OK` with `{ "message": "Crop deleted successfully" }`. `404`, `409` (if referenced in orders), `500` for errors.

### System Settings Management (`/api/system-settings`)
*   #### Get All System Settings (`GET /`)
    *   **Response:** `200 OK` with a JSON array of system setting objects (`{setting_key, setting_value, description, updated_at}`).
*   #### Get System Setting by Key (`GET /<string:setting_key>`)
    *   **Response:** `200 OK` with the system setting object. `404` if not found.
*   #### Create/Update System Setting (`PUT /<string:setting_key>`)
    *   **Request Body (JSON):** `{ "setting_value": "...", "description": "..." }` (setting_value required)
    *   **Response:** `200 OK` or `201 Created` with a success message. `400`, `500` for errors.

### Reporting Endpoints
*   #### Get Orders Summary (`GET /api/reports/orders-summary`)
    *   **Description:** Returns a summary of orders, including total orders and counts by status.
    *   **Response:** `200 OK` with JSON: `{ "total_orders": <count>, "orders_by_status": [ { "status": "...", "count": <num> }, ... ] }`
*   #### Get Orders Over Time (`GET /api/reports/orders-over-time`)
    *   **Description:** Returns order counts grouped by creation date.
    *   **Response:** `200 OK` with JSON array: `[ { "order_date": "YYYY-MM-DD", "count": <num> }, ... ]`

## Deployment (Example for cPanel)

The `app.py` is written to be generally compatible with environments like cPanel that use Passenger or similar WSGI servers.

1.  Upload your project files to your hosting account.
2.  Create a Python application through the cPanel interface.
    *   Set the Application Startup File to `passenger_wsgi.py` (or as required by your host).
    *   Set the Application Entry point to `app` (if `passenger_wsgi.py` imports `app` from `app.py`).
    *   Example `passenger_wsgi.py`:
        ```python
        import os
        import sys

        # Add the project directory to Python's path
        sys.path.insert(0, os.path.dirname(__file__))

        # Import the Flask app instance
        from app import app as application
        ```
3.  Install dependencies into the virtual environment created by cPanel for your application.
4.  Set up environment variables through the cPanel interface (for database credentials, `SECRET_KEY`, etc.).
5.  Ensure your MySQL database is set up and accessible with the provided credentials.

## Future Enhancements

*   User authentication for admin APIs.
*   More detailed status options and history.
*   Integration with a payment gateway.
*   SMS notifications for order updates.
*   Full implementation of the `cargoweb/` admin frontend.
