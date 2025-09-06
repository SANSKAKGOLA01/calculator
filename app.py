from flask import Flask, render_template, request, jsonify
from flask_cors import CORS  # <-- Add this import
import re
import math

app = Flask(__name__)
CORS(app)  # <-- Add this line

def safe_eval(expression):
    """Safely evaluate mathematical expressions"""
    try:
        # Remove any whitespace
        expression = expression.replace(' ', '')
        
        # Replace display symbols with actual operators
        expression = expression.replace('×', '*').replace('÷', '/').replace('−', '-')
        
        # Validate expression contains only allowed characters
        allowed_chars = set('0123456789+-*/.()')
        if not all(c in allowed_chars for c in expression):
            raise ValueError("Invalid characters")
        
        # Check for balanced parentheses
        if expression.count('(') != expression.count(')'):
            raise ValueError("Unbalanced parentheses")
        
        # Evaluate using a restricted environment
        allowed_names = {
            "__builtins__": {},
            "abs": abs,
            "round": round,
            "min": min,
            "max": max,
        }
        
        result = eval(expression, allowed_names)
        
        # Handle special cases
        if isinstance(result, (int, float)):
            if math.isnan(result) or math.isinf(result):
                raise ValueError("Invalid result")
            return result
        else:
            raise ValueError("Invalid expression")
            
    except ZeroDivisionError:
        raise ValueError("Division by zero")
    except Exception as e:
        raise ValueError("Invalid expression")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        data = request.get_json()
        expression = data.get('expression', '')
        
        if not expression:
            return jsonify({'error': 'No expression provided'}), 400
        
        result = safe_eval(expression)
        
        # Format result
        if isinstance(result, float) and result.is_integer():
            result = int(result)
        
        return jsonify({'result': result})
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Calculation error'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
