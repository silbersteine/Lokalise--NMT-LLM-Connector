# Lokalise Translation Integration with Neural Machine Translation (NMT) Engine

This script allows you to integrate Lokalise with a 3rd party Machine Translation (NMT) engine (e.g., DeepL) to automatically translate and update localization keys in different languages. Though DeepL is the MT engine I use here, you can modify the script to work with your MT engine of choice. 

## Prerequisites

Before using this script, ensure you have the following:

- Python installed on your system (version 3.x recommended)
- Required Python libraries (`requests`, `deepl`, `dotenv`) installed (`pip install requests deepl python-dotenv`)

## Setup

1.  **Clone the Repository:**

   ````bash
   git clone https://github.com/yourusername/your-repo.git
   cd your-repo
   ````

2. **Obtain DeepL Authentication Key:**

   - Sign up or log in to [DeepL](https://www.deepl.com/).
   - Go to your DeepL account to obtain an authentication key.
   - Set the `DEEPL_AUTH_KEY` environment variable with your DeepL authentication key.

3. **Obtain Lokalise API Token:**

   - Sign up or log in to [Lokalise](https://lokalise.com/).
   - Go to your Lokalise account settings to obtain an API token.
   - Set the `LOKALISE_API_TOKEN` environment variable with your Lokalise API token.

4. **Create .env File and Add Tokens**
    - LOKALISE_API_TOKEN=your_lokalise_api_token_here
    - DEEPL_AUTH_KEY=your_deepl_auth_key_here

## Usage

The script fetches all keys with untranslated translations from your Lokalise project, translates them using DeepL, and updates the translations back in Lokalise.

You can run the script as needed, create a microservice that listens to triggering events in Lokalise like file uploaded to trigger the script, or run it as a cron job from your repo or local device. 

## Configuration Options 

You can customize the behavior of the script by modifying the following parameters:

    - lokalise_project_id: Your Lokalise project ID.
    - lokalise_base_url: Base URL for Lokalise API requests.
    - lokalise_update_translation_url: URL template for updating translations in Lokalise.
    - logger: Configure logging behavior (console output and log file).

## Error Handling

The script handles various API errors and logs them for easy troubleshooting.

## License

This project is licensed under the MIT License.
