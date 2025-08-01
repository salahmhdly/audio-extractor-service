import os
from flask import Flask, request, redirect, url_for, send_from_directory, render_template_string
import subprocess

# إعداد تطبيق فلاسك
app = Flask(__name__)

# تحديد مجلد لرفع الملفات وحفظ النتائج
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# دالة فصل الصوت (نفس الكود السابق مع تعديل بسيط)
def extract_audio(video_path, audio_path):
    try:
        command = f"ffmpeg -i \"{video_path}\" -vn -acodec libmp3lame -q:a 2 \"{audio_path}\""
        subprocess.run(command, shell=True, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"حدث خطأ أثناء تنفيذ FFmpeg: {e}")
        return False

# كود HTML للصفحة الرئيسية (تم دمجه هنا لسهولة الاستخدام)
HTML_TEMPLATE = '''
<!doctype html>
<title>فصل الصوت من الفيديو</title>
<h1>ارفع ملف فيديو لفصل الصوت منه</h1>
<form method=post enctype=multipart/form-data>
  <input type=file name=file>
  <input type=submit value=ارفع>
</form>
'''

# كود HTML لصفحة التحميل
DOWNLOAD_TEMPLATE = '''
<!doctype html>
<title>اكتملت المعالجة</title>
<h1>تم فصل الصوت بنجاح!</h1>
<p><a href="{{ url_for('download_file', filename=filename) }}">اضغط هنا لتحميل الملف الصوتي ({{ filename }})</a></p>
<p><a href="/">العودة للصفحة الرئيسية</a></p>
'''

# المسار الرئيسي للتطبيق (يعرض نموذج الرفع)
@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # التأكد من وجود ملف في الطلب
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        
        if file:
            # حفظ ملف الفيديو المرفوع
            video_filename = file.filename
            video_path = os.path.join(app.config['UPLOAD_FOLDER'], video_filename)
            file.save(video_path)

            # تحديد اسم ومسار الملف الصوتي الناتج
            audio_filename = os.path.splitext(video_filename)[0] + '.mp3'
            audio_path = os.path.join(app.config['UPLOAD_FOLDER'], audio_filename)

            # استدعاء دالة فصل الصوت
            success = extract_audio(video_path, audio_path)

            if success:
                # إذا نجحت العملية، اعرض صفحة التحميل
                return render_template_string(DOWNLOAD_TEMPLATE, filename=audio_filename)
            else:
                return "حدث خطأ أثناء معالجة الملف."

    # إذا كان الطلب GET، اعرض الصفحة الرئيسية
    return render_template_string(HTML_TEMPLATE)

# مسار لتنزيل الملفات
@app.route('/uploads/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

# تشغيل الخادم
if __name__ == '__main__':
    # يعمل على كل الواجهات ويستخدم المنفذ 8080
    app.run(host='0.0.0.0', port=8080, debug=True)
