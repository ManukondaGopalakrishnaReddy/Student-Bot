from fastapi import FastAPI, UploadFile, File, HTTPException
from io import BytesIO
from fastapi.responses import JSONResponse, FileResponse
from studentGPT import *

app = FastAPI()

@app.get("/")
async def read_root():
    return {"Hello": "world"}

@app.post("/questionAnswering")
async def generate_answer(file: UploadFile = File(None), question : str=None):
    if question:
        answer = chatCompletion(question)
    elif file:
        text_from_audio = transcribe_audio(file.filename)
        question = text_from_audio
        answer = chatCompletion(text_from_audio)
    else:
        return JSONResponse(content={"error": "Either provide a question in text or an audio file."}, status_code=400)
    return {"Question":question , "Answer": answer}


@app.get("/references/{answer}")
async def get_references(answer):
    return list_references(answer)

@app.get("/generateImage/{prompt}")
async def generate_image(prompt: str):
    image = generate_the_image(prompt)
    image.save("generated_image.png")
    return FileResponse("generated_image.png")

@app.post("/imageCaptioning")
async def generate_caption(file: UploadFile = File(...)):
    if file:
        with open(file.filename, "wb") as f:
            f.write(file.file.read())
            
        answer = generate_image_caption(file.filename)
        return {"File name": file.filename, "Answer": answer}
    else:
        return JSONResponse(content={"error": "Provide audio file."}, status_code=400)
    
    
@app.get("/text_to_speech/{text}")
async def convert_text_to_speech(text : str):
    try:
        audio_file_path = text_to_speech(text=text)
        return FileResponse(audio_file_path, media_type="audio/wav", filename="generated_audio.wav")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    



