import os
from dotenv import load_dotenv
import requests
import deepl
import logging
from logging.handlers import RotatingFileHandler

# Load environment variables from .env file
load_dotenv()

# Initialize logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# Create console handler
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)

# Create file handler (rotate logs)
log_file_path = 'error.log'
fh = RotatingFileHandler(log_file_path, maxBytes=1024*1024, backupCount=5)
fh.setFormatter(formatter)
logger.addHandler(fh)

def handle_api_error(response):
    # Handle Lokalise API errors based on HTTP status code
    error_message = response.json().get('error', {}).get('message', 'Unknown error')
    status_code = response.status_code

    if 400 <= status_code < 500:
        logger.error(f"Client error: {status_code} - {error_message}")
    elif 500 <= status_code < 600:
        logger.error(f"Server error: {status_code} - {error_message}")
    else:
        logger.error(f"Unexpected error: {status_code} - {error_message}")

def fetch_all_keys(lokalise_base_url, lokalise_headers):
    all_keys = []
    page = 1

    while True:
        try:
            response = requests.get(
                f"{lokalise_base_url}/keys",
                headers=lokalise_headers,
                params={
                    "include_translations": "1",
                    "filter_untranslated": "1",
                    "page": page
                }
            )
            response.raise_for_status()  # Raise exception for non-2xx status codes

            data = response.json()
            keys = data.get('keys', [])
            all_keys.extend(keys)

            if len(keys) == 0:
                break  # No more keys to fetch

            page += 1  # Move to the next page

        except requests.RequestException as e:
            logger.error(f"Error fetching keys: {e}")
            break

    return all_keys

def update_translation(lokalise_update_endpoint, payload, lokalise_headers):
    try:
        response = requests.put(lokalise_update_endpoint, json=payload, headers=lokalise_headers)
        response.raise_for_status()  # Raise exception for non-2xx status codes

        return response.json() if response.status_code == 200 else None

    except requests.RequestException as e:
        logger.error(f"Error updating translation: {e}")
        return None

def main():
    try:
        # Retrieve environment variables
        lokalise_api_token = os.getenv("LOKALISE_API_TOKEN")
        deepl_auth_key = os.getenv("DEEPL_AUTH_KEY")

        if not (lokalise_api_token and deepl_auth_key):
            raise ValueError("Environment variables LOKALISE_API_TOKEN and DEEPL_AUTH_KEY are not set.")

        # Define API configuration
        lokalise_project_id = "9763876266290d71498b88.53651952"
        lokalise_base_url = f"https://api.lokalise.com/api2/projects/{lokalise_project_id}"
        lokalise_headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "X-Api-Token": lokalise_api_token
        }
        lokalise_update_translation_url = lokalise_base_url + "/translations/{translation_id}"

        # Fetch all keys
        keys = fetch_all_keys(lokalise_base_url, lokalise_headers)

        # Initialize DeepL translator
        translator = deepl.Translator(deepl_auth_key)

        # Process translations
        for key in keys:
            translations = key.get('translations', [])
            en_translation = next((t for t in translations if t.get('language_iso') == 'en'), None)
            
            untranslated_languages = [
                (t.get('language_iso'), t.get('translation_id'))
                for t in translations
                if t.get('language_iso') != 'en' and t.get('translation') == ''
            ]

            if en_translation and untranslated_languages:
                en_translation_value = en_translation.get('translation')

                for lang_iso, translation_id in untranslated_languages:
                    translated_text = translator.translate_text(en_translation_value, target_lang=lang_iso).text
                    
                    lokalise_update_endpoint = lokalise_update_translation_url.format(translation_id=translation_id)
                    payload = {
                        "translation": translated_text,
                        "is_unverified": True
                    }

                    # Update translation
                    response = update_translation(lokalise_update_endpoint, payload, lokalise_headers)

                    if response:
                        logger.info(f"Translation updated for language '{lang_iso}': '{translated_text}'")
                    else:
                        logger.error(f"Failed to update translation for language '{lang_iso}'")

    except Exception as e:
        logger.exception("An unexpected error occurred")

if __name__ == "__main__":
    main()
