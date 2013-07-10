#!/usr/bin/env python

import argparse
import ConfigParser
import logging
import os
import re
import sys

from common import setup_logging
from member.database import Database
from netzone_email import NetZoneEmail
from processor import Processor


def main():
    parser = argparse.ArgumentParser(
        description="tvuster.ch email address tool.")
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="be verbose and print debug messages as well")
    parser.add_argument(
        "--no-download", "-n", action="store_false", dest="download",
        help="do not download data from tvuster.ch (use last downloaded)")
    parser.add_argument(
        "--show-all", "-a", action="store_true",
        help="show all entries, even unchanged ones")
    parser.add_argument(
        "mode", metavar="<mode>", choices=["diff", "sync", "diff-and-sync"],
        default="diff-and-sync", nargs="?",
        help="'diff', 'sync' or 'diff-and-sync' (default=diff-and-sync)")

    args = parser.parse_args()

    setup_logging(args.verbose)

    logger = logging.getLogger()
    logger.debug("command-line: '%s'" % " ".join(sys.argv))
    logger.debug("args: %s" % args)

    config = ConfigParser.ConfigParser()
    config.read(".config")
    tvusterch_username = config.get("tvuster.ch", "Username")
    tvusterch_password = config.get("tvuster.ch", "Password")
    netzone_logindomain = config.get("netzone", "LoginDomain")
    netzone_password = config.get("netzone", "Password")

    logger.info("loading Member-DB...")
    member_db = Database()
    member_db.load(update=args.download, username=tvusterch_username, password=tvusterch_password)
    logger.info("loading NetZone-Data... (takes about 30 seconds)")
    netzone_email = NetZoneEmail(logindomain=netzone_logindomain, password=netzone_password)
    netzone_email.update()

    processor = Processor(member_db, netzone_email)
    processor.save_diff_report()

    report = processor.get_diff_report(show_all=args.show_all)
    if args.mode == "diff":
        print report
    elif args.mode == "sync":
        processor.sync()
    elif args.mode == "diff-and-sync":
        print report
        if processor._num_diffs > 0:
            resp = raw_input("Shall the previous differences be synced? [y]/n ")
            if resp.lower() in ["", "y", "yes"]:
                processor.sync()

    logger.info("done")


if __name__ == '__main__':
    # make script location current working directory (resolve symlinks)
    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    main()
