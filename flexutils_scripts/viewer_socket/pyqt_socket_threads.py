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
import shutil
import signal
import time

import numpy as np
from xmipp_metadata.image_handler import ImageHandler

from PyQt5.QtCore import QThread, pyqtSignal

from flexutils_scripts.viewer_socket.client import Client

from flexutils_scripts import getProgram, runProgram


class ServerQThread(QThread):
    def __init__(self, program, metadata_file, mode, port, env):
        super().__init__()
        self.program = getProgram(program)
        self.metadata_file = metadata_file
        self.mode = mode
        self.port = port
        self.env = env
        self.process = None

    def run(self):
        args = f"--metadata_file {self.metadata_file} --mode {self.mode} --port {self.port}"
        self.process = runProgram(self.program, args, popen=True)

    def stop(self):
        os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)

class ClientQThread(QThread):
    finished = pyqtSignal()
    volume = pyqtSignal(object)
    chimera = pyqtSignal()

    def __init__(self, port, path, mode):
        super().__init__()
        self.client = Client(port)
        self.path = path
        self.mode = mode
        self.z = None
        self.file_names = None

    def readMap(self, file):
        map = ImageHandler().read(file).getData()
        return np.squeeze(map)

    def run(self):
        np.savetxt(os.path.join(self.path, "z_server.txt"), self.z)
        while not os.path.isfile(os.path.join(self.path, "z_server.txt")) and not os.access(os.path.join(self.path, "z_server.txt"), os.R_OK):
            time.sleep(0.01)
        self.client.sendDataToSever(os.path.join(self.path, "z_server.txt"))

        # Read generated volume
        if self.mode == "Zernike3D":
            vol_file = os.path.join(self.path, "deformed_{:02d}.mrc")
        elif self.mode == "CryoDrgn":
            vol_file = os.path.join(os.path.join(self.path, "vol_{:03d}.mrc"))
        elif self.mode == "HetSIREN":
            vol_file = os.path.join(os.path.join(self.path, "decoded_map_class_{:02d}.mrc"))
        elif self.mode == "NMA":
            vol_file = os.path.join(os.path.join(self.path, "decoded_map_class_{:02d}.mrc"))
        elif self.mode == "3DFlex":
            vol_file = os.path.join(os.path.join(self.path, "decoded_map_class_{:02d}.mrc"))

        # Emit signals
        if self.z.shape[0] == 1:
            generated_map = self.readMap(vol_file.format(1))
            self.volume.emit(generated_map)
            os.remove(vol_file.format(1))
        else:
            for idx in range(self.z.shape[0]):
                new_path = os.path.join(self.path, self.file_names[idx] + ".mrc")
                if vol_file.format(idx + 1) != new_path:
                    ImageHandler().convert(vol_file.format(idx + 1), new_path, overwrite=True)
                    os.remove(vol_file.format(idx + 1))

        # Emit signals
        if self.z.shape[0] > 1:
            self.chimera.emit()
        self.finished.emit()
