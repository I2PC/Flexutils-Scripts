#!/usr/bin/env python
# **************************************************************************
# *
# * Authors:  David Herreros Calero (dherreros@cnb.csic.es)
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

import numpy as np

from flexutils_scripts import utils as utl

from xmipp_metadata.metadata import XmippMetaData

from joblib import Parallel, delayed


def iterRowsAndClone(metadata):
    row = md.Row()
    for objId in metadata:
        row.readFromMd(metadata, objId)
        yield row.clone()


def computeNewDeformationField(row, Z, start_coords, mask_DF, Z_new):
    outRow = row
    z_clnm = row["MDL_SPH_COEFFICIENTS"]
    A = utl.resizeZernikeCoefficients(z_clnm)

    # Get Masked deformation field
    A_masked = utl.maskDeformationField(A, Z, start_coords, mask_DF, Z_new=Z_new)

    # Write Zernike3D coefficients to file
    z_clnm = utl.resizeZernikeCoefficients(A_masked)
    outRow["MDL_SPH_COEFFICIENTS"] = z_clnm

    # For evaluation (debuggin purposes)
    d = Z_new @ A_masked.T

    # Compute mean deformation
    deformation = np.sqrt(np.mean(np.sum(d ** 2, axis=1)))
    outRow["MDL_SPH_DEFORMATION"] = deformation

    return outRow


def maskDeformationField(md_file, maski, maskdf, prevL1, prevL2, L1, L2, Rmax, thr):
    # Read data
    start_mask = utl.readMap(maski)
    mask_DF = utl.readMap(maskdf)

    # Get Xmipp origin
    xmipp_origin = utl.getXmippOrigin(start_mask)

    # Get original coords in mask
    start_coords = utl.getCoordsAtLevel(start_mask, 1)
    start_coords_xo = start_coords - xmipp_origin

    # Metadata
    metadata = XmippMetaData(md_file)
    # metadata.sort()
    # rows = [row.clone() for row in md.iterRows(metadata)]
    # rows = Parallel(n_jobs=thr, verbose=100)(delayed(lambda x: x.clone())(row) for row in metadata)

    # Compute original deformation field
    Z = utl.computeBasis(L1=prevL1, L2=prevL2, pos=start_coords_xo, r=Rmax)
    Z_new = utl.computeBasis(L1=L1, L2=L2, pos=start_coords_xo, r=Rmax)

    # Compute new deformation field
    outRows = Parallel(n_jobs=thr, verbose=100) \
              (delayed(lambda x: computeNewDeformationField(x, Z, start_coords, mask_DF, Z_new))(row)
              for row in metadata)

    # Fill output metadata
    metadata_out = XmippMetaData(None)
    for outRow in outRows:
        metadata_out.appendMetaDataRows(outRow)

    dir = os.path.dirname(md_file)
    metadata_out.write(os.path.join(dir, "inputParticles_focused.xmd"), overwrite=True)


def main():
    import argparse

    # Input parameters
    parser = argparse.ArgumentParser()
    parser.add_argument('--i', type=str, required=True)
    parser.add_argument('--maski', type=str, required=True)
    parser.add_argument('--maskdf', type=str, required=True)
    parser.add_argument('--prevl1', type=int, required=True)
    parser.add_argument('--prevl2', type=int, required=True)
    parser.add_argument('--l1', type=int, required=True)
    parser.add_argument('--l2', type=int, required=True)
    parser.add_argument('--rmax', type=float, required=True)
    parser.add_argument('--thr', type=int, required=True)

    args = parser.parse_args()

    # Initialize volume slicer
    maskDeformationField(args.i, args.maski, args.maskdf, args.prevl1, args.prevl2,
                         args.l1, args.l2, args.rmax, args.thr)
