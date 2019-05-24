import json
from peewee import *


db = SqliteDatabase('web.db')


class JSONField(TextField):
    def db_value(self, value):
        return json.dumps(value)

    def python_value(self, value):
        if value is not None:
            return json.loads(value)


class Entry(Model):
    location = BinaryUUIDField()
    time = DateTimeField()
    data = JSONField()

    class Meta:
        database = db


if __name__ == '__main__':
    db.create_tables([Entry, ])
