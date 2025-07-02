# USSD-based Crop Transport Service with Admin Dashboard

This project provides a USSD (Unstructured Supplementary Service Data) interface for users to request transportation services for their crops. It also includes a backend API and a React/TypeScript frontend for an admin web dashboard to manage and track these transport orders. The backend is built with Flask (Python) and uses a MySQL database for data storage.

## Features

*   **USSD Interface:**
    *   Request crop transportation by specifying crop type, quantity, pickup location, and destination (dynamically fetched from database).
    *   Track the status of an existing transport order using a tracking number.
    *   View contact information for the service.
*   **Backend API for Admin Dashboard:**
    *   Comprehensive CRUD APIs for Orders, Transporters, Locations, Crops, and System Settings.
    *   Reporting APIs for order summaries and orders over time.
*   **Admin Web Dashboard (`cargoweb/`):**
    *   (Currently includes) UI for displaying reports (Orders Summary, Orders Over Time).
    *   (Future scope) Full UI for managing all entities and system configurations.
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
├── cargoweb/         # React/TypeScript frontend for the Admin Web Dashboard
├── README.md         # This file
└── requirements.txt  # Python backend dependencies (generate if not present)
```

## Prerequisites

### Backend (Python Flask USSD Service & API)
*   Python 3.8+
*   Flask
*   mysql-connector-python
*   python-dotenv (recommended for .env file management)
*   A running MySQL Server instance

### Frontend (Admin Dashboard - `cargoweb/`)
*   Node.js (e.g., v18.x or later)
*   npm (usually comes with Node.js) or yarn

## Setup and Installation

This project consists of a Python Flask backend and a React (TypeScript) frontend located in the `cargoweb/` directory.

### 1. Clone the Repository
    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```

### 2. Backend Setup (Python Flask USSD Service & API)

   a.  **Navigate to Project Root:**
       Ensure you are in the main project directory (e.g., `ussd-crop-transport-service/`).

   b.  **Create a Python Virtual Environment (recommended):**
        ```bash
        python3 -m venv venv
        source venv/bin/activate  # On Windows: venv\Scripts\activate
        ```

   c.  **Install Backend Dependencies:**
        A `requirements.txt` should ideally be present for the backend.
        ```bash
        pip install Flask mysql-connector-python python-dotenv
        # Create/update requirements.txt after installing all necessary packages:
        # pip freeze > requirements.txt
        ```
        If a `requirements.txt` is provided:
        ```bash
        pip install -r requirements.txt
        ```

### 3. Frontend Setup (Admin Dashboard - `cargoweb/`)

   a.  **Navigate to Frontend Directory:**
        ```bash
        cd cargoweb
        ```

   b.  **Install Frontend Dependencies:**
        Using npm:
        ```bash
        npm install
        ```
        Or using yarn:
        ```bash
        yarn install
        ```

## Configure Environment Variables

### Backend (Python Flask - in project root)

The backend uses environment variables for critical configurations. It's recommended to use a `.env` file in the project root directory. If you installed `python-dotenv`, this file will be loaded automatically when running `flask run` or `python app.py`.

Create a `.env` file in the project root with the following content:
    ```env
    # Flask Configuration
    SECRET_KEY='your_very_secret_flask_key_here_CHANGE_ME' # Important: Change for production!
    FLASK_ENV='development'  # Set to 'production' for deployment
    # FLASK_APP='app.py' # Usually not needed if your main file is app.py

    # MySQL Database Configuration
    MYSQL_HOST='localhost'
    MYSQL_USER='your_mysql_user'
    MYSQL_PASSWORD='your_mysql_password'
    MYSQL_DB='transport_db'
    MYSQL_PORT='3306'
    ```
    **Note on Database:** Ensure the MySQL database (e.g., `transport_db`) specified in `MYSQL_DB` exists on your MySQL server. The application will attempt to create the necessary tables within this database if they don't already exist.

### Frontend (Admin Dashboard - `cargoweb/`)

The frontend currently has the API base URL hardcoded in `cargoweb/src/store/reportStore.ts` as `http://localhost:5000/api`.

**Recommendation for Production/Flexibility:**
For better flexibility, especially when deploying, this API URL should be configured using environment variables for the frontend. Vite (used in this React setup) supports environment variables through `.env` files in the `cargoweb/` directory.

1.  Create a `.env` file (e.g., `.env.local` or `.env`) in the `cargoweb/` directory.
2.  Add your API URL, prefixed with `VITE_` (as required by Vite):
    ```env
    VITE_API_BASE_URL=http://localhost:5000/api
    ```
3.  Modify the frontend code (e.g., in `reportStore.ts` and any other places API calls are made) to use this environment variable:
    ```typescript
    const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api';
    ```
This change makes the frontend API endpoint configurable without code changes for different environments.

## Running the Full Project

To run the complete application, you need to start both the backend Flask server and the frontend React development server.

### 1. Start the Backend (Python Flask API)

*   Ensure your Python virtual environment (e.g., `venv`) is activated.
*   Make sure your `.env` file is configured correctly in the project root, especially the database connection details.
*   Ensure your MySQL server is running.
*   From the **project root directory**, run:
    ```bash
    flask run
    ```
    Or, if you prefer to specify the host and port (especially if running in a VM or container for testing):
    ```bash
    python app.py
    # app.py is configured to run on host="0.0.0.0" and port from os.environ.get('PORT', 5000)
    ```
*   The backend API should now be running, typically on `http://localhost:5000`. You should see log output in your terminal.

### 2. Start the Frontend (React Admin Dashboard)

*   Open a **new terminal window or tab**.
*   Navigate to the frontend directory:
    ```bash
    cd cargoweb
    ```
*   If you haven't already, install dependencies:
    ```bash
    npm install
    # or yarn install
    ```
*   Start the frontend development server:
    ```bash
    npm run dev
    # or yarn dev
    ```
*   The frontend application will typically start on a different port (Vite's default is often `http://localhost:5173`, but check your terminal output).
*   Open the frontend URL provided in your terminal (e.g., `http://localhost:5173`) in your web browser to access the admin dashboard.

**Important:**
*   The frontend (e.g., in `reportStore.ts`) is configured to make API calls to the backend, by default at `http://localhost:5000/api`. Ensure this matches where your backend is actually running. If you configured `VITE_API_BASE_URL` in `cargoweb/.env`, ensure it's correct.
*   You need both servers running simultaneously to use the admin dashboard features that interact with the API.

## USSD Workflow

The USSD service is accessible via a callback URL, typically `http://your_domain_or_ip/`, which would be configured with a USSD provider like Africa's Talking. The menus for selecting crops and locations are now dynamically populated from the database.

1.  **Main Menu:** User dials the USSD code.
    *   `CON Karibu Huduma ya Usafirishaji wa Mazao`
        *   `1. Omba Usafiri` (Request Transport)
        *   `2. Fuatilia Ombi` (Track Order)
        *   `3. Mawasiliano` (Contact Info)
        *   `0. Toka` (Exit)

2.  **Omba Usafiri (Request Transport):**
    *   User selects crop type (from DB list).
    *   User enters quantity (in bags).
    *   User selects pickup location (from DB list).
    *   User selects destination location (from DB list).
    *   Order is confirmed, a tracking number is generated, and transporter details (randomly assigned from DB) are provided.
    *   `END UTHIBITISHO - OMBI LIMEPOKELEWA!...`

3.  **Fuatilia Ombi (Track Order):**
    *   User enters their tracking number.
    *   Order status and details are displayed (fetched with joins).
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

The `app.py` is written to be generally compatible with environments like cPanel that use Passenger or similar WSGI servers. Further details would depend on specific hosting provider configurations for both Python backend and Node.js frontend.

1.  **Backend Deployment:**
    *   Upload your Python project files (excluding `venv`).
    *   Create a Python application through the cPanel interface.
    *   Set the Application Startup File (e.g., `passenger_wsgi.py`).
    *   Install dependencies into the virtual environment created by cPanel.
    *   Set up environment variables for database credentials, `SECRET_KEY`, `FLASK_ENV='production'`.
2.  **Frontend Deployment:**
    *   Build the React application: `cd cargoweb && npm run build`.
    *   Upload the contents of the `cargoweb/dist` directory to your web server (e.g., into `public_html` or a subdirectory).
    *   Ensure your web server (e.g., Apache, Nginx) is configured to serve the `index.html` from this directory and handle client-side routing correctly (often requires rewrite rules for single-page applications).
    *   Configure the production API URL for the frontend if it's different from development.

## Future Enhancements

*   User authentication for admin APIs and frontend dashboard.
*   More detailed status options and history for orders.
*   Integration with a payment gateway.
*   SMS notifications for order updates.
*   Full UI implementation for managing all entities (Transporters, Locations, Crops, Settings) in `cargoweb/`.
*   Advanced reporting features (filtering, charting, export to CSV/Excel).
```
