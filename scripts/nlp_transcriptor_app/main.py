from flask import *

app = Flask(__name__)

UPLOAD_FOLDER = './static/uploads'
ALLOWED_EXTENSIONS = {'txt'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/')
def main():
    return render_template("index.html")


def allowed_file(filename: str):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/success_upload', methods=['POST'])
def success():
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


if __name__ == '__main__':
    app.run(host="172.20.67.166", debug=False)
