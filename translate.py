from fastapi import FastAPI, UploadFile
from fastapi.responses import FileResponse
from seamless_communication.models.inference import Translator

import os
import torch
import torchaudio
import uuid

'''
The API endpoint for a requests script to submit a wav file for
translation. Wav files need to be in the correct format as
16khz sample rate, 1 channel, and 16-bit int for best results.


'''

MODEL = "seamlessM4T_large" # Also seamlessM4T_medium and 
VOCODER = "vocoder_36langs"
device = torch.device("cuda:0") if torch.cuda.is_available() else torch.device("cpu")
dtype = torch.float16 if torch.cuda.is_available() else torch.float32

app = FastAPI()

@app.post("/translate/{task_str}/{tgt_lang}/")
async def translate(task_str: str,
                    tgt_lang: str,
                    audio_upload: UploadFile = UploadFile(...)) -> FileResponse:
    
    file_name = str(uuid.uuid4())[0:7] + ".wav"
    file_path = os.path.join(os.path.curdir, file_name)
    with open(file_path, 'wb') as temp_file:
        temp_file.write(await audio_upload.read())

    translator = Translator(MODEL, VOCODER, device, dtype)
    translated_text, waveform, sample_rate, = translator.predict(file_path,
                                                                 task_str=task_str,
                                                                 tgt_lang=tgt_lang,
                                                                 src_lang=None,
                                                                 ngram_filtering=True)
    torchaudio.save(file_path, waveform[0].to(torch.float32).cpu(), sample_rate=sample_rate)

    return FileResponse(path=file_path, filename="downloaded.wav", media_type='audio/wav')