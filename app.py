# =================================================
#          الكود النهائي لملف app.py
# =================================================
import os
from flask import Flask, request, redirect, url_for, send_from_directory, render_template_string
from flask_cors import CORS  # <-- 1. استيراد المكتبة
import subprocess

# إعداد تطبيق فلاسك
app = Flask(__name__)
CORS(app)  # <-- 2. تفعيل السماح بالطلبات من أي مصدر

# تحديد مجلد لرفع الملفات وحفظ النتائج
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# دالة فصل الصوت (تبقى كما هي)
def extract_audio(video_path, audio_path):
    try:
        # استخدام علامات الاقتباس حول المسارات للتعامل مع الأسماء التي تحتوي على مسافات
        command = f"ffmpeg -i \"{video_path}\" -y -vn -acodec libmp3lame -q:a 2 \"{audio_path}\""
        # -y للموافقة على الكتابة فوق الملفات الموجودة
        subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        return True, None
    except subprocess.CalledProcessError as e:
        # طباعة الخطأ من ffmpeg لمساعدتنا على التشخيص
        print(f"حدث خطأ أثناء تنفيذ FFmpeg: {e.stderr}")
        return False, e.stderr

# المسار الرئيسي للتطبيق (يعالج طلبات رفع الملفات)
@app.route('/', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "لم يتم إرسال أي ملف", 400
        
    file = request.files['file']
    if file.filename == '':
        return "لم يتم اختيار أي ملف", 400
        
    if file:
        video_filename = file.filename
        video_path = os.path.join(app.config['UPLOAD_FOLDER'], video_filename)
        file.save(video_path)

        audio_filename = os.path.splitext(video_filename)[0] + '.mp3'
        audio_path = os.path.join(app.config['UPLOAD_FOLDER'], audio_filename)

        success, error_message = extract_audio(video_path, audio_path)

        if success:
            # إذا نجحت العملية، أرسل الملف الصوتي مباشرة
            return send_from_directory(app.config['UPLOAD_FOLDER'], audio_filename, as_attachment=True)
        else:
            # إذا فشلت، أرسل رسالة خطأ واضحة
            return f"فشل في معالجة الفيديو. خطأ FFmpeg: {error_message}", 500

# تشغيل الخادم
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

