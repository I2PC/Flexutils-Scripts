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

def getCondaSourceFile():
    conda_source_file = f"{getCondaBase()}/etc/profile.d/conda.sh"
    return conda_source_file

def getProgram(program, env_name=None):
    env_name = env_name if env_name is not None else "flexutils"
    return f"source {getCondaSourceFile()} && conda activate {env_name} && {program}"

def runProgram(program, args, env=None, cwd=None):
    command = program + " " + args
    subprocess.check_call(command, shell=True, stdout=sys.stdout, stderr=sys.stderr,
                          env=env, cwd=cwd)
