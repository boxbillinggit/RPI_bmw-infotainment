__author__ = 'lars'

import os, glob

ROOT = os.getcwd()

# sftp config
SFTP_ROOT="public-repository/debs"
SFTP_HOST="deploy"


def find_debian_package():

	return glob.glob('*/*.deb')


def deploy_debian_package(debpkg):

	sftp_cmd = list()
	sftp_cmd.append("'END'")

	for pkg in debpkg:
		sftp_cmd.append("put %s %s/%s" % (pkg, SFTP_ROOT, pkg))

	sftp_cmd.append("END")

	# deploy through sftp
	os.system("sftp %s << %s" % (SFTP_HOST, "\n".join(sftp_cmd) ))


if __name__ == "__main__":

	os.chdir(ROOT)
	deploy_debian_package(find_debian_package())

	print("Done!")
