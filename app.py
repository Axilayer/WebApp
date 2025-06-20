from flask import Flask, render_template, request, send_from_directory, jsonify
import os
import whisper
import spacy
from transfer_files_through_wifi import list_files, connect_to_wifi, download_file

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

MODEL = whisper.load_model("base")  # Load Whisper model

# Load NLP models
nlp = spacy.load("en_core_web_sm")
med7 = spacy.load("en_core_med7_lg")

# Define colors for entity labels
col_dict_med = {
    label: color for label, color in zip(
        med7.pipe_labels['ner'], 
        ['blue', 'yellow', 'green', 'red', 'purple', 'darkblue', 'darkred']
    )
}

col_dict_ner = {
    # "DATE": "magenta",
}

@app.route("/")
def home():
    return render_template("login.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Handle login logic here (e.g., authentication)
        return render_template("dashboard.html")
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/ehr_fisr_page")
def ehr_fisr_page():
    return render_template("ehr_fisr_page.html")

@app.route("/hospital_notification")
def hospital_notification():
    return render_template("hospital_notification.html")

@app.route("/inventory_management")
def inventory_management():
    return render_template("inventory_management.html")

@app.route("/dosage_protocol")
def dosage_protocol():
    return render_template("dosage_protocol.html")

@app.route("/settings")
def settings():
    return render_template("settings.html")

@app.route("/ehr_form")
def ehr_form():
    return render_template("ehr_form.html")

@app.route("/record_audio")
def record_audio():
    return render_template("record_audio.html")

@app.route("/save_audio", methods=["POST"])
def save_audio():
    if "audio" in request.files:
        audio_file = request.files["audio"]
        audio_path = os.path.join(UPLOAD_FOLDER, "recording.wav")
        audio_file.save(audio_path)
        return jsonify({"success": True, "message": "Audio saved successfully!"}), 200
    return jsonify({"success": False, "message": "No audio file received."}), 400

@app.route("/upload_audio", methods=["POST"])
def upload_audio():
    """Upload audio from file input"""
    if "audio" in request.files:
        audio_file = request.files["audio"]
        audio_path = os.path.join(UPLOAD_FOLDER, "uploaded_audio.wav")
        audio_file.save(audio_path)
        return jsonify({"success": True, "message": "Audio uploaded successfully!"}), 200
    return jsonify({"success": False, "message": "No audio file received."}), 400    

@app.route("/transcribe_audio", methods=["POST"])
def transcribe_audio():
    """Transcribe the most recently recorded/uploaded audio"""
    audio_path = os.path.join(UPLOAD_FOLDER, "recording.wav")  # Default: last recorded
    uploaded_audio_path = os.path.join(UPLOAD_FOLDER, "uploaded_audio.wav")

    if os.path.exists(uploaded_audio_path):  # Prefer uploaded audio if available
        audio_path = uploaded_audio_path

    if not os.path.exists(audio_path):
        return "No audio found for transcription", 400

    result = MODEL.transcribe(audio_path)  # Transcribe audio using Whisper
    transcript = result["text"]

    doc_prop = nlp(transcript)
    doc_med = med7(transcript)

    ent_dict = {}
    for ent in doc_med.ents:
        # tokens = ent.text.lstrip().rstrip().split(' ')
        # for token in tokens:
        #     ent_dict[token] = ent.label_
        ent_dict[ent.text] = ent.label_
    
    # Generate colored HTML text for the transcription
    colored_text = ""

    for token in doc_prop:
        word = token.text
        if word in ent_dict:  # Medical entity detected
            color = col_dict_med.get(ent_dict[word], "gold")
            colored_text += f'<span style="color:{color}; font-weight:bold;">{word}</span> '
        elif token.ent_type_:  # General named entity detected
            color = col_dict_ner.get(token.ent_type_, "darkgreen")
            colored_text += f'<span style="color:{color}; font-weight:bold;">{word}</span> '
        else:  # Normal text
            colored_text += f"{word} "

    return render_template("transcription_result.html", transcript=colored_text, col_dict_med=col_dict_med, 
    col_dict_ner=col_dict_ner)

@app.route("/download_transcribe_audio", methods=["POST"])
def download_audio():
    print("\n🔄 Connecting to XIAO ESP32S3 Wi-Fi...")
    connect_to_wifi()
    
    print("\n📋 Listing files from ESP32S3 SD card...\n")
    files = list_files()
    
    filename = files[-1]
    # download last file
    download_file(files[-1])
    os.rename(filename, os.path.join(UPLOAD_FOLDER, "recording.wav"))
    return transcribe_audio()

@app.route("/uploads/<filename>")
def uploaded_file(filename):
    """Serve uploaded files"""
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == "__main__":
    app.run(debug=True, port=5050)