#!/usr/bin/env python

import argparse
import json
import sys
import os
import shutil
import errno
import subprocess
from lxml import etree


# FIXME: Clean the __main__ part up
# FIXME: Warn about adding application to project.xml and run xadd
# FIXME: Run update_versions


def sign_binary(boinc_project_dir, app_directory, target_file):
    """Signs binary using the sign_executable binary of BOINC

    Args:
        boinc_project_dir (string): BOINC project root directory
        app_directory (string): Directory containing deployed
            application files (apps/../..)
        target_file (string): File to sign within the app_directory
    """
    # FIXME: parameters are `a bit` redundant
    try:
        cmd = "{} {} {} > {}".format(
            os.path.join(boinc_project_dir, "bin/sign_executable"),
            os.path.join(app_directory, target_file),
            os.path.join(boinc_project_dir, "keys/code_sign_private"),
            os.path.join(app_directory, target_file + ".sig"))
        p = subprocess.Popen(cmd, shell=True)
        os.waitpid(p.pid, 0)
    except OSError:
        print(
            "WARNING: cannot sign `{}`, do it manually!".
            format(target_file))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Deploy BOINC application to `apps` folder.')
    parser.add_argument(
        '--config',
        type=str,
        dest='config',
        help='Config JSON to use',
        required=True)
    parser.add_argument(
        '--source-dir',
        type=str,
        dest='directory',
        help='Directory containing application files',
        required=True)
    args = parser.parse_args()

    # Check environment for BOINC_PROJECT_DIR
    if 'BOINC_PROJECT_DIR' not in os.environ:
        print(
            "ERROR: BOINC_PROJECT_DIR environment variable " /
            "is not set\n")
        sys.exit(254)
    boinc_project_dir = os.environ["BOINC_PROJECT_DIR"]
    if not os.path.isdir(boinc_project_dir):
        print(
            "ERROR: BOINC_PROJECT_DIR directory (`{}`) does not exist".
            format(boinc_project_dir))
        sys.exit(253)

    # Load config
    try:
        config_data = json.load(open(args.config))
    except IOError:
        print("ERROR: no such config file `{}`\n".format(args.config))
        sys.exit(255)

    # Copy application files with proper name
    main_executable_found = False
    search_dir = args.directory
    for root, dirs, files in os.walk(search_dir):
        for file in files:
            if file == config_data["main_executable"]:
                main_executable_found = True
    if not main_executable_found:
        print("ERROR: Main executable file not found!")
        sys.exit(252)

    app_directory = os.path.join(
        boinc_project_dir,
        "apps",
        config_data["name"], config_data["version"],
        config_data["platform"])
    print("#" * 48)
    print("INFO: Source dir is: {}".format(search_dir))
    print("INFO: Target dir is: {}".format(app_directory))
    print("INFO: Application name is: {}".format(config_data["name"]))
    print("INFO: Version is: {}".format(config_data["version"]))
    print("INFO: Platform is: {}".format(config_data["platform"]))
    print("#" * 48)
    if os.path.isdir(app_directory):
        print(
            "ERROR: target directory `{}` already exists, " /
            "remove it first.".
            format(app_directory))
        sys.exit(251)
    try:
        os.makedirs(app_directory)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

    version_xml = etree.Element("version")
    for root, dirs, files in os.walk(search_dir):
        print("INFO: Copying files...")
        for file in files:
            file_data = file.split('.')
            target_file = "{}_{}_{}_{}".format(
                file_data[0],
                config_data["name"],
                config_data["version"],
                config_data["platform"])
            # Append file extension at the end (if there is any)
            try:
                target_file = "{}.{}".format(target_file, file_data[1])
            except IndexError:
                pass
            shutil.copy(os.path.join(search_dir, file),
                        os.path.join(app_directory, target_file))
            # Sign binary
            sign_binary(boinc_project_dir, app_directory, target_file)
            # Add data to version.xml
            file_xml = etree.Element("file")
            phy_name_xml = etree.Element("physical_name")
            phy_name_xml.text = target_file
            file_xml.append(phy_name_xml)
            if file == config_data["main_executable"]:
                main_exe_xml = etree.Element("main_program")
                file_xml.append(main_exe_xml)
            else:
                logical_name_xml = etree.Element("logical_name")
                logical_name_xml.text = file
                file_xml.append(logical_name_xml)
            version_xml.append(file_xml)
    # Write version.xml and sign it
    print("INFO: Generating version.xml.")
    with open(os.path.join(app_directory, "version.xml"), "w") as text_file:
            text_file.write(etree.tostring(version_xml, pretty_print=True))

    sign_binary(boinc_project_dir, app_directory, "version.xml")
    print("INFO: Done.")
