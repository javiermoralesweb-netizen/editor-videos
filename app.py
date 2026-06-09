from flask import Flask, request, jsonify
import subprocess
import tempfile
import os
import requests

app = Flask(__name__)

@app.route('/editar', methods=['POST'])
def editar_video():
    data = request.json
    web_content_link = data['web_content_link']
    titulo = data['titulo']

    # Descargar vídeo desde Google Drive (enlace público)
    input_path = tempfile.mktemp(suffix='.mp4')
    output_path = tempfile.mktemp(suffix='.mp4')

    r = requests.get(web_content_link, stream=True)
    with open(input_path, 'wb') as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)

    # Tamaño de fuente dinámico
    if len(titulo) < 20:
        fontsize = 70
    elif len(titulo) < 40:
        fontsize = 50
    else:
        fontsize = 35

    # FFmpeg añade texto
    cmd = [
        'ffmpeg', '-i', input_path,
        '-vf', f"drawtext=text='{titulo}':fontcolor=white:fontsize={fontsize}:borderw=3:bordercolor=black:x=(w-text_w)/2:y=h/8:font=Arial",
        '-codec:a', 'copy',
        output_path
    ]
    subprocess.run(cmd, check=True)

    # Leer vídeo editado
    with open(output_path, 'rb') as f:
        video_data = f.read()

    # Limpiar archivos temporales
    os.remove(input_path)
    os.remove(output_path)

    return send_file(output_path, mimetype='video/mp4')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
