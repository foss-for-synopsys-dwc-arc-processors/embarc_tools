from __future__ import print_function, division, unicode_literals
import os
import sys
import logging
from ...osp import osp


help = "Get, set or unset osp configuration."

usage = ("\n    embarc config osp --add <name> -m <url> --mr <rev> [<dest>]\n"
         "\n    embarc config osp --add <name> --local [<dest>]\n"
         "    embarc config osp --set <name>\n"
         "    embarc config osp --rename <oldname> <newname>\n"
         "    embarc config osp --remove <name>\n"
         "    embarc config osp --list")


def run(args, remainder=None):
    osppath = osp.OSP()
    if args.add:
        if args.local and (args.manifest_url or args.manifest_rev):
            logging.error("--local cannot be combined with -m or --mr")
            sys.exit(1)
        if args.local:
            osppath.local(args.name, args.local)
        if args.manifest_url:
            rev = args.manifest_rev or "master"
            dest = args.directory or os.path.join(os.getcwd(), "embarc_osp")
            osppath.create(args.add, args.manifest_url, rev, dest)
    elif args.rename:
        if len(remainder) != 1:
            logging.error("usage: embarc config osp --rename <old> <new>")
            sys.exit(1)
        else:
            old = args.directory
            new = remainder[0]
            logging.info("rename {} to {}".format(old, new))
            osppath.rename(old, new)
            args.list = True
    elif args.remove:
        name = args.remove
        logging.info("remove {} ".format(name))
        osppath.remove(name)
        args.list = True
    elif args.set:
        logging.info("set %s as global EMBARC_ROOT" % args.set)
        osppath.set_global(args.set)
    else:
        if remainder:
            logging.error("usage: " + usage)
            sys.exit(1)

    if args.list:
        logging.info("current recored embARC source code")
        osppath.list()


def setup(subparsers):
    subparser = subparsers.add_parser('osp', help=help)
    subparser.usage = usage
    mutualex_group = subparser.add_mutually_exclusive_group()
    mutualex_group.add_argument(
        "--add", help='fetch the remote source code and add it to osp.json')
    subparser.add_argument('-m', '--manifest-url',
                           help='''manifest repository URL to clone;
                           cannot be combined with -l''')
    subparser.add_argument('--mr', '--manifest-rev', dest='manifest_rev',
                           help='''manifest revision to check out and use;
                           cannot be combined with -l''')
    subparser.add_argument(
        'directory', nargs='?', default=None,
        help='''with -l, the path to the local osp repository;
        without it, the directory to create the workspace in (defaulting
        to the current working directory in this case)''')
    subparser.add_argument('-l', '--local', action='store_true',
                           help="""add local existing directory to osp.json """)
    mutualex_group.add_argument(
        "--rename", action='store_true', help="rename osp source code")
    mutualex_group.add_argument(
        '-rm', '--remove', help="remove the specified osp source code", metavar='')
    subparser.add_argument(
        '--list', action='store_true', help="show all recored embARC OSP source code")
    mutualex_group.add_argument(
        '-s', '--set', help="set a global EMBARC_OSP_ROOT, make sure you have added it to osp.json", metavar='')

    subparser.set_defaults(func=run)
