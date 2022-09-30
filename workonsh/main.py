import click
import os
import subprocess
import time

from subprocess import Popen, PIPE

from workonsh.utils import rule_from_pattern, make_logger

def run_process(command):
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return iter(p.stdout.readline, b'')


def build_rsync_command(src, dest, exclude, filter, dry_run):
    if dry_run:
        command = ["rsync", "-aic", "--delete"]
    else:
        command = ["rsync", "-avzic", "--progress", "--delete"]
    for exc in exclude:
        command.extend(["--exclude", exc])
    if filter is not None:
        command.extend(["--filter", f":- {filter}"])
    if dry_run:
        command.append("--dry-run")
    command.extend([src, dest])
    return command

def build_fswatch_command(src, exclude):
    command = ["fswatch", '--recursive']
    for exc in exclude:
        command.extend(["--exclude", exc])
    command.append(src)
    return command


def run_fswatch(src, dest, exclude, filter, exclude_with_filter, logger, rsync_interval=3):
    last_rsynced = time.time()
    fswatch_command = build_fswatch_command(src, exclude_with_filter)
    for line in run_process(fswatch_command):
        str_line = line.decode('utf-8').rstrip('\n')
        logger.info(f"Detected a changese in file: {str_line}", )
        if time.time() - last_rsynced >= rsync_interval:
            logger.info(f"Running Rsync from {src} to {dest}")
            run_rsync(src, dest, exclude, filter, dry_run=False)
            last_rsynced = time.time()


def run_rsync(src, dest, exclude, filter, dry_run=False):
    print("="*10, "Running Rsync", "Dry" if dry_run else "", "="*10)
    command = build_rsync_command(src, dest, exclude, filter, dry_run) 
    num_synced_files = 0
    for line in run_process(command):
        print(line.decode('utf-8').rstrip('\n'))
        num_synced_files += 1
    print("="*10, "Done", "="*10)
    return num_synced_files 

@click.command()
@click.option(
    '--project-name', '-n', required=True,
    help='Name of the project that is used to sync: this is also the folder name of the project and used in both src and dest.'
)
@click.option(
    '--src', '-s', required=True,
    help='Source folder to sync'
)
@click.option(
    '--dest', '-d', required=True,
    help='Destination folder to sync'
)
@click.option(
    '--exclude', '-e', type=str, multiple=True,
    default=['__pycache__', '.git/', '.git/*'],
    help='Exclude files by RegEx'
)
@click.option(
    '--filter', '-f', type=str,
    help="""Ignore all files matched with, similar to filter of rsync,
            could be .gitignore
    """
)
@click.option(
    '--log-file', '-l', type=str,
    help="Log file"
)
@click.option(
    '--rsync-interval', '-i', type=int, default=5,
    help="Time interval to run rsync."
)
@click.option(
    '--yes', '-y', is_flag=True,
    help="Don't ask any interactive questions; pretend 'source-to-dest' for initial sync"
)
def main(project_name, src, dest, exclude, filter, log_file, rsync_interval, yes):
    logger = make_logger(log_file)
    exclude_with_filter = list(exclude)
    srcn = os.path.join(src, f"{project_name}")
    destn = os.path.join(dest, f"{project_name}")

    if filter is not None:
        with open(filter) as f:
            for line in f.readlines():
                line = line.rstrip('\n')
                regex = rule_from_pattern(line)
                if regex is not None:
                    exclude_with_filter.append(regex)

    logger.info("Establishing the connection...")
    logger.info("Compare source folder and destination folder")
    num_sync_files = run_rsync(srcn, dest, exclude, filter, dry_run=True)

    if num_sync_files > 0:
        logger.info(f"Source folder {srcn} is currently not synced with the destination folder {destn}...")
        print("="*10, "Sync source vs destination...", "="*10)
        print(f"You could sync the newer version of src ({srcn}) to dest ({destn}) [s] \n \
Or you could sync the newer version of dest ({destn}) to src ({srcn}) [d] \n \
Or terminate the process [t]!!!\n \
!!!! BECAREFUL -- THIS IS IRREVERSIBLE!!!!\n \
Choose [s/d/T]:...", end='')
        if yes:
            choice = 's'
            print(choice)
        else:
            choice = input().lower()
        terminate = False
        frm, to = None, None
        if choice == 's':
            frm, to = srcn, dest
        elif choice == 'd':
            frm, to = destn, src
        else:
            terminate = True

        if not terminate:
            print(f"Syncing from ({frm}) to ({to})...")
            print(f"Check dry run first...")
            run_rsync(frm, to, exclude, filter, dry_run=True)
            print(f"Do you want to proceed [y, N]...", end='')
            if yes:
                proceed = 'y'
                print(proceed)
            else:
                proceed = input().lower()
            if proceed == 'y':
                run_rsync(frm, to, exclude, filter, dry_run=False)
            else:
                terminate = True

        if terminate:
            logger.info("Terminate the session.")
            exit(0)

    logger.info(f"Synced source ({srcn}) and destination ({destn}) directories. Starting the session...HIHI")

    if '.project' in exclude_with_filter:
        exclude_with_filter.remove('.project')
    run_fswatch(srcn, dest, exclude, filter, exclude_with_filter, logger, rsync_interval)
