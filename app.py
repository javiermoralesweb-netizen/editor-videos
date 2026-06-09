from flask import Flask, request, jsonify
import subprocess
import tempfile
import os
import requests

app = Flask(__name__)

@app.route('/', methods=['GET'])
def health():
    return 'OK', 200

@app.route('/editar', methods=['POST'])
def editar_video():
    data = request.json
    web_content_link = data['web_content_link']
    titulo = data['titulo']

    input_path = tempfile.mktemp(suffix='.mp4')
    compressed_path = tempfile.mktemp(suffix='_compressed.mp4')
    output_path = tempfile.mktemp(suffix='_output.mp4')

    try:
        # Descargar vídeo
        r = requests.get(web_content_link, stream=True)
        with open(input_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

        # Comprimir vídeo primero para reducir memoria
        compress_cmd = [
            'ffmpeg', '-i', input_path,
            '-vf', 'scale=720:-2',
            '-c:v', 'libx264', '-crf', '28',
            '-preset', 'ultrafast',
            '-c:a', 'aac', '-b:a', '96k',
            '-y', compressed_path
        ]
        subprocess.run(compress_cmd, check=True)

        # Tamaño de fuente dinámico
        if len(titulo) < 20:
            fontsize = 60
        elif len(titulo) < 40:
            fontsize = 45
        else:
            fontsize = 30

        # Limpiar título para FFmpeg
        titulo_clean = titulo.replace("'", "").replace(":", "").replace("\\", "")

        # FFmpeg añade texto
        cmd = [
            'ffmpeg', '-i', compressed_path,
            '-vf', f"drawtext=text='{titulo_clean}':fontcolor=white:fontsize={fontsize}:borderw=3:bordercolor=black:x=(w-text_w)/2:y=h/8",
            '-c:v', 'libx264', '-crf', '28',
            '-preset', 'ultrafast',
            '-c:a', 'copy',
            '-y', output_path
        ]
        subprocess.run(cmd, check=True)

        # Leer y devolver vídeo
        with open(output_path, 'rb') as f:
            video_data = f.read()

        return video_data, 200, {'Content-Type': 'video/mp4'}

    finally:
        for path in [input_path, compressed_path, output_path]:
            if os.path.exists(path):
                os.remove(path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
    
@app.route('/', methods=['GET'])
def health():
    return 'OK', 200
