from flask import Flask, render_template, request, redirect
import speech_recognition as sr 
import os 
from pydub import AudioSegment
from pydub.silence import split_on_silence
from gingerit.gingerit import GingerIt
from flask import jsonify

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])


def index():
    transcript = ""
    text = ""
    result=""
    l = ""
    mis = 0
    if request.method == "POST":
        print("FORM DATA RECEIVED")

        if "file" not in request.files:
            return redirect(request.url)

        file = request.files["file"]
        if file.filename == "":
            return redirect(request.url)

        if file:
            r = sr.Recognizer()
            sound = AudioSegment.from_wav(file)  
            chunks = split_on_silence(sound,
                min_silence_len = 500,
                silence_thresh = sound.dBFS-14,
                keep_silence=500,
            )
            folder_name = "audio-chunks"
            if not os.path.isdir(folder_name):
                os.mkdir(folder_name)
            for i, audio_chunk in enumerate(chunks, start=1):
                chunk_filename = os.path.join(folder_name, f"chunk{i}.wav")
                audio_chunk.export(chunk_filename, format="wav")
                with sr.AudioFile(chunk_filename) as source:
                    audio_listened = r.record(source)
                    try:
                        text = r.recognize_google(audio_listened)
                        #return jsonify(result={"status": 200})
                    except sr.UnknownValueError as e:
                        print("Error:", str(e))
                    else:
                        text = f"{text.capitalize()}. "
                        print(chunk_filename, ":", text)
                        transcript += text
            parser = GingerIt()
            k=parser.parse(transcript)
            print(k)
            text=k['text']
            result = k['result']
            l=k['corrections']
            mis = len(l)
           

    return render_template('index.html',transcript=transcript, result=result , l=l , mis=mis)


if __name__ == "__main__":
    app.run(debug=True, threaded=True)
