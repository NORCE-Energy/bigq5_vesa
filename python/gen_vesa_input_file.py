#! /usr/bin/env python3
"""
Generates a top surface to be used as input for the VESA
simulator.

The top surface is created as a realization of multivariate
normal distribution with a given mean, variance, and covariance
matrix. See documentation file docs/main.pdf for more information.

Most of the parameters for the surface generation are fixed in a 
JSON input file "input_params.json", while a remaining 3 parameters 
are given on the command line when running this script.
See the documentation file docs/main.pdf for more information about
the setup and the parameters.

The "fixed" parameters are as follows:

- "curvature" : 0.005
- "tilt_angle" : 0.477
- "num_std_dev_confidence_delta_h" : 3 
- "nx" : 200
- "ny" : 125
- "reservoir_depth" : 1000
- "reservoir_thickness" : 100
- "variogram.type" : "spherical"
- "reservoir_xy_size" : [50000, 25000]

The remaining three parameters are "dynamic",  i.e. given on the command line.
They determine the shape of the stochastically 
ridge-like features [1] that are added to the top surface, see the documentation
file docs/main.pdf for more information. The parameters are:

- "range_x" (the width of the ridges should be less than range_y)
- "range_y" (the length of the ridges)
- "requested_delta_h" (the amplitude of the ridges)

See also documentation files in the docs folder for more information.


References: 
1. Nilsen, Halvor Møll, et al. "Impact of top-surface morphology on CO2
storage capacity." International Journal of Greenhouse Gas Control, 11
(2012): 221-235.  

2. Jean-Paul, Chilès, and Delfiner Pierre. "Geostatistics: modeling
spatial uncertainty." John Wiley & Sons Inc., New Jersey (2012).

Author: H.H. (based on code by S. Tveitt and R. Kaufmann)
Date: December 2018

"""
import argparse
import json
import numpy as np
import os
import time

import norce.bigq5

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('range_x', type=float)
    parser.add_argument('range_y', type=float)
    parser.add_argument('requested_delta_h', type=float)
    cmd_line_args = parser.parse_args()
    cfg = norce.bigq5.read_json_comment('input_params.json')
    main_prog = MainProgram(cmd_line_args, cfg)

class MainProgram:
    def __init__(self, cmd_line_args, cfg):
        self.cfg = cfg
        self.add_cmd_line_arguments_to_cfg(cmd_line_args)
        t_start = self.start_timer('')
        real = norce.bigq5.Realization(self.cfg)
        t0 = self.start_timer('Generating covariance matrix..')
        cov = real.compute_covariance_matrix()
        self.show_run_time(t0)
        t0 = self.start_timer('Generating cholesky matrix..')
        real.compute_cholesky_matrix(cov)
        cov = None # Free up memory allocated for covariance matrix
        self.show_run_time(t0)
        t0 = self.start_timer('Generating realization..')
        real.gen_realization()
        self.show_run_time(t0)
        real.write_top_surface()

        
    def add_cmd_line_arguments_to_cfg(self, cmd_line_args):
        self.cfg['range_x'] = cmd_line_args.range_x
        self.cfg['range_y'] = cmd_line_args.range_y
        self.cfg['requested_delta_h'] = cmd_line_args.requested_delta_h
        return 
        
    def start_timer(self, msg):
        if len(msg) > 0:
            print(msg)
        t0 = time.time()
        return t0
    
    def show_run_time(self, t0, msg=None):
        t1 = time.time()
        if msg is None:
            print('  Finished in {:.4g} seconds..'.format(t1-t0))
        else:
            print(msg.format(t1-t0))
        
    
if __name__ == "__main__":
    main()
