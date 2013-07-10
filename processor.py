class Processor(object):
    def __init__(self, member_db, netzone_email):
        self._member_db = member_db
        self._netzone_email = netzone_email

    def save_diff_report(self):
        report = self.get_diff_report(show_all=True)
        f = open("tmp/diffs", "w+")
        f.write(report)
        f.close()

    def get_diff_report(self, show_all=False):
        # diff accounts
        num_diffs = 0
        report = ""
        lines = ["Accounts:"]
        accounts = set(self._member_db.email.accounts +
                       self._netzone_email.accounts)
        for account in sorted(accounts):
            if account not in self._member_db.email.accounts:
                # entry to be deleted
                lines.append("R- %s" % account)
                num_diffs += 1
            elif account not in self._netzone_email.accounts:
                # entry to be added
                lines.append("A+ %s" % account)
                num_diffs += 1
            else:
                # entry unchanged
                if show_all:
                    lines.append("   %s" % account)

        if len(lines) == 1:
            lines.append("(no differences)")
        report += "\n".join(lines) + "\n"

        # diff aliases
        lines = ["Aliases:"]
        aliases = set(self._member_db.email.aliases.keys() +
                      self._netzone_email.aliases.keys())
        for alias in sorted(aliases):
            if alias not in self._member_db.email.aliases.keys():
                # entry to be deleted
                lines.append("R- %s: %s" %
                             (alias, self._netzone_email.aliases[alias]))
                num_diffs += 1
            elif alias not in self._netzone_email.aliases.keys():
                # entry to be added
                lines.append("A+ %s: %s" %
                             (alias, self._member_db.email.aliases[alias]))
                num_diffs += 1
            elif self._member_db.email.aliases[alias] != \
                    self._netzone_email.aliases[alias]:
                # entry to be changed
                lines.append(
                    "M- %s: %s" % (alias, self._netzone_email.aliases[alias]))
                lines.append("M+ %s: %s" %
                             (alias, self._member_db.email.aliases[alias]))
                num_diffs += 1
            else:
                # entry unchanged
                if show_all:
                    lines.append("   %s: %s" %
                                 (alias, self._netzone_email.aliases[alias]))

        if len(lines) == 1:
            lines.append("(no differences)")
        report += "\n".join(lines) + "\n"

        # diff lists
        lines = ["Lists:"]
        lists = set(self._member_db.email.lists.keys() +
                    self._netzone_email.lists.keys())
        for list_name in sorted(lists):
            if list_name not in self._member_db.email.lists.keys():
                # entry to be deleted
                lines.append("R- %s:" % list_name)
                num_diffs += 1
                for recipient in self._netzone_email.lists[list_name]:
                    lines.append("R-     %s" % recipient)
                    num_diffs += 1
            elif list_name not in self._netzone_email.lists.keys():
                # entry to be added
                lines.append("A+ %s:" % list_name)
                for recipient in self._member_db.email.lists[list_name]:
                    lines.append("A+     %s" % recipient)
                    num_diffs += 1
            elif self._member_db.email.lists[list_name] != \
                    self._netzone_email.lists[list_name]:
                # entry to be changed
                lines.append("M  %s:" % list_name)
                recipients = set(self._member_db.email.lists[list_name] +
                                 self._netzone_email.lists[list_name])
                for recipient in sorted(recipients):
                    if recipient not in self._member_db.email.lists[list_name]:
                        lines.append("M-     %s" % recipient)
                        num_diffs += 1
                    elif recipient not in self._netzone_email.lists[list_name]:
                        lines.append("M+     %s" % recipient)
                        num_diffs += 1
                    else:
                        if show_all:
                            lines.append("M      %s" % recipient)
            else:
                # entry unchanged
                if show_all:
                    lines.append("   %s:" % list_name)
                    for recipient in self._netzone_email.lists[list_name]:
                        lines.append("       %s" % recipient)

        if len(lines) == 1:
            lines.append("(no differences)")
        report += "\n".join(lines)+ "\n"
        self._num_diffs = num_diffs
        return report

    def sync(self):
        # accounts
        accounts = set(self._member_db.email.accounts +
                       self._netzone_email.accounts)
        for account in sorted(accounts):
            if account not in self._member_db.email.accounts:
                # entry to be deleted
                self._netzone_email.del_account(account)
            elif account not in self._netzone_email.accounts:
                # entry to be added
                self._netzone_email.add_account(
                    account, self._member_db.email.accounts[account])

        # aliases
        aliases = set(self._member_db.email.aliases.keys() +
                      self._netzone_email.aliases.keys())
        for alias in sorted(aliases):
            if alias not in self._member_db.email.aliases.keys():
                # entry to be deleted
                self._netzone_email.del_alias(alias)
            elif alias not in self._netzone_email.aliases.keys():
                # entry to be added
                self._netzone_email.add_alias(
                    alias, self._member_db.email.aliases[alias])
            elif self._member_db.email.aliases[alias] != \
                    self._netzone_email.aliases[alias]:
                # entry to be changed
                self._netzone_email.change_alias(
                    alias, self._member_db.email.aliases[alias])

        # lists
        lists = set(self._member_db.email.lists.keys() +
                    self._netzone_email.lists.keys())
        for list_name in sorted(lists):
            if list_name not in self._member_db.email.lists.keys():
                # entry to be deleted
                self._netzone_email.del_list(list_name)
            elif list_name not in self._netzone_email.lists.keys():
                # entry to be added
                self._netzone_email.add_list(
                    list_name, self._member_db.email.lists[list_name])
            elif self._member_db.email.lists[list_name] != \
                    self._netzone_email.lists[list_name]:
                # entry to be changed
                self._netzone_email.change_list(
                    list_name, self._member_db.email.lists[list_name])
