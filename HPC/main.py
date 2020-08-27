"""Script entry point."""

# from paramiko_tutorial import main
#
# if __name__ == '__main__':
#     main()

from ParamikoTools import client  #RemoteClient
from ParamikoTools import files # fetch_local_files

from HPC.config import (
    host,
    user,
    ssh_key_filepath,
    local_file_directory,
    remote_path,
    passphrase
)


def main():
    """Initialize remote host client and execute actions."""
    remote = client.RemoteClient(host, user, ssh_key_filepath, remote_path, passphrase)
    upload_files_to_remote(remote)
    execute_command_on_remote(remote)
    remote.disconnect()


def upload_files_to_remote(remote):
    """Upload files to remote via SCP."""
    local_files = files.fetch_local_files(local_file_directory)
    remote.bulk_upload(local_files)


def execute_command_on_remote(remote):
    """Execute UNIX command on the remote host."""
    remote.execute_cmd('cd /var/www/ghost ls')

main()