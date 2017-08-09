from flask import Flask
app = Flask('speaker')

app.config.update(dict(
    SECRET_KEY=b'_5#y2L"F4Q8z\n\xec]/'
))
app.config.from_envvar('SPEAKER_SETTINGS', silent=True)

import speaker.speaker