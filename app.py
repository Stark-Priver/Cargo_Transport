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

        # Define the orders table schema
        orders_table_sql = """
        CREATE TABLE IF NOT EXISTS orders (
            track_number VARCHAR(20) PRIMARY KEY,
            phone_number VARCHAR(20),
            crop VARCHAR(100),
            quantity INT,
            pickup_location VARCHAR(255),
            destination_location VARCHAR(255),
            transporter_name VARCHAR(255),
            transporter_phone VARCHAR(20),
            transporter_rating VARCHAR(10),
            status VARCHAR(255),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            status_updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """
        cursor.execute(orders_table_sql)
        conn.commit()
        logger.info("`orders` table checked/created successfully.")

    except MySQLError as e:
        logger.error(f"Error during table creation: {e}")
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
            track_number, phone_number, crop, quantity, pickup_location,
            destination_location, transporter_name, transporter_phone,
            transporter_rating, status, created_at, status_updated_at
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        current_time = datetime.now()
        # Ensure all expected fields are present in order_data and provide defaults if necessary
        data_tuple = (
            track_number,
            order_data.get('phone_number'),
            order_data.get('crop'),
            order_data.get('quantity'),
            order_data.get('pickup_location'),
            order_data.get('destination_location'),
            order_data.get('transporter', {}).get('name'),
            order_data.get('transporter', {}).get('phone'),
            order_data.get('transporter', {}).get('rating'),
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

        sql = "SELECT * FROM orders WHERE track_number = %s"
        cursor.execute(sql, (track_number,))
        order_data = cursor.fetchone()

        if order_data:
            logger.info(f"Order {track_number} fetched successfully from MySQL.")
            # Structure transporter details as expected by the USSD logic
            order_data['transporter'] = {
                'name': order_data.get('transporter_name'),
                'phone': order_data.get('transporter_phone'),
                'rating': order_data.get('transporter_rating')
            }
            # Convert datetime objects to string if necessary for JSON serialization later,
            # though USSD directly uses them. For API consistency, this is good.
            if isinstance(order_data.get('created_at'), datetime):
                order_data['created_at'] = order_data['created_at'].isoformat()
            if isinstance(order_data.get('status_updated_at'), datetime):
                order_data['status_updated_at'] = order_data['status_updated_at'].isoformat()
            return order_data
        else:
            logger.info(f"Order {track_number} not found in MySQL.")
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
        
        # Mapping dictionaries
        crops = {'1': 'Mahindi', '2': 'Viazi', '3': 'Mpunga', '4': 'Zao Jingine'}
        locations = {
            '1': 'Mbeya Mjini', '2': 'Uyole', '3': 'Maendeleo', '4': 'Sisimba',
            '5': 'Itiji', '6': 'Ruanda', '7': 'Tunduma', '8': 'Vwawa',    
            '9': 'Chunya', '10': 'Kyela', '11': 'Sehemu nyingine'
        }
        
        # Main Menu
        if text == '':
            response = "CON Karibu Huduma ya Usafirishaji wa Mazao\n"
            response += "1. Omba Usafiri\n"
            response += "2. Fuatilia Ombi\n"
            response += "3. Mawasiliano\n"
            response += "0. Toka"
        
        # Option 1: Request Transport
        elif text == '1':
            response = "CON CHAGUA ZAO UNALOTAKA KUSAFIRISHA:\n\n"
            response += "1. Mahindi\n"
            response += "2. Viazi\n"
            response += "3. Mpunga\n"
            response += "4. Zao Jingine\n\n"
            response += "0. Rudi Nyuma"
        
        # Quantity input for each crop
        elif text in ['1*1', '1*2', '1*3', '1*4']:
            crop_choice = text.split('*')[1]
            crop_name = crops.get(crop_choice, 'Zao')
            response = f"CON WEKA KIASI CHA {crop_name.upper()}:\n\n"
            response += "Andika idadi ya magunia\n"
            response += f"(Kiwango: {Config.MIN_QUANTITY}-{Config.MAX_QUANTITY} magunia)\n\n"
            response += "0. Rudi Nyuma"
        
        elif text == '1*0':  # Back to main menu from crop selection
            response = "CON HUDUMA YA USAFIRIDHAJI MAZAO\n"
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
        cursor.execute("SELECT * FROM orders ORDER BY created_at DESC")
        orders = cursor.fetchall()

        # Convert datetime objects to ISO format strings for JSON serialization
        for order in orders:
            if isinstance(order.get('created_at'), datetime):
                order['created_at'] = order['created_at'].isoformat()
            if isinstance(order.get('status_updated_at'), datetime):
                order['status_updated_at'] = order['status_updated_at'].isoformat()
            # Add transporter sub-dictionary for consistency if needed by frontend
            order['transporter'] = {
                'name': order.get('transporter_name'),
                'phone': order.get('transporter_phone'),
                'rating': order.get('transporter_rating')
            }


        return jsonify(orders), 200
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
                # Fetch the updated order to return
                cursor.execute("SELECT * FROM orders WHERE track_number = %s", (track_number,))
                updated_order = cursor.fetchone() # Using non-dictionary cursor here, need to map

                # Get column names to create a dict
                column_names = [desc[0] for desc in cursor.description]
                updated_order_dict = dict(zip(column_names, updated_order))

                if isinstance(updated_order_dict.get('created_at'), datetime):
                    updated_order_dict['created_at'] = updated_order_dict['created_at'].isoformat()
                if isinstance(updated_order_dict.get('status_updated_at'), datetime):
                    updated_order_dict['status_updated_at'] = updated_order_dict['status_updated_at'].isoformat()

                updated_order_dict['transporter'] = {
                    'name': updated_order_dict.get('transporter_name'),
                    'phone': updated_order_dict.get('transporter_phone'),
                    'rating': updated_order_dict.get('transporter_rating')
                }
                return jsonify(updated_order_dict), 200
            else:
                # This case should ideally not be reached if existence check passed
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