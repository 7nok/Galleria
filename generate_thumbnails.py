import os
from PIL import Image

UPLOAD_FOLDER = 'static/uploads'
THUMBNAIL_FOLDER = 'static/thumbnails'
SIZE = (200, 200)

if not os.path.exists(THUMBNAIL_FOLDER):
    os.makedirs(THUMBNAIL_FOLDER)

for filename in os.listdir(UPLOAD_FOLDER):
    if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
        original_path = os.path.join(UPLOAD_FOLDER, filename)
        thumbnail_path = os.path.join(THUMBNAIL_FOLDER, filename)
        if not os.path.exists(thumbnail_path):
            try:
                with Image.open(original_path) as img:
                    img.thumbnail(SIZE)
                    img.save(thumbnail_path)
                print(f"Generated thumbnail for {filename}")
            except Exception as e:
                print(f"Error generating thumbnail for {filename}: {e}")