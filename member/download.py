import logging
import requests

class Homepage(object):
    _base_url = "http://tvuster.ch"

    def __init__(self):
        self._logger = logging.getLogger("tvu_member.download.Homepage")
        self._session = requests.Session()
        self._logged_in = False

    def login(self, username, password):
        self._logger.debug("logging into %s..." % self._base_url)
        data = {
            'name': username,
            'pass': password,
            'form_id': 'user_login',
            'op': 'Anmelden',
        }
        resp = self._session.post(self._base_url + "/user/login", data=data)
        assert resp.reason == "OK"
        self._logged_in = True

    def logout(self):
        self._logger.debug("logging out...")
        resp = self._session.get(self._base_url + "/user/logout")
        assert resp.reason == "OK"
        self._logged_in = False

    def get_mitglieder_csv(self):
        self._logger.debug("getting tvu-mitglieder.csv...")
        resp = self._session.get(
            self._base_url + "/tvu-mitglieder.csv")
        assert resp.reason == "OK"
        return resp.content


def get_mitglieder_csv(username, password):
    h = Homepage()
    h.login(username=username, password=password)
    data = h.get_mitglieder_csv()
    h.logout()
    return data


if __name__ == "__main__":
    data = get_mitglieder_csv()
    f = open("tmp/tvu-mitglieser.csv", "w")
    f.write(data)
    f.close()
