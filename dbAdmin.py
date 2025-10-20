

GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent"
def generate_csv(prompt):
    meta_prompt = '''Act as a professional data parser. The accompanying raw data includes the final desired CSV header row on the very first line. Parse the rest of the unstructured text line-by-line, structuring it to fit the specified columns.
        Your entire response MUST be ONLY the raw CSV text. Start directly with the header row provided in the input. Do not add any extra text or formatting.
        data:
        
        '''
    meta_prompt += prompt
    print("prompt", meta_prompt)
    """
    Sends a prompt to the Gemini API to request a full HTML template.
    """
    # NOTE: You should ensure 'requests' and 'GEMINI_URL' are imported/defined
    # and that the API key is secured (e.g., loaded from an environment variable).

    headers = {
        "Content-Type": "application/json"
    }
    
    # It is strongly recommended to use a secured environment variable for your key
    # api_key = os.environ.get("GEMINI_API_KEY") 
    params = {
        # The key should be handled securely, this is just for structure:
        "key": "AIzaSyBwJWClkdIcOZlzvgoFdoj7BaYzEscZ6Zg" 
    }
    
    # The payload is structured to ask the model for a text response
    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": meta_prompt
                    }
                ]
            }
        ]
    }

    try:
        # Assuming GEMINI_URL is defined (e.g., the URL for generateContent)
        # and 'requests' is imported
        response = requests.post(GEMINI_URL, headers=headers, params=params, json=data, timeout=120)
        
        # Raise an exception for bad status codes (4xx or 5xx)
        response.raise_for_status()

        # Extract the HTML text from the response
        response_json = response.json()
        
        # Safely navigate the JSON structure to get the text content
        if 'candidates' in response_json and len(response_json['candidates']) > 0:
            html_template = response_json['candidates'][0]['content']['parts'][0]['text']
        else:
            print("Error: No candidates found in the response.")
            return None
            
    except requests.exceptions.HTTPError as errh:
        print(f"Http Error: {errh}")
        return None
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
        return None
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
        return None
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")
        return None
    except KeyError:
        print("Error: Malformed JSON response from API.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred during API call: {e}")
    #file creation
    response = html_template
    response.replace("'''"," ")
    print(response)
    response = io.StringIO(response)
    df = pd.read_csv(response)
    print(df)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Parsed Data')
    output.seek(0)
    return output
prompt = '''
Product Name, SKU, Purchase Date, Price
Bought a new "Wireless Keyboard Pro" for 55.00 on 2025-08-15. SKU: KBD-99
The office chair, SKU CHR-003, was 189.99 on 08/16/2025.
Subscription renewal for "Cloud Storage 1TB" was $9.99 on the 16th of August 2025.'''
response = generate_csv(prompt)
if response:
    print("status code: 200")
