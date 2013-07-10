# -*- coding: utf-8 -*-

import csv
import logging
import pprint

from member import Member


pp = pprint.PrettyPrinter(indent=4)

class Email(object):
    _additional_aliases = {
        "anmeldungen": ["anmeldung@tvuster.ch"],
        "buchholz": ["igs@stadt-uster.ch"],
        "dienstag": ["aktive@tvuster.ch"],
        "freitag": ["aktive@tvuster.ch"],
        "maennerriege": ["peter.sunier@tvuster.ch"],
        "puent": ["bruno.ciccotosto@stadt-uster.ch"],
    }

    def __init__(self):
        self._logger = logging.getLogger("tvu_member.email.Email")

    @property
    def accounts(self):
        return self._accounts

    @property
    def aliases(self):
        return self._aliases

    @property
    def lists(self):
        return self._lists

    def parse(self, filename):
        self._logger.debug("parsing '%s'..." % filename)
        csvfile = open(filename)
        try:
            dialect = csv.Sniffer().sniff(csvfile.read(1024))
            csvfile.seek(0)
            reader = csv.reader(csvfile, dialect)

            accounts = []
            aliases = {}
            lists = {}
            for i, row in enumerate(reader):
                fields = row
                if i == 0:
                    heading_fields = fields
                    continue

                data = dict(zip(heading_fields, fields))
                member = Member(data)

                # check if email contains tvuster.ch-account
                # (prevent creation of alias to itself)
                email = member.email
                full_tvuster_email = member.tvuster_email + "@tvuster.ch"
                if full_tvuster_email in email:
                    email.remove(full_tvuster_email)
                    accounts.append(member.tvuster_email)

                # skip members with no email
                if member.email == []:
                    continue

                if email != []:
                    aliases[member.tvuster_email] = email

                for email_alias in member.email_aliases:
                    if aliases.get(email_alias) is None:
                        aliases[email_alias] = []
                    aliases[email_alias].append(
                        member.tvuster_email + "@tvuster.ch")

                for email_list in member.email_lists:
                    if lists.get(email_list) is None:
                        lists[email_list] = []
                    lists[email_list].append(
                        member.tvuster_email + "@tvuster.ch")
        finally:
            csvfile.close()

        aliases.update(self._additional_aliases)

        # sort
        accounts = sorted(accounts)
        for key in aliases.keys():
            aliases[key] = sorted(aliases[key])
        for key in lists.keys():
            lists[key] = sorted(lists[key])

        self._accounts = accounts
        self._aliases = aliases
        self._lists = lists
