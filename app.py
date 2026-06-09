from flask import Flask, request, jsonify
import subprocess
import tempfile
import os
import requests

app = Flask(__name__)

@app.route('/editar', methods=['POST'])
def editar_video():
    data = request.json
    file_id = data['file_id']
    titulo = data['titulo']
    token = data['token']

    # Descargar vídeo desde Google Drive
    url = f"https://www.googleapis.com/drive/v3/files/{file_id}?alt=media"
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(url, headers=headers, stream=True)

    input_path = tempfile.mktemp(suffix='.mp4')
    output_path = tempfile.mktemp(suffix='.mp4')

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

    # Subir vídeo editado a Google Drive
    with open(output_path, 'rb') as f:
        video_data = f.read()

    upload_url = "https://www.googleapis.com/upload/drive/v3/files?uploadType=media"
    upload_headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "video/mp4"
    }
    upload_r = requests.post(upload_url, headers=upload_headers, data=video_data)
    new_file_id = upload_r.json()['id']

    # Limpiar archivos temporales
    os.remove(input_path)
    os.remove(output_path)

    return jsonify({"file_id": new_file_id})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
