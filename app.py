from flask import Flask, request, jsonify
import os
import random
import string
import json
from datetime import datetime, timedelta
import logging
from werkzeug.exceptions import BadRequest

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuration
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
    DATABASE_FILE = 'transport_orders.json'
    MAX_QUANTITY = 1000  # Maximum bags allowed
    MIN_QUANTITY = 1     # Minimum bags required

# Initialize app config
app.config.from_object(Config)

# Data storage functions (JSON-based for cPanel compatibility)
def load_orders():
    """Load orders from JSON file"""
    try:
        if os.path.exists(Config.DATABASE_FILE):
            with open(Config.DATABASE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    except Exception as e:
        logger.error(f"Error loading orders: {e}")
        return {}

def save_orders(orders):
    """Save orders to JSON file"""
    try:
        with open(Config.DATABASE_FILE, 'w', encoding='utf-8') as f:
            json.dump(orders, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving orders: {e}")
        return False

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
    """Save order to database"""
    orders = load_orders()
    orders[track_number] = {
        **order_data,
        'created_at': datetime.now().isoformat(),
        'status': 'Ombi limepokelewa na Msafirishaji atawasiliana na wewe hivi karibuni',
        'status_updated_at': datetime.now().isoformat()
    }
    return save_orders(orders)

def get_order_status(track_number):
    """Get order status from database"""
    orders = load_orders()
    return orders.get(track_number)

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
                        "Mizigo iko karibu na mahali pa utoaji",
                        "Mizigo imefika mahali pa utoaji"
                    ]
                    current_status = random.choice(statuses)
                    
                    response = f"END HALI YA OMBI: {track_input}\n\n"
                    response += f"Zao: {order['crop']}\n"
                    response += f"Kiasi: {order['quantity']} Magunia\n"
                    response += f"Kutoka: {order.get('pickup_location', 'N/A')}\n"
                    response += f"Kwenda: {order.get('destination_location', order.get('location', 'N/A'))}\n"
                    response += f"Hali: {current_status}\n\n"
                    response += "MAELEZO YA MSAFIRISHAJI:\n"
                    response += f"Msafirishaji: {order['transporter']['name']}\n"
                    response += f"Mawasiliano: {order['transporter']['phone']}\n\n"
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

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Create orders file if it doesn't exist
    if not os.path.exists(Config.DATABASE_FILE):
        save_orders({})
    
    # For cPanel hosting, use the environment port or default to 5000
    port = int(os.environ.get('PORT', 5000))
    
    # Debug mode should be False in production
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    
    app.run(host="0.0.0.0", port=port, debug=debug_mode)