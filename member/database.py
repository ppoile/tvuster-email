from datetime import datetime
import os

from download import get_mitglieder_csv
from email import Email


class Database(object):
    _timestamp_format = "%Y%m%d_%H%M"
    _filename_pattern = "tmp/tvu-mitglieder_%s.csv"
    _linkname = "tmp/tvu-mitglieder.csv"

    def __init__(self):
        self._email = Email()

    @property
    def email(self):
        return self._email

    def load(self, update=True, username=None, password=None):
        if update:
            data = get_mitglieder_csv(username, password)
            self._save(data)
        self._email.parse(self._linkname)

    def _save(self, data):
        time_stamp = datetime.now().strftime(self._timestamp_format)
        filename = self._filename_pattern % time_stamp
        f = open(filename, "w")
        f.write(data)
        f.close()
        if os.path.exists(self._linkname):
            os.unlink(self._linkname)
        os.symlink(os.path.basename(filename), self._linkname)


if __name__ == '__main__':
    db = Database()
    db.load(update=False)
