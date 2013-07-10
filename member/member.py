# -*- coding: utf-8 -*-

riegen_mailinglisten_mapping = {
    "LA-Jugend 1": ["jugend1", "alle"],
    "LA-Jugend 2": ["jugend2", "alle"],
    "LA-Jugend 3": ["jugend3", "alle"],
    "LA-Junioren": ["aktive", "alle"],
    "LA-Aktive": ["aktive", "alle"],
    "LA-Aktive-Schnupperer": ["aktive"],
    "LA-Jugend 1-Warteliste": ["jugend1-warteliste"],
    "LA-Jugend 2-Warteliste": ["jugend2-warteliste"],
    "VB-Frauen": ["volleyball", "alle"],
}

funktionen_mailinglisten_mapping = {
    "Anmeldung": [
        "anmeldung",
    ],
    "Fähnrich": [
        "alle",
    ],
    "Passivmitglied": [
        "alle",
    ],
    "TVU-Aktuar": [
        "alle",
        "vorstand",
    ],
    "TVU-Beisitzer": [
        "alle",
        "vorstand",
    ],
    "TVU-DSU": [
        "dsu",
    ],
    "TVU-Ehrenmitglied": [
        "alle",
    ],
    "TVU-Eventmanager": [
        "alle",
        "vorstand",
    ],
    "TVU-Helfer": [
        "alle",
        "helfer",
    ],
    "TVU-Jugendverantwortlicher": [
        "alle",
        "jugileiter",
        "jugend1",
        "jugend1-warteliste",
        "jugend2",
        "jugend2-warteliste",
        "jugend3",
        "leiter",
        "vorstand",
        "zlv",
        "ztv",
    ],
    "TVU-Kassier": [
        "alle",
        "vorstand",
    ],
    "TVU-Leiter-Jugend 1": [
        "alle",
        "jugend1",
        "jugileiter",
    ],
    "TVU-Leiter-Jugend 2": [
        "alle",
        "jugend2",
        "jugileiter",
    ],
    "TVU-Leiter-Jugend 3": [
        "alle",
        "jugend3",
        "jugileiter",
    ],
    "TVU-Leiter-Lauf": [
        "alle",
        "jugend2",
        "jugend3",
        "jugileiter",
    ],
    "TVU-Leiter-Turnen für jedermann": [
        "alle",
    ],
    "TVU-Leiter-Aktive": [
        "aktive",
        "alle",
        "leiter",
    ],
    "TVU-Märtbar": [
        "maertbar",
    ],
    "TVU-Oberturner": [
        "alle",
        "info",
        "leiter",
        "swiss-athletics",
        "vorstand",
        "zlv",
        "ztv",
    ],
    "TVU-Präsident": [
        "alle",
        "info",
        "leiter",
        "swiss-athletics",
        "vorstand",
        "zlv",
        "ztv",
    ],
    "TVU-Revisor": [
        "alle",
    ],
}

funktionen_alias_mapping = {
    "Administrator": "admin",
    "TVU-Präsident": "praesident",
    "TVU-Aktuar": "aktuar",
    "TVU-Oberturner": "oberturner",
    "TVU-Eventmanager": "events",
    "TVU-Jugendverantwortlicher": "jugend",
    "TVU-Kassier": "kassier",
}


class Member(object):
    def __init__(self, data):
        self._data = data

    @property
    def vorname(self):
        return self._data["Vorname"].strip()

    @property
    def nachname(self):
        return self._data["Nachname"].strip()

    @property
    def riege(self):
        return self._data["Riege"].strip()

    @property
    def funktionen(self):
        funktionen = self._data["Funktionen"].strip()
        if funktionen == "":
            return []
        return [item.strip() for item in funktionen.split(",")]

    @property
    def email(self):
        email = self._data["Email"].strip()
        email = email.replace(",", ";")
        if email == "":
            return []
        return [self._to_email(item) for item in email.split(";")]

    @property
    def tvuster_email(self):
        vorname = self.vorname
        vorname = vorname.replace(" ", "_")
        vorname = vorname.replace(".", "")
        nachname = self.nachname
        nachname = nachname.replace(" ", "_")
        nachname = nachname.replace(".", "")
        if vorname == "" or self.nachname == "":
            email = vorname + self.nachname
        else:
            email = vorname + "." + self.nachname
        email = self._to_email(email)
        return email

    @property
    def email_aliases(self):
        aliases = self._data["Email-Alias"]
        aliases = aliases.replace(",", ";")
        if aliases == "":
            aliases = []
        else:
            aliases = [self._to_email(item) for item in aliases.split(";")]

        for funktion in self.funktionen:
            if funktionen_alias_mapping.has_key(funktion):
                aliases.append(funktionen_alias_mapping[funktion])

        return aliases

    @property
    def email_lists(self):
        lists = []
        if riegen_mailinglisten_mapping.has_key(self.riege):
            lists.extend(riegen_mailinglisten_mapping[self.riege])

        for funktion in self.funktionen:
            if funktionen_mailinglisten_mapping.has_key(funktion):
                lists.extend(funktionen_mailinglisten_mapping[funktion])

        return sorted(set(lists))

    def _to_email(self, email):
        email = email.strip()
        email = email.replace(" ", "_")
        email = email.replace("ä", "ae")
        email = email.replace("ö", "oe")
        email = email.replace("ü", "ue")
        email = email.replace("é", "e")
        email = email.replace("è", "e")
        email = email.lower()
        return email
