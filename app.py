from flask import Flask, render_template, request, redirect, url_for, send_file, flash
import os
import shutil
import subprocess
import time

UPLOAD_FOLDER = 'uploads'
RESULT_IMAGE = 'depth_map.png'

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for flash messages
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

from flask import session
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html', result_img=None)

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['image']
    print("File received:", file)
    if file:
        img_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(img_path)
        print("File saved to:", img_path)
        shutil.copy(img_path, 'data/example.jpg')
        print("File copied to data/example.jpg")
        try:
            print("Running depth_test2.py...")
            result = subprocess.run(
                ['python', 'depth_test2.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=600  # seconds
            )
            print("Subprocess finished with return code:", result.returncode)
            if result.returncode != 0:
                print("Subprocess error:", result.stderr.decode())
                flash("Error running depth_test2.py: " + result.stderr.decode())
                return redirect(url_for('index'))
        except subprocess.TimeoutExpired:
            print("Timeout expired")
            flash("Processing timed out. Please try a smaller image.")
            return redirect(url_for('index'))
        except Exception as e:
            print("Unexpected error:", e)
            flash(f"Unexpected error: {e}")
            return redirect(url_for('index'))

        # Wait briefly to ensure file is written
        for _ in range(10):
            if os.path.exists(RESULT_IMAGE):
                print("Result image found.")
                break
            time.sleep(0.2)
        else:
            print("Result image not found.")
            flash("Depth map could not be generated. Please check your input image and try again.")
            return redirect(url_for('index'))

        static_result_path = os.path.join('static', RESULT_IMAGE)
        shutil.move(RESULT_IMAGE, static_result_path)
        print("Result image moved to static folder.")
        return render_template('index.html', result_img=RESULT_IMAGE)
    print("No file uploaded.")
    flash("No file uploaded.")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)