from __future__ import print_function, division, unicode_literals
import os
import sys
import logging
from ...osp import osp


help = "get, set or unset osp configuration."

usage = ("\n    embarc config osp --add <name> -m <url> --mr <rev> [<dest>]\n"
         "    embarc config osp --add <name> --local [<dest>]\n"
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
            osppath.local(args.add, args.local)
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
            logging.info(f"rename {old} to {new}")
            osppath.rename(old, new)
            args.list = True
    elif args.remove:
        name = args.remove
        logging.info(f"remove {name} ")
        osppath.remove(name)
        args.list = True
    elif args.set:
        logging.info(f"set {args.set} as global EMBARC_ROOT")
        osppath.set_global(args.set)
    else:
        if remainder:
            logging.error(f"usage: {usage}")
            sys.exit(1)

    if args.list:
        logging.info("current recored embARC source code")
        osppath.list()


def setup(subparsers):
    subparser = subparsers.add_parser('osp', help=help)
    subparser.usage = usage
    mutualex_group = subparser.add_mutually_exclusive_group()
    mutualex_group.add_argument(
        "--add", metavar='', help='add a local or remote osp source code named <name>')
    subparser.add_argument('-m', '--manifest-url', metavar='',
                           help='''osp repository url to clone;
                           cannot be combined with -l''')
    subparser.add_argument('--mr', '--manifest-rev', dest='manifest_rev', metavar='',
                           help='''osp revision to check out and use;
                           cannot be combined with -l''')
    subparser.add_argument(
        'directory', nargs='?', default=None, metavar='',
        help='''with -l, the path to the local osp repository;
        without it, the directory to create the osp in (defaulting
        to the current working directory)''')
    subparser.add_argument('-l', '--local', metavar='',
                           help="""local existing osp directory""")
    mutualex_group.add_argument(
        "--rename", action='store_true', help="rename existing osp source code")
    mutualex_group.add_argument(
        '-rm', '--remove', help="remove the specified osp source code", metavar='')
    subparser.add_argument(
        '--list', action='store_true', help="show all recored osp source code")
    mutualex_group.add_argument(
        '-s', '--set', help="set a global EMBARC_ROOT, make sure you have added it to osp.json", metavar='')

    subparser.set_defaults(func=run)
