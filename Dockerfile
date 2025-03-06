# Dockerfile בסיסי לאפליקציית Python
FROM python:3.10-alpine

# מגדירים תיקייה פנימית בקונטיינר עבור הקוד
WORKDIR /app

# מעתיקים את קבצי האפליקציה מהתיקייה המקומית app/ לתיקייה /app בתוך הקונטיינר
COPY app/ /app

# אם תרצה בעתיד להתקין ספריות Python (Flask וכו'), תוכל להשתמש ב-requirements.txt. לדוגמה:
# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

# הפקודה שתופעל כשהקונטיינר יתחיל
CMD ["python", "app.py"]

