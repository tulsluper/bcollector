#!/usr/bin/env python

import os
import importlib
import argparse
import logging
import tempfile
import tarfile
from datetime import datetime
from multiprocessing import Pool
from contextlib import closing
from paramiko import SSHClient, AutoAddPolicy


def ssh_run(args):
    system, address, username, password, commands = args
    address, port = address.split(':') if ':' in address else address, 22
    outs, errs, exception = {}, {}, None
    try:
        client = SSHClient()
        client.set_missing_host_key_policy(AutoAddPolicy())
        client.load_system_host_keys()
        client.connect(address, port=port, username=username, password=password)
        for name, command in commands:
            stdin, stdout, stderr = client.exec_command(command)
            outs[name] = stdout.read()
            errs[name] = stderr.read()
    except Exception as e:
        exception = e
    finally:
        client.close()
    return system, outs, errs, exception


def main():


    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-c', '--configfile', metavar='FILE', default='conf.py',
        help='use this configuration file')
    args = parser.parse_args()

    configfile = args.configfile
    if configfile[-3:] == '.py':
        configfile = configfile[:-3]
    conf = importlib.import_module(configfile)
    from conf import CONNECTIONS, COMMANDS, PROCESSES
    from conf import DATADIR, LOGFILE

    logging.basicConfig(
        filename=LOGFILE,
        level=logging.INFO,
        format='%(asctime)s %(name)s %(levelname)s %(message)s')
    logging.getLogger("paramiko").setLevel(logging.WARNING)
    logger = logging.getLogger('bcollector')
    logger.info('start')

    dtstr = datetime.now().strftime("%Y-%m-%d.%H-%M-%S")
    if not os.path.exists(DATADIR):
        os.makedirs(DATADIR)
    archive = os.path.join(DATADIR, '%s.tar.gz' %dtstr)

    with closing(Pool(PROCESSES)) as pool, tarfile.open(archive, "w:gz") as tar:
        for result in pool.imap_unordered(ssh_run, CONNECTIONS):
            system, outs, errs, exception = result
            if not exception:
                for command, out in outs.items():
                    with tempfile.NamedTemporaryFile() as temp:
                        temp.write(out)
                        temp.flush()
                        tar.add(temp.name, arcname='%s.%s' %(system, command))
                        logger.info('%s %s' %(system, command))
            else:
                logger.warning('%s %s' %(system, exception))
    logger.info('finish')
    return


if __name__ == '__main__':
    main()


