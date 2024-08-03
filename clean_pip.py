import os

commands = [
    "pip freeze > requirements.txt",
    "pip uninstall -r requirements.txt -y",
]


def run_command(command):
    print("Running command: {}".format(command))
    os.system(command)


for command in commands:
    run_command(command)
# import pip
from subprocess import call

# for dist in pip.get_installed_distributions():
#     call("pip uninstall -y " + dist.project_name, shell=True)



# import pkg_resources
# from subprocess import call

# installed_packages = pkg_resources.working_set
# installed_packages_list = sorted(
#     ["%s==%s" % (i.key, i.version) for i in installed_packages]
# )

# for package in installed_packages_list:
#     call("pip uninstall -y " + package.split("==")[0], shell=True)



# import setuptools
# from subprocess import call

# installed_packages = setuptools.PackageFinder.find()
# installed_packages_list = sorted(
#     ["%s==%s" % (i.key, i.version) for i in installed_packages]
# )

# for package in installed_packages_list:
#     call("pip uninstall -y " + package.split("==")[0], shell=True)

