FROM python:3.6-alpine
RUN mkdir /app
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt
RUN cp settings.example.py settings.py
EXPOSE 5000