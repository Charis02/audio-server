db = db.getSiblingDB('audio-files');
db.audio_files.drop();

db.audio_files.insert({
    "id": "1",
    "title": "The Beatles - Yesterday",
});