#!/usr/bin/env python

# Python swap manager
# Copyright (c) 2018-2018, Mickael Badet
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#     * Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice,this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the copyright holder nor the names of its
#       contributors may be used to endorse or promote products derived from
#       this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

__all__ = [
    # Main swap management.
    'swapcheck_main',
    "SwapInfo"
]

# libs
import os
import re
import subprocess
import psutil
import psutil._common
from mblibs import is_windows
from mblibs.fast import FastSettings
from mblibs.fast import FastEmail


# ----------------------------------------------------------------------------------------------------------------------
# - Process swap info object
# ----------------------------------------------------------------------------------------------------------------------
class SwapInfo:
    # ------------------------------------------------------------------------------------------------------------------
    def __init__(self):
        self._data = []
        self.swap_total = 0
        self.check()
        self.check.cache_clear()

    # ------------------------------------------------------------------------------------------------------------------
    @psutil._common.memoize
    def check(self):
        """
        Function to get all swap informations

        bash:
        for file in /proc/*/status ; do awk '/Tgid|VmSwap|Name/{printf $2 " " $3}END{ print ""}' $file; done | grep kB | sort -k 3 -n

        :return: bool
        """
        # check system
        if is_windows():
            raise Exception("Windows not implemented, sorry")

        # init
        self._data = []
        self.swap_total = 0

        # get all PIDs
        pids = [pid for pid in os.listdir('/proc') if pid.isdigit()]
        for pid in pids:
            # get content informations
            try:
                content = open(os.path.join('/proc', pid, 'status'), 'rb').read()

            except IOError:
                # proc has already terminated
                continue

            # extract informations
            name = ""
            process_id = 0
            swap = 0.0
            content_array = content.split(b"\n")
            for row in content_array:
                row_array = row.split(b'\t')
                try:
                    # process name
                    if row_array[0] == b'Name:':
                        name = row_array[1].decode()

                    # swap information
                    elif row_array[0] == b'VmSwap:':
                        swap = float(row_array[1].split(b" kB")[0].strip())
                        self.swap_total += swap

                    # process ID
                    elif row_array[0] == b'Tgid:':
                        process_id = int(row_array[1])

                except:
                    continue

            # organisation
            if name != "":
                self._data.append({"name": name,
                                   "pid": process_id,
                                   "swap": swap,
                                   })

    # ------------------------------------------------------------------------------------------------------------------
    def swap_info(self, order_by="swap"):
        """
        Get list of data ordering by arguments (name, pid or swap)

        :param order_by: name, pid or swap ordering
        :return: list
        """
        # check
        if not order_by in ["name", "pid", "swap"]:
            raise Exception("Ordering '{}' not implemented!".format(order_by))

        try:
            # sorting
            list_sorted = sorted(self._data, key=lambda k: k[order_by])

            # Add total information
            list_sorted.append({"name": "Total Process",
                                "pid": -1,
                                "swap": self.swap_total})
            return list_sorted

        except:
            return None

    # ------------------------------------------------------------------------------------------------------------------
    def swap_info_text(self, order_by="swap"):
        """
        Get list of data ordering by arguments (name, pid or swap) and display in text

        :param order_by: name, pid or swap ordering
        :return: string
        """
        # get informations
        listing = self.swap_info(order_by)

        # text construction
        body = ""
        for row in listing:
            body += "- {name} (#{pid}): swap={swap}ko\n".format(**row)
        return body

    # ------------------------------------------------------------------------------------------------------------------
    def swap_info_html(self, order_by="swap"):
        """
        Get list of data ordering by arguments (name, pid or swap) and display in html

        :param order_by: name, pid or swap ordering
        :return: string
        """
        # get informations
        listing = self.swap_info(order_by)

        # text construction
        body = "<table width=90% border=1 cellspacing=0 cellpadding=0>\n"
        body += "<tr><td>Name</td><td>Process ID</td><td>Swap</td></tr>\n"
        for row in listing:
            body += "<tr><td>{name}</td><td>{pid}</td><td>{swap}ko</td></tr>\n".format(**row)
        body += "</table>\n"
        return body

    # ------------------------------------------------------------------------------------------------------------------
    def count(self):
        """
        Count all process found!
        :return: int
        """
        return len(self._data)

    # ------------------------------------------------------------------------------------------------------------------
    def swap_memory(self):
        """
        get current system swap
        :return: tuple
        """
        return psutil.swap_memory()

    # ------------------------------------------------------------------------------------------------------------------
    def is_swap_alert(self, alert_limit=50.0):
        """
        Check if system swap is in alert (percent pressure)

        :param alert_limit: percent limit to alerting
        :return:
        """
        info = self.swap_memory()
        return info.percent >= alert_limit

    # ------------------------------------------------------------------------------------------------------------------
    def can_reset(self):
        """
        Check if swap can be resetting with current memories.
        If no more left RAM, function returns False

        :return: boolean
        """
        swapobject = psutil.swap_memory()
        memobject = psutil.virtual_memory()
        try:
            if memobject.available > swapobject.used:
                return True
            return False

        except:
            return False


# ----------------------------------------------------------------------------------------------------------------------
def bash(commandline, root=False):
    """
    Execute a bash command

    :param commandline: command line
    :param is_root: command must be root command
    :return: return command
    """
    commandline = commandline.strip()
    if commandline == "":
        raise Exception("No command!".format(commandline))

    # check if root command
    if root and not os.geteuid() == 0:
        # must be root
        raise Exception("This command must be run as root: {}".format(commandline))

    # execute command
    try:
        return subprocess.check_call(commandline, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except:
        return -1


# ----------------------------------------------------------------------------------------------------------------------
def swapcheck_main(settings_pathname, simulation=False, display_stdout=False):
    """
    Function to testing current swap and alert if detects a warning/alert

    :param settings_pathname: path filename to settings
    :param simulation: simulate resetting swap
    :param display_stdout: display result to stdout
    :return: current_percent
    """
    # get settings
    settings = FastSettings(settings_pathname)

    # get information
    alert_limit = settings.getFloat("/swap/alert-limit", default=50.0)

    # object information
    swap = SwapInfo()
    percent = swap.swap_memory().percent

    # swap is in alert
    if swap.is_swap_alert(alert_limit=alert_limit):
        # snapshot before resetting
        info_before = swap.swap_memory()

        # log
        print("- Swap alert: {:.2f}%".format(info_before.percent))

        # reset swap
        reset_swap = False
        if settings.getEnable("/swap/reset-swap"):
            # execute commands for resetting swap
            if not simulation and swap.can_reset():
                print("- Reset swap")
                bash("swapoff -a", root=True)
                bash("swapon -a", root=True)
                reset_swap = True

            else:
                print("- Cannot reset swap: simulation or no more left memories")

            # post treatments
            if settings.getEnable("/swap/post-process-alert/enable"):
                # execute post command
                for command in settings.get("/swap/post-process-alert/commands"):
                    print("- Execute post command: {} => ".format(command), end="", flush=True)
                    ret = bash(command)
                    print("ret: {}".format(ret))

        # send email
        if settings.getEnable("/swap/email/enable"):
            # template construction
            body_text = settings.get("/swap/email/template", default="{swap_percent}\n{swap_list}").format(
                swap_percent=info_before.percent,
                swap_list=swap.swap_info_text(order_by=settings.get("/swap/order-by", "swap"))
            )
            body_text = re.sub('<[^<]+?>', '', body_text)

            body = settings.get("/swap/email/template", default="{swap_percent}<br />{swap_list}").format(
                swap_percent=info_before.percent,
                swap_list=swap.swap_info_html(order_by=settings.get("/swap/order-by", "swap"))
            )

            # adding "addons" :) if cannot reset swap
            if not reset_swap:
                body_text = "**Cannot reset swap: simulation or no more left memories**\n\n" + body_text
                body = "<b>Cannot reset swap: simulation or no more left memories</b><br /><br />" + body

            # Email object
            email = FastEmail()

            # SMTP configuration
            email.smtp_host = settings.get("/smtp/host", "localhost")
            email.smtp_port = settings.getInt("/smtp/port", 25)
            email.smtp_login = settings.get("/smtp/login")
            email.smtp_password = settings.get("/smtp/password")

            # mail configuration
            email.mail_from = settings.get("/swap/email/from")
            email.mail_subject = settings.getWithDateFormat("/swap/email/subject")
            email.mail_html = body
            email.mail_text = body_text

            # send mail
            to = settings.get("/swap/email/to", [])
            if type(to) != list:
                try:
                    to = to.split(",")
                except:
                    to = [to]
            email.send_mail(to=to)

    # display to stdout
    if display_stdout:
        print(swap.swap_info_text(order_by=settings.get("/swap/order-by", "swap")))

    # return percent
    return percent
