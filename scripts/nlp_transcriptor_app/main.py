from flask import *

app = Flask(__name__)

UPLOAD_FOLDER = './static/uploads'
ALLOWED_EXTENSIONS = {'txt'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

model_dict = {
    "1": "seq2seq",
    "2": "transformer",
    "3": "self-attention"
}


@app.route('/')
def main():
    return render_template("index.html")


def allowed_file(filename: str):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/success_upload', methods=['POST'])
def success_upload():
    if request.method == 'POST':
        f = request.files['file']
        if allowed_file(f.filename):
            f.save(f.filename)
            content: list = []
            with open(f.filename, "r") as file_:
                lines = file_.readlines()
                for line in lines:
                    content.append(line)
        else:
            return render_template("error.html", error_text="Файл неверного формата")
        return render_template("success_upload.html", name=f.filename, lines=content)

@app.route('/transcription', methods=['POST'])
def transcribe():
    if request.method == 'POST':
        model = request.form.get("tr_model")

        return render_template("transcription.html", model=model, model_name=model_dict[model])


if __name__ == '__main__':
    app.run(host="172.20.67.166", debug=True)
