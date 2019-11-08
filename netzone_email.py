#!/usr/bin/python
# -*- coding: utf-8 -*-

from BeautifulSoup import BeautifulSoup
import logging
import pprint
import re
import requests

pp = pprint.PrettyPrinter(indent=4)


class NetZoneEmail(object):
    MAX_NUM_ALIASES = 10

    def __init__(self, logindomain, password):
        self._logger = logging.getLogger("netzone_email")
        self._session = Session(logindomain, password)

    @property
    def accounts(self):
        return self._accounts

    @property
    def aliases(self):
        return self._aliases

    @property
    def lists(self):
        return self._mailinglists

    def update(self, categories=None, filter_spec=None):
        if categories is None:
            categories = ["accounts", "aliases", "lists"]

        if not self._session._logged_in:
            self._session.login()

        resp = self._session.get_suburl("")
        data = resp.content
        if "accounts" in categories:
            self.parse_accounts(data)
        if "aliases" in categories:
            self.parse_aliases(data)
        if "lists" in categories:
            self.get_and_parse_lists(data, filter_spec=filter_spec)

    def parse_accounts(self, data):
        self._logger.debug("getting accounts...")
        soup = BeautifulSoup(data)
        table = soup.findAll("table")[0]
        assert table.findPrevious("h4").text == \
u'Postfach (POP3/IMAP) Übersicht:'
        heading_row = table.findAll('tr')[0]
        headings = [x.text for x in heading_row.findAll('th')]
        assert len(headings) == 9
        num_tds_per_row = len(headings) + 1
        tds = table.findAll("td")
        columns = []
        while True:
            chunk = tds[:num_tds_per_row]
            columns.append(chunk)
            tds = tds[num_tds_per_row:]
            if tds == []:
                break
        accounts = []
        for column in columns:
            email_address = str(column[1].strong.string)
            accounts.append(email_address)
        self._accounts = sorted(accounts)

    def parse_aliases(self, data):
        self._logger.debug("getting aliases...")
        soup = BeautifulSoup(data)
        tag = soup.find(text="Neue Weiterleitung/Alias")
        tag.parent[u'href']

        table = soup.findAll("table")[1]
        assert table.findPrevious("h4").text == u'Aliase / Weiterleitungen:'
        heading_row = table.findAll('tr')[0]
        headings = [x.text for x in heading_row.findAll('th')]
        assert len(headings) == 7
        tds = table.findAll("td")
        columns = []
        while True:
            chunk = tds[:len(headings)]
            columns.append(chunk)
            tds = tds[len(headings):]
            if tds == []:
                break

        aliases = dict()
        for column in columns:
            email_address = str(column[1].string).replace(" &nbsp;", "")
            email_address = email_address.split("@")[0]
            match = re.search("^<td>(.*)</td>$", str(column[2]), re.DOTALL)
            forward_addresses = match.group(1)
            forward_addresses = forward_addresses.replace("\n", "")
            forward_addresses = forward_addresses.replace(" ", "")
            forward_addresses = forward_addresses.split("<br/>")
            aliases[email_address] = sorted(forward_addresses[:-1])
        self._aliases = aliases

    def get_and_parse_lists(self, data, filter_spec=None):
        self._logger.debug("getting lists...")
        soup = BeautifulSoup(data)
        table = soup.findAll("table")[2]
        assert table.findPrevious("h4").text == u'Mailinglisten:'
        heading_row = table.findAll('tr')[0]
        headings = [x.text for x in heading_row.findAll('th')]
        assert len(headings) == 5
        tds = table.findAll("td")
        columns = []
        while True:
            chunk = tds[:len(headings)]
            columns.append(chunk)
            tds = tds[len(headings):]
            if tds == []:
                break

        mailinglists = dict()
        for column in columns:
            full_email_address = str(column[1].string).replace(" &nbsp;", "")
            email_address = full_email_address.split("@")[0]
            if filter_spec is not None and filter_spec != email_address:
                continue
            self._logger.debug("getting list '%s'..." % full_email_address)
            resp = self._session.get_suburl(
                "hvml/%s" % full_email_address)
            soup = BeautifulSoup(resp.content)
            table = soup.find("table", {"class" : "dbtable"})
            assert table.findPrevious("h4").text == u'Adressliste Import/Export:'
            heading_row = table.findAll('tr')[0]
            headings = [x.text for x in heading_row.findAll('th')]
            assert len(headings) == 4
            tds = table.findAll("td")
            columns = []
            while True:
                chunk = tds[:len(headings)]
                columns.append(chunk)
                tds = tds[len(headings):]
                if tds == []:
                    break

            recipients = []
            for column in columns:
                try:
                    recipient = str(column[1].text).replace("&nbsp;", "")
                except IndexError:
                    continue
                recipients.append(recipient)

            mailinglists[email_address] = recipients

        self._mailinglists = mailinglists

    def add_alias(self, name, forward_to):
        assert len(forward_to) <= self.MAX_NUM_ALIASES
        self._logger.info("adding alias '%s@tvuster.ch'..." % name)
        data = dict(user=name)
        for index, recipient in enumerate(forward_to, start=1):
            data["forward[%d]" % index] = recipient
        self._session.post_suburl("newalias/save", data=data)

    def del_alias(self, name):
        self._logger.info("deleting alias '%s@tvuster.ch'..." % name)
        self._session.post_suburl(
            "delete/%s@tvuster.ch/deletenow" % name)

    def change_alias(self, name, forward_to):
        assert len(forward_to) <= self.MAX_NUM_ALIASES
        self._logger.info("changing alias '%s@tvuster.ch'..." % name)
        data = dict()
        for index, recipient in enumerate(forward_to, start=1):
            data["forward[%d]" % index] = recipient
        index += 1
        while index <= self.MAX_NUM_ALIASES:
            data["forward[%d]" % index] = ""
            index += 1
        self._session.post_suburl(
            "editalias/%s@tvuster.ch/save" % name, data=data)

    def add_list(self, name, forward_to):
        self._logger.info("adding mailinglist '%s@tvuster.ch'..." % name)
        data = dict(user=name)
        self._session.post_suburl(
            "newmllist/save", data=data)

        data = dict(
            listname=name.title(),
            owner="admin@tvuster.ch",
            allowedtosend="all",
            allowedtosubscribe="all",
            moderated=0,
            responseto="from",
            listnameinsubject=0,
            setfrom=0,
            setto=0,
            maxscore=5,
            sendremovelist=0,
            phpinterface=0,
            phpkey="",
        )
        self._session.post_suburl(
            "hvml/%s@tvuster.ch/save" % name, data=data)

        data = dict(
            MAX_FILE_SIZE=2000000,
            clear=1,
        )
        f = open("tmp/recipients.txt", "wb")
        f.write("\n".join(forward_to))
        f.close()
        files = dict(userfile=open("tmp/recipients.txt", "rb"))
        self._session.post_suburl(
            "hvml/%s@tvuster.ch/upload" % name, data=data,
            files=files)

    def change_list(self, name, forward_to):
        self._logger.info("changing mailinglist '%s@tvuster.ch'..." % name)
        data = dict(
            MAX_FILE_SIZE=2000000,
            clear=1,
        )
        f = open("tmp/recipients.txt", "wb")
        f.write("\n".join(forward_to))
        f.close()
        files = dict(userfile=open("tmp/recipients.txt", "rb"))
        self._session.post_suburl(
            "hvml/%s@tvuster.ch/upload" % name, data=data,
            files=files)

    def del_list(self, name):
        self._logger.info("deleting mailinglist '%s@tvuster.ch'..." % name)
        self._session.post_suburl(
            "delete/%s@tvuster.ch/deletenow" % name)


class Session(requests.Session):
    _base_url = "https://ssl.hostpark.net/nc/m/tvuster.ch/2169/"

    def __init__(self, logindomain, password):
        self._logger = logging.getLogger("netzone_email.Session")
        self._logindomain = logindomain
        self._password = password
        requests.Session.__init__(self)
        self._logged_in = False

    def __del__(self):
        if self._logged_in:
            self.logout()

    def login(self):
        self._logger.debug("logging into %s..." % self._base_url)
        data = dict(
            logindomain=self._logindomain,
            password=self._password,
            Login="Einloggen",
        )
        resp = self.post_suburl("", data=data)
        assert resp.content == \
'<html><head><script>window.top.location.href="index.php"</script></head>\n'
        self._logged_in = True

    def logout(self):
        self._logger.debug("logging out...")
        params = dict(Login=1)
        self.get_suburl("index.php", params=params)
        self._logged_in = False

    def get_suburl(self, sub_url, **kwargs):
        resp = self.get(self._base_url + sub_url, **kwargs)
        resp.raise_for_status()
        return resp

    def post_suburl(self, sub_url, **kwargs):
        resp = self.post(self._base_url + sub_url, **kwargs)
        resp.raise_for_status()
        return resp
