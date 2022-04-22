db = db.getSiblingDB('audio_db');
db.files.drop();

db.files.insert({
    "id": "1",
    "title": "The Beatles - Yesterday",
});