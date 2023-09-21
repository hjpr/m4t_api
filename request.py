import argparse
import os
import requests
import uuid

'''
A CLI implementation of Seamless_M4T. This will eventually allow a small device
to send an api request to recieve a translation of a .wav file.

Options for tasks include...
S2ST - Speech to speech translation
S2TT - Speech to text translation
T2ST - Text to speech translation (Not implemented in CLI yet)
T2TT - Text to text translation (Not implemented in CLI yet)
ASR - Automatic speech recognition

Options for languagues can be seen here...
https://github.com/facebookresearch/seamless_communication/tree/main/scripts/m4t/predict
'''

parser = argparse.ArgumentParser()
parser.add_argument("input",
                    type=str,
                    help="Path to audio file to be translated via API.")
parser.add_argument("-t", "--type",
                    type=str,
                    default="s2st",
                    help="Type of translation task.")
parser.add_argument("-l", "--language",
                    type=str,
                    default="spa",
                    help="Three character language code to translate into.")
parser.add_argument("-o", "--output",
                    type=str,
                    default=f"{os.path.curdir}",
                    help="Path to save translated audio file to.")
args = parser.parse_args()

api_url_translate = f"http://127.0.0.1:8000/translate/{args.type}/{args.language}/"

with open(args.input, 'rb') as audio_upload:
    files = {'audio_upload': (os.path.basename(args.input), audio_upload, 'audio/wav')}
    try:
        response = requests.post(api_url_translate, files=files)
        print(response.headers)
        response.raise_for_status()

        file_name = "clientsaved" + str(uuid.uuid4())[0:7] + ".wav"
        file_path = os.path.join(args.output, file_name)
        with open(file_path, 'wb') as output_file:
            output_file.write(response.content)

    except requests.exceptions.HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except requests.exceptions.ConnectionError as conn_err:
        print(f'Connection error occurred: {conn_err}')
    except requests.exceptions.Timeout as timeout_err:
        print(f'Timeout error occurred: {timeout_err}')
    except requests.exceptions.RequestException as req_err:
        print(f'Requests error occurred: {req_err}')