__author__ = 'lars'

import os, subprocess, fnmatch, time

# specify includes to pack in the archive
PREFIX_BUILD_PATH = "build-*"
INCLUDES = ["html", PREFIX_BUILD_PATH+"/gateway"]

# path on server to put files on
SFTP_ROOT="public-repository/kodi/build/gateway"
SFTP_HOST="deploy"


# TODO: will only fetching first target (multiple builds are possible within one deploy)
def _get_build_target():

	for dirname in os.listdir('.'):
		if fnmatch.fnmatch(dirname, PREFIX_BUILD_PATH) and os.path.isdir(dirname):
			return dirname

	raise Exception('No build target found')


def archive_name():

	try:
		stdout = subprocess.check_output("git show -s --format=%h", shell=True, stderr=subprocess.STDOUT)
	except:
		stdout = "unknown"

	try:
		target = _get_build_target()
	except:
		target = "unknown-target"

	return "%s@%s.tar.gz" % (target, stdout.replace("\n", ""))


def create_archive(archive):

	bash_cmd = "tar -czf %s %s" % (archive, " ".join(INCLUDES))
	subprocess.call(bash_cmd, shell=True)
	time.sleep(1)



def deploy_archive(archive):

	# Create sftp batch-comand file for deploying files to repository. (directory must exist on remote)
	sftp_batch ="put %s %s/%s\n" % (archive, SFTP_ROOT, archive) + \
				"quit\n"

	open("sftp.batch", "w").write(sftp_batch)

	# deploy through SFTP
	subprocess.call("sftp -b sftp.batch %s" % SFTP_HOST, shell=True)


if __name__ == "__main__":

	fname = archive_name()

	create_archive(fname)
	deploy_archive(fname)
