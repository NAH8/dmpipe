#!/usr/bin/env python
#

"""
Interface to Dark Matter spectra
"""

import os
import sys
import argparse

import yaml

from astropy.table import Table

from dmpipe.dm_spectral import DMCastroData
from dmpipe.dm_plotting import plot_dm_castro


        
def main():
    """
    """
    # Argument defintion
    usage = "usage: %(prog)s [input]"    
    description = "Collect all the new source"
    
    parser = argparse.ArgumentParser(usage=usage,description=description)
    parser.add_argument('--chan', '-c', required=True, help='Channel')
    parser.add_argument('--input', '-i', required=True, help='Input FITS file')
    
    # Argument parsing
    args = parser.parse_args()

    tab_m = Table.read(args.input, hdu="MASSES")
    tab_s = Table.read(args.input, hdu=args.chan)
    dm_castro = DMCastroData.create_from_tables(tab_s, tab_m)

    dm_plot = plot_dm_castro(dm_castro)
    return dm_plot


if __name__=='__main__':
    dm_plot = main()
