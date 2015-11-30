__author__ = 'lars'

import os, subprocess

# Specify PATH if script is running from another location
ROOT = os.getcwd()

INCLUDES = ["html", "build-*/gateway"]

# path to deploy, trough sftp
SFTP_ROOT="public-repository/kodi/build/gateway"
SFTP_HOST="deploy"


def archive_name():

	try:
		stdout = subprocess.check_output("git show -s --format=%h", shell=True, stderr=subprocess.STDOUT)

	except:
		stdout = "unknown-version"

	return "gateway-%s.tar.gz" % stdout.replace("\n", "")


def create_archive(archive):

	bash_cmd = "tar -czf %s %s" % (archive, " ".join(INCLUDES))
	os.system(bash_cmd)


def deploy_archive(archive):

	# Create sftp batch-comand file for deploying files to repository. (directory must exist on remote)
	sftp_batch ="put %s %s/%s\n" % (archive, SFTP_ROOT, archive) + \
				"quit\n"

	open("sftp.batch", "w").write(sftp_batch)

	# deploy through SFTP
	os.system("sftp -b sftp.batch %s" % SFTP_HOST)


if __name__ == "__main__":

	os.chdir(ROOT)

	fname = archive_name()

	create_archive(fname)
	deploy_archive(fname)
