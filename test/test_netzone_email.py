from unittest import TestCase

from netzone_email import NetZoneEmail


class TestNetzoneEmail(TestCase):
    def test_aliases(self):
        netzone_email = NetZoneEmail()
        netzone_email._session.login()

        name = "test-name"
        netzone_email.add_alias(name, ["asdf@gmx.ch"])
        netzone_email.change_alias(name, ["asdf@gmx.net"])
        netzone_email.del_alias(name)

    def test_lists(self):
        netzone_email = NetZoneEmail()
        netzone_email._session.login()

        name = "test-list"
        netzone_email.add_list(name, ["a.b@x.com", "c.d@x.com", "e.f@x.com"])
        netzone_email.change_list(name, ["ab@x.com", "cd@x.com", "e.f@x.com"])
        netzone_email.del_list(name)
