import os
import shutil

from exall import exall, ignore, print_warning, print_traceback, print_error
from .filesystem import *

@exall(os.unlink, FileNotFoundError, ignore)
def clean(config):
    """ Clean the filesystem.
    """
    os.unlink(config.KERNEL)
    os.unlink(config.DTB)
    os.unlink(config.ROOTFS)
    shutil.rmtree(config.DIR, ignore_errors=True)

def autostart(rootfs, script):
    fs = Filesystem(rootfs)
    if script:
        fs.put(script, "/etc/init.d/S90_user_autostart", right=555)
    else:
        fs.rm("/etc/init.d/S90_user_autostart")

def sync(rootfs, src, dest):
    fs = Filesystem(rootfs)
    if not fs.implemented():
        return
    print("Adding current directory to the filesystem..")
    with tempfile.TemporaryDirectory() as tmpdirname:
        files = [ i for i in os.listdir(".") if i != "arm_now" and not i.startswith("-") ]
        if files:
            tar = tmpdirname + "/current_directory.tar"
            subprocess.check_call(["tar", "cf", tar] + files)
            subprocess.check_call("e2cp -G 0 -O 0".split(' ') + [tar, rootfs + ":/"])
            fs.create("/etc/init.d/S95_sync_current_diretory","""
                        cd {dest}
                        tar xf /current_directory.tar
                        rm /current_directory.tar
                        rm /etc/init.d/S95_sync_current_diretory
                        """.format(dest=dest), right=555)

    # TODO: check rootfs fs against parameter injection
    fs.create("/sbin/save", """
                cd {dest}
                tar cf /root.tar *
                sync
                """.format(dest=dest), right=555)