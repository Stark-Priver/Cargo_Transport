from flask import Flask, request, jsonify
import os
import random
import string
import json
from datetime import datetime, timedelta
import logging
from werkzeug.exceptions import BadRequest
import mysql.connector
from mysql.connector import Error as MySQLError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuration
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
    MAX_QUANTITY = 1000  # Maximum bags allowed
    MIN_QUANTITY = 1     # Minimum bags required

    # MySQL Configuration - Read from environment variables
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
    MYSQL_DB = os.environ.get('MYSQL_DB', 'transport_db')
    MYSQL_PORT = os.environ.get('MYSQL_PORT', 3306)
    # DATABASE_FILE = 'transport_orders.json' # Removed


# Initialize app config
app.config.from_object(Config)

# Database connection pool
db_pool = None

def create_tables_if_not_exist():
    """Creates database tables if they don't already exist."""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        if conn is None:
            logger.error("Failed to get DB connection for table creation.")
            return

        cursor = conn.cursor()

        # Define the transporters table schema
        transporters_table_sql = """
        CREATE TABLE IF NOT EXISTS transporters (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            phone VARCHAR(20) UNIQUE,
            rating VARCHAR(10),
            vehicle_details TEXT,
            notes TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """
        cursor.execute(transporters_table_sql)
        logger.info("`transporters` table checked/created successfully.")

        # Define the locations table schema
        locations_table_sql = """
        CREATE TABLE IF NOT EXISTS locations (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            type ENUM('pickup', 'destination', 'both') DEFAULT 'both',
            region VARCHAR(100),
            is_active BOOLEAN DEFAULT TRUE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            UNIQUE KEY unique_location_name_type (name, type)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """
        cursor.execute(locations_table_sql)
        logger.info("`locations` table checked/created successfully.")

        # Define the crops table schema
        crops_table_sql = """
        CREATE TABLE IF NOT EXISTS crops (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL UNIQUE,
            description TEXT,
            is_active BOOLEAN DEFAULT TRUE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """
        cursor.execute(crops_table_sql)
        logger.info("`crops` table checked/created successfully.")

        # Define the system_settings table schema
        system_settings_table_sql = """
        CREATE TABLE IF NOT EXISTS system_settings (
            setting_key VARCHAR(100) PRIMARY KEY,
            setting_value TEXT,
            description TEXT,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """
        cursor.execute(system_settings_table_sql)
        logger.info("`system_settings` table checked/created successfully.")

        # Modify the orders table schema (
        # For simplicity, we'll add new columns first. Dropping/altering old ones
        # would require more careful data migration in a live system.
        # We will make the new ID fields nullable for now to ease transition.
        # The goal is to eventually make them NOT NULL and remove denormalized fields.
        orders_table_modification_sqls = [
            "ALTER TABLE orders ADD COLUMN IF NOT EXISTS transporter_id INT NULL AFTER transporter_rating, ADD CONSTRAINT fk_transporter FOREIGN KEY (transporter_id) REFERENCES transporters(id) ON DELETE SET NULL",
            "ALTER TABLE orders ADD COLUMN IF NOT EXISTS crop_id INT NULL AFTER phone_number, ADD CONSTRAINT fk_crop FOREIGN KEY (crop_id) REFERENCES crops(id) ON DELETE SET NULL",
            "ALTER TABLE orders ADD COLUMN IF NOT EXISTS pickup_location_id INT NULL AFTER quantity, ADD CONSTRAINT fk_pickup_location FOREIGN KEY (pickup_location_id) REFERENCES locations(id) ON DELETE SET NULL",
            "ALTER TABLE orders ADD COLUMN IF NOT EXISTS destination_location_id INT NULL AFTER pickup_location_id, ADD CONSTRAINT fk_destination_location FOREIGN KEY (destination_location_id) REFERENCES locations(id) ON DELETE SET NULL"
        ]

        # Original orders table schema (if it needs to be created from scratch)
        # This includes the old fields for now, and the new FK fields.
        # In a real migration, you'd handle existing data carefully.
        orders_table_sql = """
        CREATE TABLE IF NOT EXISTS orders (
            track_number VARCHAR(20) PRIMARY KEY,
            phone_number VARCHAR(20),
            crop_id INT NULL,
            crop VARCHAR(100), -- Old field, to be deprecated
            quantity INT,
            pickup_location_id INT NULL,
            destination_location_id INT NULL,
            pickup_location VARCHAR(255), -- Old field, to be deprecated
            destination_location VARCHAR(255), -- Old field, to be deprecated
            transporter_id INT NULL,
            transporter_name VARCHAR(255), -- Old field, to be deprecated
            transporter_phone VARCHAR(20), -- Old field, to be deprecated
            transporter_rating VARCHAR(10), -- Old field, to be deprecated
            status VARCHAR(255),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            status_updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            CONSTRAINT fk_orders_crop FOREIGN KEY (crop_id) REFERENCES crops(id) ON DELETE SET NULL,
            CONSTRAINT fk_orders_pickup_location FOREIGN KEY (pickup_location_id) REFERENCES locations(id) ON DELETE SET NULL,
            CONSTRAINT fk_orders_destination_location FOREIGN KEY (destination_location_id) REFERENCES locations(id) ON DELETE SET NULL,
            CONSTRAINT fk_orders_transporter FOREIGN KEY (transporter_id) REFERENCES transporters(id) ON DELETE SET NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """
        cursor.execute(orders_table_sql) # Create orders table if not exists with new FKs
        logger.info("`orders` table schema checked/created successfully with FKs.")

        # Apply ALTER TABLE statements separately for existing tables.
        # This is a simplified approach. A proper migration tool would be better.
        # We need to catch errors if a column already exists, hence ADD COLUMN IF NOT EXISTS (MySQL 8.0.1+)
        # For older MySQL, one might need to query information_schema.columns
        # For this exercise, assuming MySQL 8.0.1+ or that these specific ALTERs are safe.
        # A more robust way for ALTER is to check if column exists first via information_schema.

        existing_columns_check = {
            "transporter_id": False, "crop_id": False,
            "pickup_location_id": False, "destination_location_id": False
        }
        cursor.execute(f"DESCRIBE orders;")
        for col_info in cursor.fetchall():
            if col_info[0] in existing_columns_check: # col_info[0] is Field name
                existing_columns_check[col_info[0]] = True

        if not existing_columns_check["transporter_id"]:
            cursor.execute("ALTER TABLE orders ADD COLUMN transporter_id INT NULL AFTER transporter_rating, ADD CONSTRAINT fk_transporter FOREIGN KEY (transporter_id) REFERENCES transporters(id) ON DELETE SET NULL")
            logger.info("Added transporter_id to orders table.")
        if not existing_columns_check["crop_id"]:
            cursor.execute("ALTER TABLE orders ADD COLUMN crop_id INT NULL AFTER phone_number, ADD CONSTRAINT fk_crop FOREIGN KEY (crop_id) REFERENCES crops(id) ON DELETE SET NULL")
            logger.info("Added crop_id to orders table.")
        if not existing_columns_check["pickup_location_id"]:
            cursor.execute("ALTER TABLE orders ADD COLUMN pickup_location_id INT NULL AFTER quantity, ADD CONSTRAINT fk_pickup_location FOREIGN KEY (pickup_location_id) REFERENCES locations(id) ON DELETE SET NULL")
            logger.info("Added pickup_location_id to orders table.")
        if not existing_columns_check["destination_location_id"]:
            cursor.execute("ALTER TABLE orders ADD COLUMN destination_location_id INT NULL AFTER pickup_location_id, ADD CONSTRAINT fk_destination_location FOREIGN KEY (destination_location_id) REFERENCES locations(id) ON DELETE SET NULL")
            logger.info("Added destination_location_id to orders table.")

        conn.commit()
        logger.info("All tables checked/created/modified successfully.")

    except MySQLError as e:
        logger.error(f"Error during table creation/modification: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()
            logger.debug("MySQL connection closed after table creation check.")


def init_db_pool():
    """Initialize MySQL connection pool."""
    global db_pool
    try:
        db_pool = mysql.connector.pooling.MySQLConnectionPool(
            pool_name="transport_pool",
            pool_size=5,
            host=app.config['MYSQL_HOST'],
            user=app.config['MYSQL_USER'],
            password=app.config['MYSQL_PASSWORD'],
            database=app.config['MYSQL_DB'],
            port=app.config['MYSQL_PORT']
        )
        logger.info("MySQL connection pool initialized successfully.")
    except MySQLError as e:
        logger.error(f"Error while connecting to MySQL using connection pool: {e}")
        db_pool = None # Ensure pool is None if initialization fails

def get_db_connection():
    """Get a connection from the pool."""
    if not db_pool:
        logger.error("Connection pool is not initialized. Call init_db_pool() first.")
        # Attempt to re-initialize, could be a transient issue or first call
        init_db_pool()
        if not db_pool: # If still not initialized, raise error
             raise MySQLError("Failed to initialize database connection pool.")
    try:
        conn = db_pool.get_connection()
        if conn.is_connected():
            logger.debug("MySQL connection acquired from pool.")
            return conn
        else:
            logger.error("Failed to get a valid connection from pool.")
            return None
    except MySQLError as e:
        logger.error(f"Error getting connection from pool: {e}")
        return None

# JSON-based functions load_orders and save_orders are now removed.

def generate_track_number():
    """Generate a unique tracking number"""
    timestamp = datetime.now().strftime("%y%m%d")
    random_part = ''.join(random.choices(string.digits, k=4))
    return f'TRK{timestamp}{random_part}'

def generate_phone_number():
    """Generate a random Tanzanian phone number"""
    prefixes = ['0754', '0755', '0756', '0757', '0765', '0766', '0767', '0768', 
                '0713', '0714', '0715', '0716', '0782', '0783', '0784', '0785']
    prefix = random.choice(prefixes)
    remaining = ''.join(random.choices(string.digits, k=6))
    return prefix + remaining

def get_transporter_details():
    """Get random transporter details"""
    transporters = [
        {"name": "Juma Mwalimu", "phone": generate_phone_number(), "rating": "4.8/5"},
        {"name": "Fatuma Hassan", "phone": generate_phone_number(), "rating": "4.9/5"},
        {"name": "Mohamed Ally", "phone": generate_phone_number(), "rating": "4.7/5"},
        {"name": "Grace Mapunda", "phone": generate_phone_number(), "rating": "4.6/5"},
        {"name": "John Msigwa", "phone": generate_phone_number(), "rating": "4.8/5"},
        {"name": "Amina Rashid", "phone": generate_phone_number(), "rating": "4.9/5"},
        {"name": "Peter Kikwete", "phone": generate_phone_number(), "rating": "4.7/5"},
        {"name": "Salma Juma", "phone": generate_phone_number(), "rating": "4.8/5"},
        {"name": "Hassan Mwenda", "phone": generate_phone_number(), "rating": "4.6/5"},
        {"name": "Neema Shayo", "phone": generate_phone_number(), "rating": "4.9/5"}
    ]
    return random.choice(transporters)

# --- Helper functions for dynamic USSD choices ---
def get_active_crops_for_ussd():
    """Fetches active crops from the database for USSD menu display."""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        if conn is None:
            logger.error("Failed to get DB connection for fetching crops.")
            return [] # Return empty list on error
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, name FROM crops WHERE is_active = TRUE ORDER BY name")
        crops = cursor.fetchall()
        return crops # List of dicts e.g. [{'id': 1, 'name': 'Mahindi'}]
    except MySQLError as e:
        logger.error(f"Error fetching active crops: {e}")
        return []
    finally:
        if cursor: cursor.close()
        if conn and conn.is_connected(): conn.close()

def get_active_locations_for_ussd(location_type_filter=None):
    """
    Fetches active locations from the database for USSD menu display.
    location_type_filter can be 'pickup' or 'destination'.
    If None, fetches all 'both' or specific types if needed broadly.
    For USSD, we usually fetch specific types.
    """
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        if conn is None:
            logger.error("Failed to get DB connection for fetching locations.")
            return []
        cursor = conn.cursor(dictionary=True)

        sql = "SELECT id, name, type FROM locations WHERE is_active = TRUE "
        params = []
        if location_type_filter == 'pickup':
            sql += "AND (type = 'pickup' OR type = 'both') "
        elif location_type_filter == 'destination':
            sql += "AND (type = 'destination' OR type = 'both') "
        # else, could fetch all active if needed, or raise error for invalid filter

        sql += "ORDER BY name"
        cursor.execute(sql, tuple(params))
        locations = cursor.fetchall()
        return locations # List of dicts e.g. [{'id':1, 'name':'Mbeya Mjini', 'type':'both'}]
    except MySQLError as e:
        logger.error(f"Error fetching active locations (type: {location_type_filter}): {e}")
        return []
    finally:
        if cursor: cursor.close()
        if conn and conn.is_connected(): conn.close()

def get_entity_by_id(entity_type, entity_id):
    """Generic function to fetch entity name by ID for confirmation messages."""
    conn = None
    cursor = None
    table_name = ""
    if entity_type == "crop":
        table_name = "crops"
    elif entity_type == "location":
        table_name = "locations"
    elif entity_type == "transporter":
        table_name = "transporters"
    else:
        return None

    try:
        conn = get_db_connection()
        if conn is None: return None
        cursor = conn.cursor(dictionary=True)
        cursor.execute(f"SELECT name FROM {table_name} WHERE id = %s", (entity_id,))
        result = cursor.fetchone()
        return result['name'] if result else None
    except MySQLError as e:
        logger.error(f"Error fetching {entity_type} with ID {entity_id}: {e}")
        return None
    finally:
        if cursor: cursor.close()
        if conn and conn.is_connected(): conn.close()


def is_valid_quantity(quantity_str):
    """Validate quantity input"""
    try:
        quantity = int(quantity_str)
        return Config.MIN_QUANTITY <= quantity <= Config.MAX_QUANTITY
    except:
        return False

def save_order(track_number, order_data):
    """Save order to MySQL database"""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        if conn is None:
            logger.error("Failed to get DB connection for saving order.")
            return False
        cursor = conn.cursor()

        sql = """
        INSERT INTO orders (
            track_number, phone_number,
            crop_id, crop,
            quantity,
            pickup_location_id, pickup_location,
            destination_location_id, destination_location,
            transporter_id, transporter_name, transporter_phone, transporter_rating,
            status, created_at, status_updated_at
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        # The USSD callback will eventually need to provide these IDs.
        # For now, they might be None if old USSD logic is still partially active.
        # The old text fields (crop, pickup_location etc.) are still populated from order_data.

        current_time = datetime.now()
        transporter_details = order_data.get('transporter', {})

        data_tuple = (
            track_number,
            order_data.get('phone_number'),
            order_data.get('crop_id'),  # New field
            order_data.get('crop'), # Old field
            order_data.get('quantity'),
            order_data.get('pickup_location_id'), # New field
            order_data.get('pickup_location'), # Old field
            order_data.get('destination_location_id'), # New field
            order_data.get('destination_location'), # Old field
            transporter_details.get('id'), # New: ID of the selected transporter
            transporter_details.get('name'), # Old field
            transporter_details.get('phone'), # Old field
            transporter_details.get('rating'),# Old field
            'Ombi limepokelewa na Msafirishaji atawasiliana na wewe hivi karibuni', # Initial status
            current_time, # created_at
            current_time  # status_updated_at
        )

        cursor.execute(sql, data_tuple)
        conn.commit()
        logger.info(f"Order {track_number} saved successfully to MySQL.")
        return True
    except MySQLError as e:
        logger.error(f"Error saving order {track_number} to MySQL: {e}")
        if conn:
            conn.rollback() # Rollback in case of error
        return False
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()
            logger.debug("MySQL connection closed after saving order.")

def get_order_status(track_number):
    """Get order status from MySQL database"""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        if conn is None:
            logger.error(f"Failed to get DB connection for fetching order {track_number}.")
            return None

        # Use a dictionary cursor to easily map column names to values
        cursor = conn.cursor(dictionary=True)

        # Join with related tables
        sql = """
        SELECT
            o.track_number, o.phone_number, o.quantity, o.status,
            o.created_at, o.status_updated_at,
            COALESCE(c.name, o.crop) as crop_name,
            COALESCE(pl.name, o.pickup_location) as pickup_location_name,
            COALESCE(dl.name, o.destination_location) as destination_location_name,
            COALESCE(t.name, o.transporter_name) as transporter_actual_name,
            COALESCE(t.phone, o.transporter_phone) as transporter_actual_phone,
            COALESCE(t.rating, o.transporter_rating) as transporter_actual_rating,
            o.crop_id, o.pickup_location_id, o.destination_location_id, o.transporter_id
        FROM orders o
        LEFT JOIN crops c ON o.crop_id = c.id
        LEFT JOIN locations pl ON o.pickup_location_id = pl.id
        LEFT JOIN locations dl ON o.destination_location_id = dl.id
        LEFT JOIN transporters t ON o.transporter_id = t.id
        WHERE o.track_number = %s
        """
        cursor.execute(sql, (track_number,))
        order_data_raw = cursor.fetchone()

        if order_data_raw:
            logger.info(f"Order {track_number} fetched successfully from MySQL for USSD.")
            order_data = dict(order_data_raw) # Make it a mutable dict

            # USSD logic expects 'crop', 'pickup_location', 'destination_location'
            # and a nested 'transporter' dict.
            order_data['crop'] = order_data.get('crop_name')
            order_data['pickup_location'] = order_data.get('pickup_location_name')
            order_data['destination_location'] = order_data.get('destination_location_name')

            order_data['transporter'] = {
                'id': order_data.get('transporter_id'), # Keep id if available
                'name': order_data.get('transporter_actual_name'),
                'phone': order_data.get('transporter_actual_phone'),
                'rating': order_data.get('transporter_actual_rating')
            }

            # Clean up redundant fields from the root of order_data for USSD context
            for key in ['crop_name', 'pickup_location_name', 'destination_location_name',
                        'transporter_actual_name', 'transporter_actual_phone', 'transporter_actual_rating',
                        'crop_id', 'pickup_location_id', 'destination_location_id', 'transporter_id']:
                order_data.pop(key, None)

            # Convert datetime objects if needed by any part of USSD (usually not directly, but good for consistency)
            if isinstance(order_data.get('created_at'), datetime):
                order_data['created_at'] = order_data['created_at'].isoformat()
            if isinstance(order_data.get('status_updated_at'), datetime):
                order_data['status_updated_at'] = order_data['status_updated_at'].isoformat()
            return order_data
        else:
            logger.info(f"Order {track_number} not found in MySQL for USSD.")
            return None
    except MySQLError as e:
        logger.error(f"Error fetching order {track_number} from MySQL: {e}")
        return None
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()
            logger.debug(f"MySQL connection closed after fetching order {track_number}.")

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'USSD Transport Service'
    })

@app.route('/', methods=['POST', 'GET'])
def ussd_callback():
    """Main USSD callback handler"""
    try:
        # Get parameters
        session_id = request.values.get("sessionId", "")
        service_code = request.values.get("serviceCode", "")
        phone_number = request.values.get("phoneNumber", "")
        text = request.values.get("text", "")
        
        # Log the request
        logger.info(f"USSD Request - Session: {session_id}, Phone: {phone_number}, Text: '{text}'")
        
        response = ""
        
        # REMOVE Old Mapping dictionaries - Data will be fetched from DB
        # crops_dict_hardcoded = {'1': 'Mahindi', '2': 'Viazi', '3': 'Mpunga', '4': 'Zao Jingine'}
        # locations_dict_hardcoded = { ... }

        # Session cache for dynamic menu items (simple approach)
        # A more robust session management (e.g. Redis, Flask session) would be better for production
        # For this example, we'll assume choices are encoded in the 'text' string or re-fetched.
        # However, to map user's numeric choice back to an ID, we often need to store the list
        # that was presented. This is a challenge in pure USSD text string.
        # A common pattern is:
        # 1. Show menu: 1. ItemA (ID:10), 2. ItemB (ID:25)
        # 2. User enters '1'. We need to know that '1' maps to ID 10.
        # The text string becomes e.g., level1_choice*level2_choice_index*level3_choice_index...
        # Then at each stage, we re-fetch the list shown at previous stage to find the ID.

        # Main Menu
        if text == '':
            response = "CON Karibu Huduma ya Usafirishaji wa Mazao\n"
            response += "1. Omba Usafiri\n"
            response += "2. Fuatilia Ombi\n"
            response += "3. Mawasiliano\n"
            response += "0. Toka"
        
        # Option 1: Request Transport - Display list of crops from DB
        elif text == '1': # User chose "1. Omba Usafiri" from main menu
            active_crops = get_active_crops_for_ussd()
            if not active_crops:
                response = "END Samahani, hakuna mazao yanayopatikana kwa sasa."
            else:
                response = "CON CHAGUA ZAO UNALOTAKA KUSAFIRISHA:\n"
                for i, crop_item in enumerate(active_crops):
                    # User will choose 1, 2, 3...
                    # The text input for next stage will be "1*<choice_number>"
                    # e.g., if user picks 1st crop, next text is "1*1"
                    response += f"{i+1}. {crop_item['name']}\n"
                response += "\n0. Rudi Nyuma" # This 0 should lead to text "1*0"

        # User has selected a crop (by index from menu), or chose 0 to go back
        # Text format: 1*<user_choice_for_crop_OR_0>
        elif text.startswith('1*') and len(text.split('*')) == 2:
            parts = text.split('*')
            crop_menu_choice_str = parts[1]

            if crop_menu_choice_str == '0': # User selected "0. Rudi Nyuma" from Crop Selection menu
                # Go back to Main Menu
                response = "CON Karibu Huduma ya Usafirishaji wa Mazao\n"
                response += "1. Omba Usafiri\n"
                response += "2. Fuatilia Ombi\n"
                response += "3. Mawasiliano\n"
                response += "0. Toka"
            else:
                # User selected a crop by its menu number (1-based)
                try:
                    crop_choice_idx_from_menu = int(crop_menu_choice_str) - 1 # Convert to 0-based index

                    # Re-fetch the list of crops to map the menu index back to the actual crop object/ID
                    # This is important if the list is dynamic or could change between requests.
                    # For USSD, this re-fetch per step is a common pattern if not using server-side session state.
                    active_crops_session = get_active_crops_for_ussd()

                    if 0 <= crop_choice_idx_from_menu < len(active_crops_session):
                        selected_crop_obj = active_crops_session[crop_choice_idx_from_menu]
                        # Now we have selected_crop_obj['id'] and selected_crop_obj['name']
                        # The next state will be asking for quantity.
                        # The text for the next stage will be: "1*<crop_menu_idx>*<quantity_or_0_for_back>"
                        response = f"CON WEKA KIASI CHA {selected_crop_obj['name'].upper()}:\n\n"
                        response += "Andika idadi ya magunia\n"
                        response += f"(Kiwango: {Config.MIN_QUANTITY}-{Config.MAX_QUANTITY} magunia)\n\n"
                        response += "0. Rudi Nyuma" # This 0 should lead to "1*<crop_menu_idx>*0"
                    else:
                        # Invalid index chosen, re-show crop list
                        response = "CON Chaguo la zao si sahihi. Jaribu tena.\n"
                        active_crops_menu_again = get_active_crops_for_ussd()
                        if not active_crops_menu_again:
                            response = "END Samahani, hakuna mazao yanayopatikana kwa sasa."
                        else:
                            for i, crop_item_again in enumerate(active_crops_menu_again):
                                response += f"{i+1}. {crop_item_again['name']}\n"
                            response += "\n0. Rudi Nyuma" # Back to main menu (text='1*0')
                except ValueError: # If crop_menu_choice_str is not a valid number
                     response = "CON Chaguo si sahihi. Jaribu tena.\n0. Rudi Nyuma" # Back to main menu (text='1*0')
        
        # OLD: elif text == '1*0':  # Back to main menu from crop selection - Handled by 1*<0> above
            # response = "CON HUDUMA YA USAFIRIDHAJI MAZAO\n"

        # User has entered quantity (or 0 to go back from quantity screen)
        # Text format: 1*<crop_menu_idx>*<quantity_or_0>
        elif text.startswith('1*') and len(text.split('*')) == 3:
            parts = text.split('*')
            crop_choice_idx_str = parts[1] # This is the MENU INDEX previously chosen for crop
            quantity_input_str = parts[2]  # This is the quantity entered, or "0" if user chose back

            if quantity_input_str == '0':  # User chose "0. Rudi Nyuma" from Quantity Input screen
                # Go back to Crop Selection screen (which is text='1')
                active_crops_reselect = get_active_crops_for_ussd()
                if not active_crops_reselect:
                    response = "END Samahani, hakuna mazao yanayopatikana kwa sasa."
                else:
                    response = "CON CHAGUA ZAO UNALOTAKA KUSAFIRISHA:\n"
                    for i, crop_item_reselect in enumerate(active_crops_reselect):
                        response += f"{i+1}. {crop_item_reselect['name']}\n"
                    response += "\n0. Rudi Nyuma" # This 0 leads to text "1*0" (Main Menu)
            elif not is_valid_quantity(quantity_input_str):
                # Invalid quantity, re-ask quantity for the previously selected crop
                try:
                    crop_choice_idx = int(crop_choice_idx_str) - 1
                    active_crops_qty_err = get_active_crops_for_ussd()
                    if 0 <= crop_choice_idx < len(active_crops_qty_err):
                        selected_crop_name_qty_err = active_crops_qty_err[crop_choice_idx]['name']
                        response = f"CON KIASI SI SAHIHI!\n\n"
                        response += f"WEKA KIASI CHA {selected_crop_name_qty_err.upper()}:\n"
                        response += "Andika idadi ya magunia\n"
                        response += f"(Kiwango: {Config.MIN_QUANTITY}-{Config.MAX_QUANTITY} magunia)\n\n"
                        response += "0. Rudi Nyuma" # This 0 leads to "1*<crop_menu_idx>*0" (Back to Crop Selection)
                    else:
                        response = "END Kosa la mfumo (crop index out of bounds). Tafadhali anza upya."
                except ValueError:
                    response = "END Kosa la mfumo (invalid crop index format). Tafadhali anza upya."
            else:
                # Quantity is valid. Text is 1*<crop_menu_idx>*<valid_qty>
                # Now show pickup locations
                active_pickup_locations = get_active_locations_for_ussd(location_type_filter='pickup')
                if not active_pickup_locations:
                    response = "END Samahani, hakuna maeneo ya kuchukua mizigo kwa sasa."
                else:
                    response = "CON CHAGUA MAHALI PA KUCHUKUA MIZIGO:\n"
                    for i, loc_item_pickup in enumerate(active_pickup_locations):
                        response += f"{i+1}. {loc_item_pickup['name']}\n"
                    response += "\n0. Rudi Nyuma"
                    # This 0 leads to "1*<crop_menu_idx>*<valid_qty>*0" (Back to Quantity Input)

        # Destination location selection after pickup location
        # Text format: 1*<crop_menu_idx>*<qty>*<pickup_loc_menu_idx_or_0>
        elif text.startswith('1*') and len(text.split('*')) == 4:
            parts = text.split('*')
            crop_choice_idx_str = parts[1]
            quantity_str = parts[2]
            pickup_loc_menu_idx_input_str = parts[3]

            if pickup_loc_menu_idx_input_str == '0':  # User chose "0. Rudi Nyuma" from Pickup Location screen
                # Go back to Quantity Input screen for the selected crop
                try:
                    crop_choice_idx = int(crop_choice_idx_str) - 1
                    active_crops_pickup_back = get_active_crops_for_ussd()
                    if 0 <= crop_choice_idx < len(active_crops_pickup_back):
                        selected_crop_name_pickup_back = active_crops_pickup_back[crop_choice_idx]['name']
                        # Text for next stage will be "1*<crop_menu_idx>*<new_qty_or_0>"
                        response = f"CON WEKA KIASI CHA {selected_crop_name_pickup_back.upper()}:\n\n"
                        response += "Andika idadi ya magunia\n"
                        response += f"(Kiwango: {Config.MIN_QUANTITY}-{Config.MAX_QUANTITY} magunia)\n\n"
                        response += "0. Rudi Nyuma" # This 0 leads to "1*<crop_menu_idx>*0" (Crop Selection)
                    else:
                        response = "END Kosa la mfumo (crop index out of bounds). Anza upya."
                except ValueError:
                     response = "END Kosa la mfumo (invalid crop index format). Anza upya."
            else:
                # Valid pickup location menu index chosen.
                # Text is 1*<crop_menu_idx>*<qty>*<pickup_loc_menu_idx>
                # Show destination locations
                try:
                    pickup_loc_menu_idx = int(pickup_loc_menu_idx_input_str) - 1
                    active_pickup_locations_session = get_active_locations_for_ussd(location_type_filter='pickup')

                    if not (0 <= pickup_loc_menu_idx < len(active_pickup_locations_session)):
                        # Invalid index, reshow pickup locations
                        response = "CON Chaguo la eneo si sahihi. Jaribu tena:\n"
                        if not active_pickup_locations_session:
                            response = "END Samahani, hakuna maeneo ya kuchukua mizigo kwa sasa."
                        else:
                            for i, loc_item_pickup_err in enumerate(active_pickup_locations_session):
                                response += f"{i+1}. {loc_item_pickup_err['name']}\n"
                            response += "\n0. Rudi Nyuma" # To quantity input
                    else:
                        selected_pickup_loc_obj = active_pickup_locations_session[pickup_loc_menu_idx]
                        selected_pickup_loc_name = selected_pickup_loc_obj['name']

                        active_dest_locations = get_active_locations_for_ussd(location_type_filter='destination')
                        if not active_dest_locations:
                            response = "END Samahani, hakuna maeneo ya kupeleka mizigo kwa sasa."
                        else:
                            response = f"CON CHAGUA MAHALI MZIGO UNAPOENDA:\n(Kutoka: {selected_pickup_loc_name})\n"
                            for i, loc_item_dest in enumerate(active_dest_locations):
                                response += f"{i+1}. {loc_item_dest['name']}\n"
                            response += "\n0. Rudi Nyuma"
                            # This 0 leads to "1*<crop_idx>*<qty>*<pickup_idx>*0" (Back to Pickup Location Selection)
                except ValueError:
                    response = "END Kosa la mfumo (invalid pickup location index format). Jaribu tena."

        # Final confirmation and order creation
        # Text format: 1*<crop_menu_idx>*<qty>*<pickup_loc_menu_idx>*<dest_loc_menu_idx_or_0>
        elif text.startswith('1*') and len(text.split('*')) == 5:
            parts = text.split('*')
            crop_choice_menu_idx_str = parts[1]
            quantity_str = parts[2]
            pickup_loc_menu_idx_str = parts[3]
            dest_loc_menu_idx_input_str = parts[4]

            if dest_loc_menu_idx_input_str == '0':  # User chose "0. Rudi Nyuma" from Destination Location screen
                # Go back to Pickup Location selection screen
                # Need to display the list of pickup locations again.
                active_pickup_locations_reselect = get_active_locations_for_ussd(location_type_filter='pickup')
                if not active_pickup_locations_reselect:
                    response = "END Samahani, hakuna maeneo ya kuchukua mizigo kwa sasa."
                else:
                    response = "CON CHAGUA MAHALI PA KUCHUKUA MIZIGO:\n"
                    for i, loc_item_pickup_reselect in enumerate(active_pickup_locations_reselect):
                        response += f"{i+1}. {loc_item_pickup_reselect['name']}\n"
                    response += "\n0. Rudi Nyuma" # This 0 leads to "1*<crop_idx>*<qty>*0" (Back to Quantity Input)
            else:
                # All inputs gathered (by menu indices), proceed to create order
                try:
                    # Resolve all choices to their actual DB objects/IDs
                    crop_choice_idx = int(crop_choice_menu_idx_str) - 1
                    active_crops_final = get_active_crops_for_ussd()
                    if not (0 <= crop_choice_idx < len(active_crops_final)): raise ValueError("Invalid crop index")
                    final_selected_crop = active_crops_final[crop_choice_idx]

                    pickup_loc_idx = int(pickup_loc_menu_idx_str) - 1
                    active_pickup_locs_final = get_active_locations_for_ussd(location_type_filter='pickup')
                    if not (0 <= pickup_loc_idx < len(active_pickup_locs_final)): raise ValueError("Invalid pickup location index")
                    final_selected_pickup_loc = active_pickup_locs_final[pickup_loc_idx]

                    dest_loc_idx = int(dest_loc_menu_idx_input_str) - 1
                    active_dest_locs_final = get_active_locations_for_ussd(location_type_filter='destination')
                    if not (0 <= dest_loc_idx < len(active_dest_locs_final)): raise ValueError("Invalid destination location index")
                    final_selected_dest_loc = active_dest_locs_final[dest_loc_idx]

                    if final_selected_pickup_loc['id'] == final_selected_dest_loc['id']:
                        response = "END MAKOSA - MAHALI NI SAWA\n\n"
                        response += "Mahali pa kuchukua na pa uwasilishaji haviwezi kuwa sawa.\n"
                        response += "Tafadhali chagua maeneo tofauti.\nAsante!" # End session here.
                    elif not is_valid_quantity(quantity_str):
                        response = "END Kiasi si sahihi. Anza upya."
                    else:
                        track_number = generate_track_number()

                        assigned_transporter = None
                        conn_tp = get_db_connection()
                        if conn_tp:
                            cursor_tp = conn_tp.cursor(dictionary=True)
                            cursor_tp.execute("SELECT id, name, phone, rating FROM transporters ORDER BY RAND() LIMIT 1")
                            assigned_transporter = cursor_tp.fetchone()
                            if cursor_tp: cursor_tp.close()
                            if conn_tp: conn_tp.close()

                        if not assigned_transporter:
                            assigned_transporter = {"name": "N/A", "phone": "N/A", "rating": "N/A", "id": None}
                            logger.warning("No transporter found in DB or DB error for USSD order, order will have NULL transporter_id.")

                        order_data_to_save = {
                            'phone_number': phone_number,
                            'crop_id': final_selected_crop['id'], 'crop': final_selected_crop['name'],
                            'quantity': quantity_str,
                            'pickup_location_id': final_selected_pickup_loc['id'], 'pickup_location': final_selected_pickup_loc['name'],
                            'destination_location_id': final_selected_dest_loc['id'], 'destination_location': final_selected_dest_loc['name'],
                            'transporter': assigned_transporter
                        }

                        if save_order(track_number, order_data_to_save):
                            response = "END UTHIBITISHO - OMBI LIMEPOKELEWA!\n\n"
                            response += f"Zao: {final_selected_crop['name']}\n"
                            response += f"Kiasi: {quantity_str} Magunia\n"
                            response += f"Kutoka: {final_selected_pickup_loc['name']}\n"
                            response += f"Kwenda: {final_selected_dest_loc['name']}\n"
                            response += f"Namba ya Ufuatiliaji: {track_number}\n\n"
                            response += f"Msafirishaji: {assigned_transporter.get('name', 'Atathibitishwa')}\n"
                            response += f"Mawasiliano: {assigned_transporter.get('phone', 'Atathibitishwa')}\n"
                            response += "Msafirishaji atawasiliana nawe.\nAsante!"
                        else:
                            response = "END Samahani, ombi lako limeshindikana. Jaribu tena."
                except ValueError as ve:
                    logger.error(f"ValueError during final order processing (text: {text}): {ve}")
                    response = "END Kosa la mfumo. Tafadhali anza upya."
                except Exception as e:
                    logger.error(f"General Exception during final order processing (text: {text}): {e}", exc_info=True)
                    response = "END Samahani, tatizo la kimfumo limetokea. Jaribu tena."
        
        # Option 2: Track Order
        elif text == '2':
            response += "Karibu! Chagua huduma:\n\n"
            response += "1. Omba Usafiri\n"
            response += "2. Fuatilia Ombi\n"
            response += "3. Mawasiliano\n"
            response += "0. Toka"
        
        # Pickup location selection after quantity input
        elif text.startswith('1*') and len(text.split('*')) == 3:
            parts = text.split('*')
            crop_choice = parts[1]
            quantity = parts[2]
            
            if quantity == '0':  # Back to crop selection
                response = "CON CHAGUA ZAO UNALOTAKA KUSAFIRISHA:\n\n"
                response += "1. Mahindi\n"
                response += "2. Viazi\n"
                response += "3. Mpunga\n"
                response += "4. Zao Jingine\n\n"
                response += "0. Rudi Nyuma"
            elif not is_valid_quantity(quantity):
                crop_name = crops.get(crop_choice, 'Zao')
                response = f"CON KIASI SI SAHIHI!\n\n"
                response += f"WEKA KIASI CHA {crop_name.upper()}:\n"
                response += "Andika idadi ya magunia\n"
                response += f"(Kiwango: {Config.MIN_QUANTITY}-{Config.MAX_QUANTITY} magunia)\n\n"
                response += "0. Rudi Nyuma"
            else:
                response = "CON CHAGUA MAHALI PA KUCHUKUA MIZIGO:\n\n"
                response += "1. Mbalali\n"
                response += "2. Uyole\n"
                response += "3. Kyela\n"
                response += "11. Sehemu nyingine\n"
                response += "0. Rudi Nyuma"
        
        # Destination location selection after pickup location
        elif text.startswith('1*') and len(text.split('*')) == 4:
            parts = text.split('*')
            crop_choice = parts[1]
            quantity = parts[2]
            pickup_choice = parts[3]
            
            if pickup_choice == '0':  # Back to quantity
                crop_name = crops.get(crop_choice, 'Zao')
                response = f"CON WEKA KIASI CHA {crop_name.upper()}:\n\n"
                response += "Andika idadi ya magunia\n"
                response += f"(Kiwango: {Config.MIN_QUANTITY}-{Config.MAX_QUANTITY} magunia)\n\n"
                response += "0. Rudi Nyuma"
            elif pickup_choice == '11':  # Other pickup location
                response = "END HUDUMA BADO Haijafika huko\n\n"
                response += "Huduma hii bado haijapatikana kwa sehemu nyingine.\n"
                response += "Tafadhali chagua kutoka kwenye maeneo yaliyoorodheshwa.\n\n"
                response += "Asante kwa kutumia huduma yetu!"
            else:
                pickup_name = locations.get(pickup_choice, 'Mahali')
                response = f"CON CHAGUA MAHALI MZIGO UNAPOENDA:\n"
                response += f"(Kutoka: {pickup_name})\n\n"
                response += "1. Soweto\n"
                response += "2. Mwanjelwa\n"
                response += "3. Maendeleo\n"
                response += "4. Igurusi\n"
                response += "11. Sehemu nyingine\n"
                response += "0. Rudi Nyuma"
        
        # Final confirmation and order creation
        elif text.startswith('1*') and len(text.split('*')) == 5:
            parts = text.split('*')
            crop_choice = parts[1]
            quantity = parts[2]
            pickup_choice = parts[3]
            destination_choice = parts[4]
            
            if destination_choice == '0':  # Back to pickup location
                response = "CON CHAGUA MAHALI KUCHUKUA MIZIGO:\n\n"
                response += "1. Mbalali \n"
                response += "2. Uyole\n"
                response += "3. Kyela\n"
                response += "5. Sehemu nyingine\n"
                response += "0. Rudi Nyuma"
            elif destination_choice == '11':  # Other destination
                response = "END HUDUMA BADO Haijafika \n\n"
                response += "Huduma hii bado haijapatikana kwa sehemu nyingine.\n"
                response += "Tafadhali chagua kutoka kwenye maeneo yaliyoorodheshwa.\n\n"
                response += "Asante kwa kutumia huduma yetu!"
            elif pickup_choice == destination_choice:  # Same pickup and destination
                response = "END MAKOSA - MAHALI NI SAWA\n\n"
                response += "Mahali pa kuchukua na pa uwasilishaji haviwezi kuwa sawa.\n"
                response += "Tafadhali chagua maeneo tofauti.\n\n"
                response += "Asante kwa kutumia huduma yetu!"
            else:
                # Create order
                track_number = generate_track_number()
                transporter = get_transporter_details()
                
                crop_name = crops.get(crop_choice, 'Zao')
                pickup_name = locations.get(pickup_choice, 'Mahali')
                destination_name = locations.get(destination_choice, 'Mahali')
                
                # Save order
                order_data = {
                    'phone_number': phone_number,
                    'crop': crop_name,
                    'quantity': quantity,
                    'pickup_location': pickup_name,
                    'destination_location': destination_name,
                    'transporter': transporter
                }
                save_order(track_number, order_data)
                
                response = "END UTHIBITISHO - OMBI LIMEPOKELEWA!\n\n"
                response += f"Zao: {crop_name}\n"
                response += f"Kiasi: {quantity} Magunia\n"
                response += f"Kutoka: {pickup_name}\n"
                response += f"Kwenda: {destination_name}\n"
                response += f"Namba ya Ufuatiliaji: {track_number}\n\n"
                response += f"Msafirishaji : {transporter['name']}\n"
                response += f"Mawasiliano: {transporter['phone']}\n"
                response += "Msafirishaji atawasiliana nawe kwa maeleezo ya bei na muda.\n"
                response += "Utapokea ujumbe wa uthibitisho.\n"
                response += "Asante kwa kutumia huduma yetu!"
        
        # Option 2: Track Order
        elif text == '2':
            response = "CON FUATILIA OMBI LAKO\n\n"
            response += "Weka namba ya ufuatiliaji:\n"
            response += "(Mfano: TRK240315001)\n\n"
            response += "0. Rudi Nyuma"
        
        elif text.startswith('2*'):
            track_input = text.split('*')[1].strip().upper()
            
            if track_input == '0':  # Back to main menu
                response = "CON HUDUMA YA USAFIRISHAJI MAZAO\n"
                response += "Karibu! Chagua huduma:\n\n"
                response += "1. Omba Usafiri\n"
                response += "2. Fuatilia Ombi\n"
                response += "3. Mawasiliano\n"
                response += "0. Toka"
            elif track_input.startswith('TRK') and len(track_input) >= 9:
                order = get_order_status(track_input)
                
                if order:
                    # Update status randomly for demo
                    statuses = [
                        "Ombi limepokewa na linatarajiwa kuanza safari",
                        "Msafiri amepokea ombi na ameshaanza safari",
                        "Mizigo iko njiani - eneo la Makambako",
                        # "Mizigo iko karibu na mahali pa utoaji", # Example statuses removed
                        # "Mizigo imefika mahali pa utoaji" # Actual status comes from DB
                    # ]
                    # current_status = random.choice(statuses) # Using actual status from DB
                    db_status = order.get('status', 'Hali haijulikani') # Get status from DB
                    
                    response = f"END HALI YA OMBI: {track_input}\n\n"
                    response += f"Zao: {order.get('crop', 'N/A')}\n"
                    response += f"Kiasi: {order.get('quantity', 'N/A')} Magunia\n"
                    response += f"Kutoka: {order.get('pickup_location', 'N/A')}\n"
                    response += f"Kwenda: {order.get('destination_location', 'N/A')}\n" # Corrected field
                    response += f"Hali: {db_status}\n\n" # Use status from DB
                    response += "MAELEZO YA MSAFIRISHAJI:\n"
                    response += f"Msafirishaji: {order.get('transporter', {}).get('name', 'N/A')}\n"
                    response += f"Mawasiliano: {order.get('transporter', {}).get('phone', 'N/A')}\n\n"
                    response += "Kwa maelezo zaidi wasiliana na Msafirishaji."
                else:
                    response = "END NAMBA HAIJAPATIKANA\n\n"
                    response += "Namba ya ufuatiliaji haipo kwenye mfumo wetu.\n"
                    response += "Tafadhali hakikisha umeweka namba sahihi.\n\n"
                    response += "Asante!"
            else:
                response = "CON NAMBA SI SAHIHI\n\n"
                response += "Namba ya ufuatiliaji si sahihi.\n"
                response += "Tafadhali weka namba sahihi\n"
                response += "(Mfano: TRK240315001)\n\n"
                response += "0. Rudi Nyuma"
        
        # Option 3: Contact Information
        elif text == '3':
            response = "END MAWASILIANO YETU\n\n"
            response += "Ofisi Kuu - Mbeya:\n"
            response += "Simu: +255 25 250 1234\n"
            response += "WhatsApp: +255 754 123 456\n"
            response += "Barua pepe: info@safirimazao.co.tz\n\n"
            response += "Masaa ya kazi:\n"
            response += "Jumatatu - Jumamosi: 7:00 - 18:00\n"
            response += "Jumapili: 8:00 - 14:00\n\n"
            response += "Asante kwa kutumia huduma yetu."
        
        # Option 0: Exit
        elif text == '0':
            response = "END ASANTE KWA KUTUMIA HUDUMA YETU\n\n"
            response += "Huduma ya usafiridhaji mazao kwa watu wote.\n"
            response += "Karibu tena!\n\n"
            response += "Kwa huduma zaidi piga: +255 25 250 1234"
        
        # Handle invalid inputs
        else:
            response = "CON CHAGUO HALIPO\n\n"
            response += "Chaguo ulilochagua halipo.\n"
            response += "Tafadhali jaribu tena na uchague chaguo sahihi.\n\n"
            response += "0. Rudi Nyuma"
        
        # Log the response
        logger.info(f"USSD Response - Session: {session_id}, Response length: {len(response)}")
        
        return response
        
    except Exception as e:
        logger.error(f"Error processing USSD request: {e}")
        return "END Samahani, kuna tatizo la kimfumo. Tafadhali jaribu baadae."

# Admin Web Dashboard APIs
@app.route('/api/orders', methods=['GET'])
def get_all_orders():
    """API endpoint to fetch all orders for the admin dashboard."""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({'error': 'Database connection failed'}), 500

        cursor = conn.cursor(dictionary=True)

        # Join with related tables to get names and other details
        sql = """
        SELECT
            o.track_number, o.phone_number, o.quantity, o.status,
            o.created_at, o.status_updated_at,
            c.name as crop_name, c.id as crop_id,
            pl.name as pickup_location_name, pl.id as pickup_location_id,
            dl.name as destination_location_name, dl.id as destination_location_id,
            t.name as transporter_name, t.phone as transporter_phone,
            t.rating as transporter_rating, t.id as transporter_id,
            o.crop as old_crop, -- Keep old fields for now if needed for data that hasn't been migrated
            o.pickup_location as old_pickup_location,
            o.destination_location as old_destination_location,
            o.transporter_name as old_transporter_name,
            o.transporter_phone as old_transporter_phone,
            o.transporter_rating as old_transporter_rating
        FROM orders o
        LEFT JOIN crops c ON o.crop_id = c.id
        LEFT JOIN locations pl ON o.pickup_location_id = pl.id
        LEFT JOIN locations dl ON o.destination_location_id = dl.id
        LEFT JOIN transporters t ON o.transporter_id = t.id
        ORDER BY o.created_at DESC
        """
        cursor.execute(sql)
        orders_raw = cursor.fetchall()

        orders_processed = []
        for order_row in orders_raw:
            order_dict = dict(order_row) # Convert named tuple/dict from cursor
            if isinstance(order_dict.get('created_at'), datetime):
                order_dict['created_at'] = order_dict['created_at'].isoformat()
            if isinstance(order_dict.get('status_updated_at'), datetime):
                order_dict['status_updated_at'] = order_dict['status_updated_at'].isoformat()

            # Structure related entities for clarity in API response
            order_dict['crop_details'] = {'id': order_dict.pop('crop_id', None), 'name': order_dict.pop('crop_name', None) or order_dict.get('old_crop')}
            order_dict['pickup_location_details'] = {'id': order_dict.pop('pickup_location_id', None), 'name': order_dict.pop('pickup_location_name', None) or order_dict.get('old_pickup_location')}
            order_dict['destination_location_details'] = {'id': order_dict.pop('destination_location_id', None), 'name': order_dict.pop('destination_location_name', None) or order_dict.get('old_destination_location')}
            order_dict['transporter_details'] = {
                'id': order_dict.pop('transporter_id', None),
                'name': order_dict.pop('transporter_name', None) or order_dict.get('old_transporter_name'), # Prioritize joined name
                'phone': order_dict.pop('transporter_phone', None) or order_dict.get('old_transporter_phone'),
                'rating': order_dict.pop('transporter_rating', None) or order_dict.get('old_transporter_rating')
            }
            # Remove redundant old fields from the main dict if they were only used for fallback
            for old_field in ['old_crop', 'old_pickup_location', 'old_destination_location', 'old_transporter_name', 'old_transporter_phone', 'old_transporter_rating']:
                order_dict.pop(old_field, None)

            orders_processed.append(order_dict)

        return jsonify(orders_processed), 200
    except MySQLError as e:
        logger.error(f"Error fetching all orders for admin: {e}")
        return jsonify({'error': 'Failed to fetch orders', 'details': str(e)}), 500
    except Exception as e:
        logger.error(f"Unexpected error fetching all orders: {e}")
        return jsonify({'error': 'An unexpected error occurred', 'details': str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

@app.route('/api/orders/<string:track_number>/status', methods=['PUT'])
def update_order_status_api(track_number):
    """API endpoint to update the status of an order."""
    try:
        data = request.get_json()
        new_status = data.get('status')

        if not new_status:
            return jsonify({'error': 'New status is required'}), 400

        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            if conn is None:
                return jsonify({'error': 'Database connection failed'}), 500

            cursor = conn.cursor()

            # Check if order exists
            cursor.execute("SELECT track_number FROM orders WHERE track_number = %s", (track_number,))
            order_exists = cursor.fetchone()
            if not order_exists:
                return jsonify({'error': 'Order not found'}), 404

            # Update status and status_updated_at
            sql = "UPDATE orders SET status = %s, status_updated_at = %s WHERE track_number = %s"
            current_time = datetime.now()
            cursor.execute(sql, (new_status, current_time, track_number))
            conn.commit()

            if cursor.rowcount > 0:
                logger.info(f"Status for order {track_number} updated to '{new_status}' via API.")

                # Fetch the updated order with joined details to return
                # Close the current cursor and get a dictionary cursor
                if cursor: cursor.close()
                cursor = conn.cursor(dictionary=True)

                fetch_sql = """
                SELECT
                    o.track_number, o.phone_number, o.quantity, o.status,
                    o.created_at, o.status_updated_at,
                    c.name as crop_name, c.id as crop_id,
                    pl.name as pickup_location_name, pl.id as pickup_location_id,
                    dl.name as destination_location_name, dl.id as destination_location_id,
                    t.name as transporter_name, t.phone as transporter_phone,
                    t.rating as transporter_rating, t.id as transporter_id,
                    o.crop as old_crop, o.pickup_location as old_pickup_location,
                    o.destination_location as old_destination_location,
                    o.transporter_name as old_transporter_name,
                    o.transporter_phone as old_transporter_phone,
                    o.transporter_rating as old_transporter_rating
                FROM orders o
                LEFT JOIN crops c ON o.crop_id = c.id
                LEFT JOIN locations pl ON o.pickup_location_id = pl.id
                LEFT JOIN locations dl ON o.destination_location_id = dl.id
                LEFT JOIN transporters t ON o.transporter_id = t.id
                WHERE o.track_number = %s
                """
                cursor.execute(fetch_sql, (track_number,))
                updated_order_raw = cursor.fetchone()

                if updated_order_raw:
                    updated_order_dict = dict(updated_order_raw)
                    if isinstance(updated_order_dict.get('created_at'), datetime):
                        updated_order_dict['created_at'] = updated_order_dict['created_at'].isoformat()
                    if isinstance(updated_order_dict.get('status_updated_at'), datetime):
                        updated_order_dict['status_updated_at'] = updated_order_dict['status_updated_at'].isoformat()

                    updated_order_dict['crop_details'] = {'id': updated_order_dict.pop('crop_id', None), 'name': updated_order_dict.pop('crop_name', None) or updated_order_dict.get('old_crop')}
                    updated_order_dict['pickup_location_details'] = {'id': updated_order_dict.pop('pickup_location_id', None), 'name': updated_order_dict.pop('pickup_location_name', None) or updated_order_dict.get('old_pickup_location')}
                    updated_order_dict['destination_location_details'] = {'id': updated_order_dict.pop('destination_location_id', None), 'name': updated_order_dict.pop('destination_location_name', None) or updated_order_dict.get('old_destination_location')}
                    updated_order_dict['transporter_details'] = {
                        'id': updated_order_dict.pop('transporter_id', None),
                        'name': updated_order_dict.pop('transporter_name', None) or updated_order_dict.get('old_transporter_name'),
                        'phone': updated_order_dict.pop('transporter_phone', None) or updated_order_dict.get('old_transporter_phone'),
                        'rating': updated_order_dict.pop('transporter_rating', None) or updated_order_dict.get('old_transporter_rating')
                    }
                    for old_field in ['old_crop', 'old_pickup_location', 'old_destination_location', 'old_transporter_name', 'old_transporter_phone', 'old_transporter_rating']:
                        updated_order_dict.pop(old_field, None)
                    return jsonify(updated_order_dict), 200
                else: # Should not happen if update was successful
                    return jsonify({'error': 'Failed to retrieve updated order details'}), 500
            else:
                # This case should ideally not be reached if existence check passed and update occurred
                return jsonify({'error': 'Order not found or status not changed'}), 404

        except MySQLError as e:
            logger.error(f"Database error updating status for order {track_number}: {e}")
            if conn:
                conn.rollback()
            return jsonify({'error': 'Database error updating status', 'details': str(e)}), 500
        except Exception as e:
            logger.error(f"Unexpected error updating status for order {track_number}: {e}")
            if conn:
                conn.rollback()
            return jsonify({'error': 'An unexpected error occurred', 'details': str(e)}), 500
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()
    except BadRequest:
        return jsonify({'error': 'Invalid JSON data'}), 400

# --- CRUD APIs for New Entities ---

# Transporters API
@app.route('/api/transporters', methods=['POST'])
def create_transporter():
    conn = None
    cursor = None
    try:
        data = request.get_json()
        if not data or not data.get('name') or not data.get('phone'):
            return jsonify({'error': 'Missing required fields: name and phone'}), 400

        conn = get_db_connection()
        if conn is None: return jsonify({'error': 'Database connection failed'}), 500
        cursor = conn.cursor()

        sql = """INSERT INTO transporters (name, phone, rating, vehicle_details, notes)
                 VALUES (%s, %s, %s, %s, %s)"""
        cursor.execute(sql, (data['name'], data['phone'], data.get('rating'),
                              data.get('vehicle_details'), data.get('notes')))
        conn.commit()
        transporter_id = cursor.lastrowid
        return jsonify({'message': 'Transporter created successfully', 'id': transporter_id}), 201
    except MySQLError as e:
        logger.error(f"Database error creating transporter: {e}")
        if conn: conn.rollback()
        # Check for unique constraint violation (e.g., phone)
        if e.errno == 1062: # Error number for duplicate entry
            return jsonify({'error': 'Duplicate entry, transporter with this phone may already exist.'}), 409
        return jsonify({'error': 'Database error', 'details': str(e)}), 500
    except BadRequest:
        return jsonify({'error': 'Invalid JSON data'}), 400
    except Exception as e:
        logger.error(f"Unexpected error creating transporter: {e}")
        if conn: conn.rollback()
        return jsonify({'error': 'An unexpected error occurred'}), 500
    finally:
        if cursor: cursor.close()
        if conn and conn.is_connected(): conn.close()

@app.route('/api/transporters', methods=['GET'])
def get_transporters():
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        if conn is None: return jsonify({'error': 'Database connection failed'}), 500
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, name, phone, rating, vehicle_details, notes, created_at, updated_at FROM transporters ORDER BY name")
        transporters = cursor.fetchall()
        for t in transporters: # Convert datetime to ISO format
            if isinstance(t.get('created_at'), datetime): t['created_at'] = t['created_at'].isoformat()
            if isinstance(t.get('updated_at'), datetime): t['updated_at'] = t['updated_at'].isoformat()
        return jsonify(transporters), 200
    except MySQLError as e:
        logger.error(f"Database error fetching transporters: {e}")
        return jsonify({'error': 'Database error', 'details': str(e)}), 500
    except Exception as e:
        logger.error(f"Unexpected error fetching transporters: {e}")
        return jsonify({'error': 'An unexpected error occurred'}), 500
    finally:
        if cursor: cursor.close()
        if conn and conn.is_connected(): conn.close()

@app.route('/api/transporters/<int:transporter_id>', methods=['GET'])
def get_transporter(transporter_id):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        if conn is None: return jsonify({'error': 'Database connection failed'}), 500
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, name, phone, rating, vehicle_details, notes, created_at, updated_at FROM transporters WHERE id = %s", (transporter_id,))
        transporter = cursor.fetchone()
        if transporter:
            if isinstance(transporter.get('created_at'), datetime): transporter['created_at'] = transporter['created_at'].isoformat()
            if isinstance(transporter.get('updated_at'), datetime): transporter['updated_at'] = transporter['updated_at'].isoformat()
            return jsonify(transporter), 200
        return jsonify({'error': 'Transporter not found'}), 404
    except MySQLError as e:
        logger.error(f"Database error fetching transporter {transporter_id}: {e}")
        return jsonify({'error': 'Database error', 'details': str(e)}), 500
    except Exception as e:
        logger.error(f"Unexpected error fetching transporter {transporter_id}: {e}")
        return jsonify({'error': 'An unexpected error occurred'}), 500
    finally:
        if cursor: cursor.close()
        if conn and conn.is_connected(): conn.close()

@app.route('/api/transporters/<int:transporter_id>', methods=['PUT'])
def update_transporter(transporter_id):
    conn = None
    cursor = None
    try:
        data = request.get_json()
        if not data: return jsonify({'error': 'No data provided for update'}), 400

        conn = get_db_connection()
        if conn is None: return jsonify({'error': 'Database connection failed'}), 500
        cursor = conn.cursor()

        # Construct SQL query dynamically based on provided fields
        update_fields = []
        update_values = []
        if 'name' in data:
            update_fields.append("name = %s")
            update_values.append(data['name'])
        if 'phone' in data:
            update_fields.append("phone = %s")
            update_values.append(data['phone'])
        if 'rating' in data:
            update_fields.append("rating = %s")
            update_values.append(data['rating'])
        if 'vehicle_details' in data:
            update_fields.append("vehicle_details = %s")
            update_values.append(data['vehicle_details'])
        if 'notes' in data:
            update_fields.append("notes = %s")
            update_values.append(data['notes'])

        if not update_fields:
            return jsonify({'error': 'No valid fields provided for update'}), 400

        update_values.append(transporter_id)
        sql = f"UPDATE transporters SET {', '.join(update_fields)}, updated_at = NOW() WHERE id = %s"

        cursor.execute(sql, tuple(update_values))
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({'error': 'Transporter not found or no new data to update'}), 404
        return jsonify({'message': 'Transporter updated successfully'}), 200
    except MySQLError as e:
        logger.error(f"Database error updating transporter {transporter_id}: {e}")
        if conn: conn.rollback()
        if e.errno == 1062: # Error number for duplicate entry (e.g. phone)
            return jsonify({'error': 'Update failed, phone number may already exist for another transporter.'}), 409
        return jsonify({'error': 'Database error', 'details': str(e)}), 500
    except BadRequest:
        return jsonify({'error': 'Invalid JSON data'}), 400
    except Exception as e:
        logger.error(f"Unexpected error updating transporter {transporter_id}: {e}")
        if conn: conn.rollback()
        return jsonify({'error': 'An unexpected error occurred'}), 500
    finally:
        if cursor: cursor.close()
        if conn and conn.is_connected(): conn.close()

@app.route('/api/transporters/<int:transporter_id>', methods=['DELETE'])
def delete_transporter(transporter_id):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        if conn is None: return jsonify({'error': 'Database connection failed'}), 500
        cursor = conn.cursor()

        # Note: Consider implications of ON DELETE SET NULL for orders.transporter_id
        cursor.execute("DELETE FROM transporters WHERE id = %s", (transporter_id,))
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({'error': 'Transporter not found'}), 404
        return jsonify({'message': 'Transporter deleted successfully'}), 200
    except MySQLError as e:
        # Handle cases where transporter cannot be deleted due to foreign key constraints
        # if not handled by ON DELETE SET NULL or ON DELETE CASCADE (which we are not using here for delete)
        logger.error(f"Database error deleting transporter {transporter_id}: {e}")
        if conn: conn.rollback()
        if e.errno == 1451: # Foreign key constraint fails
             return jsonify({'error': 'Cannot delete transporter, they are referenced in existing orders. Consider deactivating instead.'}), 409
        return jsonify({'error': 'Database error', 'details': str(e)}), 500
    except Exception as e:
        logger.error(f"Unexpected error deleting transporter {transporter_id}: {e}")
        if conn: conn.rollback()
        return jsonify({'error': 'An unexpected error occurred'}), 500
    finally:
        if cursor: cursor.close()
        if conn and conn.is_connected(): conn.close()

# Locations API
@app.route('/api/locations', methods=['POST'])
def create_location():
    conn = None
    cursor = None
    try:
        data = request.get_json()
        if not data or not data.get('name'):
            return jsonify({'error': 'Missing required field: name'}), 400

        location_type = data.get('type', 'both')
        if location_type not in ['pickup', 'destination', 'both']:
            return jsonify({'error': "Invalid type. Must be 'pickup', 'destination', or 'both'."}), 400

        conn = get_db_connection()
        if conn is None: return jsonify({'error': 'Database connection failed'}), 500
        cursor = conn.cursor()

        sql = """INSERT INTO locations (name, type, region, is_active)
                 VALUES (%s, %s, %s, %s)"""
        cursor.execute(sql, (data['name'], location_type, data.get('region'), data.get('is_active', True)))
        conn.commit()
        location_id = cursor.lastrowid
        return jsonify({'message': 'Location created successfully', 'id': location_id}), 201
    except MySQLError as e:
        logger.error(f"Database error creating location: {e}")
        if conn: conn.rollback()
        if e.errno == 1062: # Unique constraint (name, type)
            return jsonify({'error': f"Location with name '{data.get('name')}' and type '{location_type}' may already exist."}), 409
        return jsonify({'error': 'Database error', 'details': str(e)}), 500
    except BadRequest:
        return jsonify({'error': 'Invalid JSON data'}), 400
    except Exception as e:
        logger.error(f"Unexpected error creating location: {e}")
        if conn: conn.rollback()
        return jsonify({'error': 'An unexpected error occurred'}), 500
    finally:
        if cursor: cursor.close()
        if conn and conn.is_connected(): conn.close()

@app.route('/api/locations', methods=['GET'])
def get_locations():
    conn = None
    cursor = None
    try:
        filter_type = request.args.get('type')

        conn = get_db_connection()
        if conn is None: return jsonify({'error': 'Database connection failed'}), 500
        cursor = conn.cursor(dictionary=True)

        query = "SELECT id, name, type, region, is_active, created_at, updated_at FROM locations"
        params = []
        if filter_type:
            if filter_type not in ['pickup', 'destination', 'both']:
                 return jsonify({'error': "Invalid type filter. Must be 'pickup', 'destination', or 'both'."}), 400
            query += " WHERE type = %s OR type = 'both'" # 'both' locations can serve as either
            if filter_type == 'pickup': # if specifically pickup, then type='pickup' or type='both'
                params.append('pickup')
            elif filter_type == 'destination': # if specifically destination, then type='destination' or type='both'
                params.append('destination')
            else: # if 'both' is queried, it means locations explicitly marked as 'both'
                 query = "SELECT id, name, type, region, is_active, created_at, updated_at FROM locations WHERE type = %s"
                 params.append('both')


        query += " ORDER BY name"
        cursor.execute(query, tuple(params) if params else None)

        locations = cursor.fetchall()
        for loc in locations: # Convert datetime to ISO format
            if isinstance(loc.get('created_at'), datetime): loc['created_at'] = loc['created_at'].isoformat()
            if isinstance(loc.get('updated_at'), datetime): loc['updated_at'] = loc['updated_at'].isoformat()
        return jsonify(locations), 200
    except MySQLError as e:
        logger.error(f"Database error fetching locations: {e}")
        return jsonify({'error': 'Database error', 'details': str(e)}), 500
    except Exception as e:
        logger.error(f"Unexpected error fetching locations: {e}")
        return jsonify({'error': 'An unexpected error occurred'}), 500
    finally:
        if cursor: cursor.close()
        if conn and conn.is_connected(): conn.close()

@app.route('/api/locations/<int:location_id>', methods=['GET'])
def get_location(location_id):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        if conn is None: return jsonify({'error': 'Database connection failed'}), 500
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, name, type, region, is_active, created_at, updated_at FROM locations WHERE id = %s", (location_id,))
        location = cursor.fetchone()
        if location:
            if isinstance(location.get('created_at'), datetime): location['created_at'] = location['created_at'].isoformat()
            if isinstance(location.get('updated_at'), datetime): location['updated_at'] = location['updated_at'].isoformat()
            return jsonify(location), 200
        return jsonify({'error': 'Location not found'}), 404
    except MySQLError as e:
        logger.error(f"Database error fetching location {location_id}: {e}")
        return jsonify({'error': 'Database error', 'details': str(e)}), 500
    except Exception as e:
        logger.error(f"Unexpected error fetching location {location_id}: {e}")
        return jsonify({'error': 'An unexpected error occurred'}), 500
    finally:
        if cursor: cursor.close()
        if conn and conn.is_connected(): conn.close()

@app.route('/api/locations/<int:location_id>', methods=['PUT'])
def update_location(location_id):
    conn = None
    cursor = None
    try:
        data = request.get_json()
        if not data: return jsonify({'error': 'No data provided for update'}), 400

        conn = get_db_connection()
        if conn is None: return jsonify({'error': 'Database connection failed'}), 500
        cursor = conn.cursor()

        update_fields = []
        update_values = []
        if 'name' in data:
            update_fields.append("name = %s")
            update_values.append(data['name'])
        if 'type' in data:
            location_type = data['type']
            if location_type not in ['pickup', 'destination', 'both']:
                return jsonify({'error': "Invalid type. Must be 'pickup', 'destination', or 'both'."}), 400
            update_fields.append("type = %s")
            update_values.append(location_type)
        if 'region' in data:
            update_fields.append("region = %s")
            update_values.append(data['region'])
        if 'is_active' in data:
            update_fields.append("is_active = %s")
            update_values.append(bool(data['is_active']))

        if not update_fields:
            return jsonify({'error': 'No valid fields provided for update'}), 400

        update_values.append(location_id)
        sql = f"UPDATE locations SET {', '.join(update_fields)}, updated_at = NOW() WHERE id = %s"

        cursor.execute(sql, tuple(update_values))
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({'error': 'Location not found or no new data to update'}), 404
        return jsonify({'message': 'Location updated successfully'}), 200
    except MySQLError as e:
        logger.error(f"Database error updating location {location_id}: {e}")
        if conn: conn.rollback()
        if e.errno == 1062: # Unique constraint (name, type)
             return jsonify({'error': f"Update failed, location name and type combination may already exist."}), 409
        return jsonify({'error': 'Database error', 'details': str(e)}), 500
    except BadRequest:
        return jsonify({'error': 'Invalid JSON data'}), 400
    except Exception as e:
        logger.error(f"Unexpected error updating location {location_id}: {e}")
        if conn: conn.rollback()
        return jsonify({'error': 'An unexpected error occurred'}), 500
    finally:
        if cursor: cursor.close()
        if conn and conn.is_connected(): conn.close()

@app.route('/api/locations/<int:location_id>', methods=['DELETE'])
def delete_location(location_id):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        if conn is None: return jsonify({'error': 'Database connection failed'}), 500
        cursor = conn.cursor()

        cursor.execute("DELETE FROM locations WHERE id = %s", (location_id,))
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({'error': 'Location not found'}), 404
        return jsonify({'message': 'Location deleted successfully'}), 200
    except MySQLError as e:
        logger.error(f"Database error deleting location {location_id}: {e}")
        if conn: conn.rollback()
        if e.errno == 1451: # Foreign key constraint fails
             return jsonify({'error': 'Cannot delete location, it is referenced in existing orders. Consider deactivating it instead.'}), 409
        return jsonify({'error': 'Database error', 'details': str(e)}), 500
    except Exception as e:
        logger.error(f"Unexpected error deleting location {location_id}: {e}")
        if conn: conn.rollback()
        return jsonify({'error': 'An unexpected error occurred'}), 500
    finally:
        if cursor: cursor.close()
        if conn and conn.is_connected(): conn.close()

# Crops API
@app.route('/api/crops', methods=['POST'])
def create_crop():
    conn = None
    cursor = None
    try:
        data = request.get_json()
        if not data or not data.get('name'):
            return jsonify({'error': 'Missing required field: name'}), 400

        conn = get_db_connection()
        if conn is None: return jsonify({'error': 'Database connection failed'}), 500
        cursor = conn.cursor()

        sql = """INSERT INTO crops (name, description, is_active)
                 VALUES (%s, %s, %s)"""
        cursor.execute(sql, (data['name'], data.get('description'), data.get('is_active', True)))
        conn.commit()
        crop_id = cursor.lastrowid
        return jsonify({'message': 'Crop created successfully', 'id': crop_id}), 201
    except MySQLError as e:
        logger.error(f"Database error creating crop: {e}")
        if conn: conn.rollback()
        if e.errno == 1062: # Unique constraint (name)
            return jsonify({'error': f"Crop with name '{data.get('name')}' may already exist."}), 409
        return jsonify({'error': 'Database error', 'details': str(e)}), 500
    except BadRequest:
        return jsonify({'error': 'Invalid JSON data'}), 400
    except Exception as e:
        logger.error(f"Unexpected error creating crop: {e}")
        if conn: conn.rollback()
        return jsonify({'error': 'An unexpected error occurred'}), 500
    finally:
        if cursor: cursor.close()
        if conn and conn.is_connected(): conn.close()

@app.route('/api/crops', methods=['GET'])
def get_crops():
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        if conn is None: return jsonify({'error': 'Database connection failed'}), 500
        cursor = conn.cursor(dictionary=True)

        # Option to filter by is_active status, e.g., /api/crops?active=true
        is_active_filter = request.args.get('active')
        query = "SELECT id, name, description, is_active, created_at, updated_at FROM crops"
        params = []

        if is_active_filter is not None:
            if is_active_filter.lower() == 'true':
                query += " WHERE is_active = TRUE"
            elif is_active_filter.lower() == 'false':
                query += " WHERE is_active = FALSE"
            # No else, if 'active' param is present but not true/false, ignore it or return error
            # For now, ignoring invalid active filter values and returning all

        query += " ORDER BY name"
        cursor.execute(query, tuple(params)) # No params yet, but good practice

        crops_list = cursor.fetchall()
        for crop_item in crops_list: # Convert datetime to ISO format
            if isinstance(crop_item.get('created_at'), datetime): crop_item['created_at'] = crop_item['created_at'].isoformat()
            if isinstance(crop_item.get('updated_at'), datetime): crop_item['updated_at'] = crop_item['updated_at'].isoformat()
        return jsonify(crops_list), 200
    except MySQLError as e:
        logger.error(f"Database error fetching crops: {e}")
        return jsonify({'error': 'Database error', 'details': str(e)}), 500
    except Exception as e:
        logger.error(f"Unexpected error fetching crops: {e}")
        return jsonify({'error': 'An unexpected error occurred'}), 500
    finally:
        if cursor: cursor.close()
        if conn and conn.is_connected(): conn.close()

@app.route('/api/crops/<int:crop_id>', methods=['GET'])
def get_crop(crop_id):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        if conn is None: return jsonify({'error': 'Database connection failed'}), 500
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, name, description, is_active, created_at, updated_at FROM crops WHERE id = %s", (crop_id,))
        crop_item = cursor.fetchone()
        if crop_item:
            if isinstance(crop_item.get('created_at'), datetime): crop_item['created_at'] = crop_item['created_at'].isoformat()
            if isinstance(crop_item.get('updated_at'), datetime): crop_item['updated_at'] = crop_item['updated_at'].isoformat()
            return jsonify(crop_item), 200
        return jsonify({'error': 'Crop not found'}), 404
    except MySQLError as e:
        logger.error(f"Database error fetching crop {crop_id}: {e}")
        return jsonify({'error': 'Database error', 'details': str(e)}), 500
    except Exception as e:
        logger.error(f"Unexpected error fetching crop {crop_id}: {e}")
        return jsonify({'error': 'An unexpected error occurred'}), 500
    finally:
        if cursor: cursor.close()
        if conn and conn.is_connected(): conn.close()

@app.route('/api/crops/<int:crop_id>', methods=['PUT'])
def update_crop(crop_id):
    conn = None
    cursor = None
    try:
        data = request.get_json()
        if not data: return jsonify({'error': 'No data provided for update'}), 400

        conn = get_db_connection()
        if conn is None: return jsonify({'error': 'Database connection failed'}), 500
        cursor = conn.cursor()

        update_fields = []
        update_values = []
        if 'name' in data:
            update_fields.append("name = %s")
            update_values.append(data['name'])
        if 'description' in data:
            update_fields.append("description = %s")
            update_values.append(data['description'])
        if 'is_active' in data:
            update_fields.append("is_active = %s")
            update_values.append(bool(data['is_active']))

        if not update_fields:
            return jsonify({'error': 'No valid fields provided for update'}), 400

        update_values.append(crop_id)
        sql = f"UPDATE crops SET {', '.join(update_fields)}, updated_at = NOW() WHERE id = %s"

        cursor.execute(sql, tuple(update_values))
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({'error': 'Crop not found or no new data to update'}), 404
        return jsonify({'message': 'Crop updated successfully'}), 200
    except MySQLError as e:
        logger.error(f"Database error updating crop {crop_id}: {e}")
        if conn: conn.rollback()
        if e.errno == 1062: # Unique constraint (name)
             return jsonify({'error': f"Update failed, crop name may already exist."}), 409
        return jsonify({'error': 'Database error', 'details': str(e)}), 500
    except BadRequest:
        return jsonify({'error': 'Invalid JSON data'}), 400
    except Exception as e:
        logger.error(f"Unexpected error updating crop {crop_id}: {e}")
        if conn: conn.rollback()
        return jsonify({'error': 'An unexpected error occurred'}), 500
    finally:
        if cursor: cursor.close()
        if conn and conn.is_connected(): conn.close()

@app.route('/api/crops/<int:crop_id>', methods=['DELETE'])
def delete_crop(crop_id):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        if conn is None: return jsonify({'error': 'Database connection failed'}), 500
        cursor = conn.cursor()

        cursor.execute("DELETE FROM crops WHERE id = %s", (crop_id,))
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({'error': 'Crop not found'}), 404
        return jsonify({'message': 'Crop deleted successfully'}), 200
    except MySQLError as e:
        logger.error(f"Database error deleting crop {crop_id}: {e}")
        if conn: conn.rollback()
        if e.errno == 1451: # Foreign key constraint fails
             return jsonify({'error': 'Cannot delete crop, it is referenced in existing orders. Consider deactivating it instead.'}), 409
        return jsonify({'error': 'Database error', 'details': str(e)}), 500
    except Exception as e:
        logger.error(f"Unexpected error deleting crop {crop_id}: {e}")
        if conn: conn.rollback()
        return jsonify({'error': 'An unexpected error occurred'}), 500
    finally:
        if cursor: cursor.close()
        if conn and conn.is_connected(): conn.close()

# System Settings API
@app.route('/api/system-settings', methods=['GET'])
def get_all_system_settings():
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        if conn is None: return jsonify({'error': 'Database connection failed'}), 500
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT setting_key, setting_value, description, updated_at FROM system_settings")
        settings = cursor.fetchall()
        for s in settings: # Convert datetime to ISO format
            if isinstance(s.get('updated_at'), datetime): s['updated_at'] = s['updated_at'].isoformat()
        return jsonify(settings), 200
    except MySQLError as e:
        logger.error(f"Database error fetching system settings: {e}")
        return jsonify({'error': 'Database error', 'details': str(e)}), 500
    except Exception as e:
        logger.error(f"Unexpected error fetching system settings: {e}")
        return jsonify({'error': 'An unexpected error occurred'}), 500
    finally:
        if cursor: cursor.close()
        if conn and conn.is_connected(): conn.close()

@app.route('/api/system-settings/<string:setting_key>', methods=['GET'])
def get_system_setting(setting_key):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        if conn is None: return jsonify({'error': 'Database connection failed'}), 500
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT setting_key, setting_value, description, updated_at FROM system_settings WHERE setting_key = %s", (setting_key,))
        setting = cursor.fetchone()
        if setting:
            if isinstance(setting.get('updated_at'), datetime): setting['updated_at'] = setting['updated_at'].isoformat()
            return jsonify(setting), 200
        return jsonify({'error': 'System setting not found'}), 404
    except MySQLError as e:
        logger.error(f"Database error fetching system setting {setting_key}: {e}")
        return jsonify({'error': 'Database error', 'details': str(e)}), 500
    except Exception as e:
        logger.error(f"Unexpected error fetching system setting {setting_key}: {e}")
        return jsonify({'error': 'An unexpected error occurred'}), 500
    finally:
        if cursor: cursor.close()
        if conn and conn.is_connected(): conn.close()

@app.route('/api/system-settings/<string:setting_key>', methods=['PUT'])
def update_system_setting(setting_key):
    conn = None
    cursor = None
    try:
        data = request.get_json()
        if not data or 'setting_value' not in data : # description is optional
            return jsonify({'error': 'Missing required field: setting_value'}), 400

        conn = get_db_connection()
        if conn is None: return jsonify({'error': 'Database connection failed'}), 500
        cursor = conn.cursor()

        # Using INSERT ... ON DUPLICATE KEY UPDATE for simplicity (upsert)
        # Requires setting_key to be PRIMARY or UNIQUE for ON DUPLICATE KEY UPDATE to work as expected.
        sql = """INSERT INTO system_settings (setting_key, setting_value, description)
                 VALUES (%s, %s, %s)
                 ON DUPLICATE KEY UPDATE setting_value = VALUES(setting_value), description = VALUES(description), updated_at = NOW()"""

        cursor.execute(sql, (setting_key, data['setting_value'], data.get('description')))
        conn.commit()

        # lastrowid is not reliable for ON DUPLICATE KEY UPDATE.
        # rowcount returns 1 for INSERT, 2 for UPDATE (if data changed), 0 if no change.
        if cursor.rowcount == 0 : # No change, means value was same. Still a success.
             logger.info(f"System setting '{setting_key}' value unchanged.")
             return jsonify({'message': f"System setting '{setting_key}' value unchanged."}), 200
        elif cursor.rowcount == 1: # Inserted
            logger.info(f"System setting '{setting_key}' created successfully.")
            return jsonify({'message': f"System setting '{setting_key}' created successfully."}), 201
        elif cursor.rowcount == 2: # Updated
            logger.info(f"System setting '{setting_key}' updated successfully.")
            return jsonify({'message': f"System setting '{setting_key}' updated successfully."}), 200
        else: # Should not happen with this logic but as a fallback
            logger.info(f"System setting '{setting_key}' processed.")
            return jsonify({'message': f"System setting '{setting_key}' processed."}), 200

    except MySQLError as e:
        logger.error(f"Database error updating system setting {setting_key}: {e}")
        if conn: conn.rollback()
        return jsonify({'error': 'Database error', 'details': str(e)}), 500
    except BadRequest:
        return jsonify({'error': 'Invalid JSON data'}), 400
    except Exception as e:
        logger.error(f"Unexpected error updating system setting {setting_key}: {e}")
        if conn: conn.rollback()
        return jsonify({'error': 'An unexpected error occurred'}), 500
    finally:
        if cursor: cursor.close()
        if conn and conn.is_connected(): conn.close()

# --- Reporting Data API Endpoints ---
@app.route('/api/reports/orders-summary', methods=['GET'])
def get_orders_summary_report():
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        if conn is None: return jsonify({'error': 'Database connection failed'}), 500
        cursor = conn.cursor(dictionary=True)

        # Total orders
        cursor.execute("SELECT COUNT(*) as total_orders FROM orders")
        total_orders = cursor.fetchone()['total_orders']

        # Orders by status
        cursor.execute("SELECT status, COUNT(*) as count FROM orders GROUP BY status")
        orders_by_status = cursor.fetchall()

        return jsonify({
            'total_orders': total_orders,
            'orders_by_status': orders_by_status
        }), 200
    except MySQLError as e:
        logger.error(f"Database error generating orders summary report: {e}")
        return jsonify({'error': 'Database error generating report', 'details': str(e)}), 500
    except Exception as e:
        logger.error(f"Unexpected error generating orders summary report: {e}")
        return jsonify({'error': 'An unexpected error occurred'}), 500
    finally:
        if cursor: cursor.close()
        if conn and conn.is_connected(): conn.close()

@app.route('/api/reports/orders-over-time', methods=['GET'])
def get_orders_over_time_report():
    # Add date range filters later if needed e.g. ?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        if conn is None: return jsonify({'error': 'Database connection failed'}), 500
        cursor = conn.cursor(dictionary=True)

        # Orders grouped by creation date
        # For simplicity, grouping by DATE(created_at). More complex grouping (week, month) can be added.
        sql = """
        SELECT DATE(created_at) as order_date, COUNT(*) as count
        FROM orders
        GROUP BY DATE(created_at)
        ORDER BY order_date ASC
        """
        cursor.execute(sql)
        orders_over_time = cursor.fetchall()

        # Convert date objects to string for JSON
        for item in orders_over_time:
            if isinstance(item.get('order_date'), datetime.date): # cursor returns datetime.date for DATE()
                item['order_date'] = item['order_date'].isoformat()
            elif isinstance(item.get('order_date'), datetime): # just in case
                 item['order_date'] = item['order_date'].date().isoformat()


        return jsonify(orders_over_time), 200
    except MySQLError as e:
        logger.error(f"Database error generating orders over time report: {e}")
        return jsonify({'error': 'Database error generating report', 'details': str(e)}), 500
    except Exception as e:
        logger.error(f"Unexpected error generating orders over time report: {e}")
        return jsonify({'error': 'An unexpected error occurred'}), 500
    finally:
        if cursor: cursor.close()
        if conn and conn.is_connected(): conn.close()


@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Initialize the database connection pool
    init_db_pool()
    
    # Create tables if they don't exist
    # This should be called after pool initialization, as create_tables_if_not_exist uses get_db_connection
    if db_pool: # Only attempt table creation if pool was initialized
        create_tables_if_not_exist()
    else:
        logger.error("Database pool not initialized. Skipping table creation. Application might not work correctly.")

    # For cPanel hosting, use the environment port or default to 5000
    port = int(os.environ.get('PORT', 5000))
    
    # Debug mode should be False in production
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    
    app.run(host="0.0.0.0", port=port, debug=debug_mode)