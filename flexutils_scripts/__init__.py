# **************************************************************************
# *
# * Authors:     David Herreros Calero (dherreros@cnb.csic.es)
# *
# * Unidad de  Bioinformatica of Centro Nacional de Biotecnologia , CSIC
# *
# * This program is free software; you can redistribute it and/or modify
# * it under the terms of the GNU General Public License as published by
# * the Free Software Foundation; either version 2 of the License, or
# * (at your option) any later version.
# *
# * This program is distributed in the hope that it will be useful,
# * but WITHOUT ANY WARRANTY; without even the implied warranty of
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# * GNU General Public License for more details.
# *
# * You should have received a copy of the GNU General Public License
# * along with this program; if not, write to the Free Software
# * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
# * 02111-1307  USA
# *
# *  All comments concerning this program package may be sent to the
# *  e-mail address 'scipion@cnb.csic.es'
# *
# **************************************************************************


import os
import sys
import subprocess
import pkg_resources
from importlib import import_module


__version__ = "1.0.0"


def getImagePath(image_name):
    """Returns the absolute path to an image within the package."""
    module_dir = os.path.dirname(__file__)  # Get the directory of this module
    image_path = os.path.join(module_dir, 'media', image_name)
    return image_path

def getCondaBase():
    try:
        conda_base = subprocess.check_output("conda info --base", shell=True, text=True).strip()
        return conda_base
    except subprocess.CalledProcessError as e:
        print(f"Error finding Conda base: {e}")
        return None

def getCondaActivationCommand():
    return f'eval "$({getCondaBase()}/bin/conda shell.bash hook)"'

def getCondaSourceFile():
    conda_source_file = f"{getCondaBase()}/etc/profile.d/conda.sh"
    return conda_source_file

def getProgram(program, env_name=None):
    env_name = env_name if env_name is not None else "flexutils"

    if env_name != "flexutils":
        # We need to call the script with python
        program_path = findEntryPointPath(program)
        program = "python " + program_path

    return f"{getCondaActivationCommand()} && conda activate {env_name} && {program}"

def findEntryPointPath(entry_point_name):
    entry_point = None

    # Attempt to find the entry point
    for ep in pkg_resources.iter_entry_points(group='console_scripts'):
        if ep.name == entry_point_name:
            entry_point = ep
            break

    if entry_point is not None:
        # Extract module (and function, if any)
        module_name = entry_point.module_name
        attrs = entry_point.attrs

        # Import the module/package
        module = import_module(module_name)

        # Resolve the module/package to its file path
        file_path = os.path.abspath(module.__file__)

        return file_path
    else:
        raise FileNotFoundError(f"Script {entry_point_name} not found")

def runProgram(program, args, env=None, cwd=None):
    command = program + " " + args
    subprocess.check_call(command, shell=True, stdout=sys.stdout, stderr=sys.stderr,
                          env=env, cwd=cwd)
