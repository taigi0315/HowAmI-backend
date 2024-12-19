# convert_key.py
import base64
import os
from dotenv import load_dotenv

def convert_key_to_base64():
    # Load .env file
    load_dotenv()
    
    # Get private key from .env
    private_key = os.getenv('FIREBASE_PRIVATE_KEY')
    if not private_key:
        print("Error: FIREBASE_PRIVATE_KEY not found in .env file")
        return
    
    try:
        # Convert to base64
        encoded = base64.b64encode(private_key.encode('utf-8')).decode('utf-8')
        
        print("\n=== Base64 Encoded Private Key ===")
        print(encoded)
        print("\n=== Update your .env file with: ===")
        print("FIREBASE_PRIVATE_KEY_BASE64=" + encoded)
        print("\n=== Remove the original FIREBASE_PRIVATE_KEY ===")
        
    except Exception as e:
        print(f"Error encoding private key: {str(e)}")

if __name__ == "__main__":
    convert_key_to_base64()