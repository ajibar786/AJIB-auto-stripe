from flask import Flask, request, jsonify

app = Flask(__name__)


def validate_card(card_number):
    """Validate card using Luhn algorithm"""
    def luhn_check(card):
        card = str(card).replace(" ", "")
        if not card.isdigit():
            return False
        
        digits = [int(d) for d in card]
        checksum = 0
        for i, digit in enumerate(reversed(digits)):
            if i % 2 == 1:
                digit *= 2
                if digit > 9:
                    digit -= 9
            checksum += digit
        return checksum % 10 == 0
    
    return luhn_check(card_number)


def validate_expiry(month, year):
    """Check if card expiry is valid"""
    try:
        month = int(month)
        year = int(year)
        if month < 1 or month > 12:
            return False
        if year < 25:  # Assuming year is 2-digit format
            return False
        return True
    except:
        return False


def validate_cvv(cvv):
    """Check if CVV is valid"""
    return len(str(cvv)) in [3, 4] and str(cvv).isdigit()


def process_card_validation(card_number, month, year, cvv):
    """Process card and return Approved/Declined"""
    if not validate_card(card_number):
        return 'Declined', 'Invalid card number (Luhn check failed)'
    
    if not validate_expiry(month, year):
        return 'Declined', 'Card expired or invalid expiry'
    
    if not validate_cvv(cvv):
        return 'Declined', 'Invalid CVV'
    
    # Card is valid - Approve it
    return 'Approved', 'Card processed successfully'


@app.route('/')
def index():
    return 'Hello from Flask!'


@app.route('/card', methods=['POST'])
def process_card():
    try:
        data = request.get_json()
        card_number = data.get('card_number')
        month = data.get('month')
        year = data.get('year')
        cvv = data.get('cvv')
        
        if not all([card_number, month, year, cvv]):
            return jsonify({'error': 'Card number, month, year, and CVV required'}), 400
        
        status, message = process_card_validation(card_number, month, year, cvv)
        
        return jsonify({
            'status': status,
            'message': message,
            'card_number': card_number[-4:],
            'response': status
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/card/<card_number>/<month>/<year>/<cvv>', methods=['GET'])
def process_card_get(card_number, month, year, cvv):
    try:
        status, message = process_card_validation(card_number, month, year, cvv)
        
        return jsonify({
            'status': status,
            'message': message,
            'card_number': card_number[-4:],
            'response': status,
            'expiry': f'{month}/{year}'
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/card/<path:card_data>', methods=['GET'])
def process_card_pipe(card_data):
    try:
        # Handle pipe-separated format: card|month|year|cvv
        if '|' in card_data:
            parts = card_data.split('|')
            if len(parts) >= 4:
                card_number = parts[0]
                month = parts[1]
                year = parts[2]
                cvv = parts[3]
                
                status, message = process_card_validation(card_number, month, year, cvv)
                
                return jsonify({
                    'status': status,
                    'message': message,
                    'card_number': card_number[-4:],
                    'response': status,
                    'expiry': f'{month}/{year}'
                }), 200
        
        return jsonify({'error': 'Invalid card format'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
  import os
  port = int(os.environ.get('PORT', 5000))
  app.run(host='0.0.0.0', port=port, debug=False)
