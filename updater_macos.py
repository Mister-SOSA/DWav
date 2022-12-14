from urllib.request import urlopen
from requests import get
from io import BytesIO
from zipfile import ZipFile
import os
import shutil
import subprocess
import urllib.request as urllib
import tkinter as tk
from tkinter import messagebox
from tkinter import *
from tkinter import filedialog as fd
import configparser
import sys
from supabase import create_client, Client
from subprocess import Popen, PIPE

url = 'supabase_url'
key = 'supabase_key'
Client = create_client(url, key)

root = tk.Tk()
root.overrideredirect(1)
root.withdraw()

def log_auth(hwid, attempted_key, working_directory, key_found, version_found, auth_response, ip_address, notes):
    """ Send authentication results to SQL table """
    Client.table('auth_mac').insert({"hwid": hwid,
                                 "attempted_key": attempted_key,
                                 "working_directory": working_directory,
                                 "key_found": key_found,
                                 "version_found": version_found,
                                 "auth_response": auth_response,
                                 "ip_address": ip_address,
                                 "notes": notes}).execute()

def log_updates(hwid, installed_version, available_version, accepted_update, working_directory, outcome, ip_address, notes):
    """ Send update results to SQL table """
    Client.table('updates_mac').insert({"hwid": hwid,
                                 "installed_version": installed_version,
                                 "available_version": available_version,
                                 "accepted_update": accepted_update,
                                 "working_directory": working_directory,
                                 "ip_address": ip_address,
                                 "outcome": outcome,
                                 "notes": notes}).execute()

def get_hwid():
    """ Fetch this machine's HWID for authentication """
    stdout = Popen('system_profiler SPHardwareDataType | grep Serial', shell=True, stdout=PIPE).stdout
    output = (stdout.read()).decode('ascii')
    uuid = (output[output.index(':') + 2: len(output)]).strip()
    return uuid



def download_and_unzip(url, install_directory):
    """ Function to download and unzip from url """
    print('\n\nDownloading Detroit Wave Soundkit. Please Wait...')
    http_response = urlopen(url)
    zipfile = ZipFile(BytesIO(http_response.read()))
    zipfile.extractall(path=install_directory)

def get_ip():
    ip = get('https://api.ipify.org').content.decode('utf8')
    return ip

def newest_version():
    """ Fetch newest available version number from Github text file """
    fetch_config = urllib.urlopen(
        'https://raw.githubusercontent.com/Mister-SOSA/dwum/main/newest_version.txt')
    return ((fetch_config.read()).decode())


def current_version():
    """ Fetch currently installed version number from local config file """
    with open(os.path.join(sys.executable.split('MacOS')[0], 'Resources/version.ini')) as f:
        return f.readlines()[0]


def update():
    """ Fetch newest version of kit and unzip it in the current directory """
    f = open(os.path.join(sys.executable.split('MacOS')[0], 'Resources/dir.ini'), 'r+')
    current_dir = f.read().strip().replace("\x00", '')
    if (current_dir == 'undefined' or current_dir == ''):
        messagebox.showinfo('Detroit Wave Updater', 'Please select the folder where you\'d like the kit to be installed. Usually this is your FL Studio Packs directory.')
        install_dir = fd.askdirectory()
        if install_dir == '':
            messagebox.showinfo('Detroit Wave Updater', 'You did not select a folder. Start the updater again to try again.')
            sys.exit()
        else:
            try:
                f = open(os.path.join(sys.executable.split('MacOS')[0], 'Resources/dir.ini'), 'r+')
                f.truncate(0)
                f.write(install_dir)
                f.close()
            except Exception as e:
                messagebox.showinfo('Detroit Wave Updater', e)
    else:
        res = messagebox.askyesno('Detroit Wave Updater', 'Would you like to update to the same directory?\n' + current_dir)
        if res == True:
            install_dir = current_dir
        else:
            messagebox.showinfo('Detroit Wave Updater', 'Please select the folder where you\'d like the kit to be installed. Usually this is your FL Studio Packs directory.')
            install_dir = fd.askdirectory()
            if install_dir == '':
                messagebox.showinfo('Detroit Wave Updater', 'You did not select a folder. Start the updater again to try again.')
                sys.exit()
            else:
                try:
                    f = open(os.path.join(sys.executable.split('MacOS')[0], 'Resources/dir.ini'), 'r+')
                    f.truncate(0)
                    f.write(install_dir)
                    f.close()
                except Exception as e:
                    messagebox.showinfo('Detroit Wave Updater', e)

    if (os.path.isdir(install_dir + 'Alex Kure - Detroit Wave')):
        try:
            shutil.rmtree(install_dir + 'Alex Kure - Detroit Wave/')
        except:
            log_updates(get_hwid(), current_version(), newest_version(), 'TRUE', os.getcwd(), get_ip(),'FAILED', 'Update failed due to a permissions issue.')
            messagebox.showerror(
                'Permissions Issue', 'Update failed due to a permissions issue. Usually this means the folder you picked is protected by your computer.')
            sys.exit()
    try:
        messagebox.showinfo('Detroit Wave Updater', 'The download will begin once you click OK. Please be patient, as the file is quite large. The program may appear unresponsive while the kit downloads.')
        download_and_unzip(
            'https://www.dropbox.com/s/zazlpjlshbm1r0r/Alex%20Kure%20-%20Detroit%20Wave.zip?dl=1', install_dir)
        log_updates(get_hwid(), current_version(), newest_version(), 'TRUE', os.getcwd(), 'SUCCESS', get_ip(), 'Successfully updated.')
        messagebox.showinfo('Detroit Wave Updater', 'Update completed! Feel free to give me feedback on Instagram: @AlexKure')

    except:
        log_updates(get_hwid(), current_version(), newest_version(), 'TRUE', os.getcwd(), 'FAILED',  get_ip(), 'Update failed due to file availability or network connection.')
        messagebox.showerror(
            'Update Failed!', 'Make sure you are connected to the internet and try again.\nIf this error persists, contact me on Instagram: @AlexKure')
        sys.exit();
    try:
        f = open(os.path.join(sys.executable.split('MacOS')[0], 'Resources/version.ini'), "r+")
        f.truncate(0)
        f.write(newest_version())
        f.close()
    except Exception as e:
        messagebox.showinfo('Detroit Wave Updater', e)


def main():
    """ Initiate config parser and read key file """
    config = configparser.ConfigParser()
    config.read(os.path.join(sys.executable.split('MacOS')[0], 'Resources/key.dll'))

    """ Check HWID with internal key file. If matched, proceed. If not, quit with error """
    if (config['REGISTRATION']['hwid'] == 'unregistered'):
        log_auth(get_hwid(), config['REGISTRATION']['hwid'], os.getcwd(), 'TRUE', 'TRUE', 'SUCCESS', get_ip(), 'First time registration.')
        config['REGISTRATION']['hwid'] = get_hwid()
        try:
            with open(os.path.join(sys.executable.split('MacOS')[0], 'Resources/key.dll'), 'w') as configfile:
                config.write(configfile)
        except Exception as e:
            log_auth(get_hwid(), config['REGISTRATION']['hwid'], os.getcwd(), 'TRUE', 'TRUE', 'FAILED', get_ip(), 'First time registration failed!')
            messagebox.showinfo(
                'Registration Failed!', 'First time setup failed.\n' + str(e))

    if (config['REGISTRATION']['HWID'] != get_hwid()):
        log_auth(get_hwid(), config['REGISTRATION']['hwid'], os.getcwd(), 'TRUE', 'TRUE', 'FAILED', get_ip(), 'Piracy Protection Triggered.')
        messagebox.showerror('Validation Failed!', 'Your device is not registered with this soundkit. Make sure you have purchased the soundkit and are using your own copy of the updater.\n\nFor assistance, DM me on Instagram: @AlexKure')
        sys.exit()
    else:
        log_auth(get_hwid(), config['REGISTRATION']['hwid'], os.getcwd(), 'TRUE', 'TRUE', 'SUCCESS', get_ip(), 'Successful Login.')

    """ Check if a new version of the kit is available. If so, download it and unzip it to the current dir """
    if (current_version() != newest_version()):
        res = messagebox.askyesno('Detroit Wave Updater', 'An update is available! Would you like to download it?')
        if res == True:
            update()
        else:
            log_updates(get_hwid(), current_version(), newest_version(), 'FALSE', os.getcwd(), 'REJECTED', get_ip(), 'User rejected update')
            messagebox.showinfo('Update Cancelled', 'If you change your mind, run this updater again to download the latest version of Detroit Wave.')
            sys.exit()
    else:
        res = messagebox.askyesno('Detroit Wave Updater', 'You already have the newest version of the soundkit. Would you like to reinstall it anyway?')
        if res == True:
            log_updates(get_hwid(), current_version(), newest_version(), 'TRUE', os.getcwd(), 'N/A', get_ip(), 'User reinstalled.')
            update()
        else:
            sys.exit()
