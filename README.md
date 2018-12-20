# VESA top surface generator
This repository provides a script that can generate a reservoir top
surface for the VESA simulator [1].

![Top surface](images/surf_25x25.png?raw=true&s=50)

The top surface is created as a realization of a multivariate
normal distribution with a given mean, variance, and covariance
matrix. The covariance function can have a different range in the
x- and y-directions, in order to model offshore sand ridges, see [3].

The generated top surfaces has a tilt angle in x-direction and is curved
slightly in the y-direction. This type of reservoir model can then be applied in numerical
simulation of CO2 storage to study how the top surface morphology of the
reservoir can impact storage 
capacity [3]. 

More documentation is available in LaTeX format. To generate
the PDF documentation, run

```
$ make docs
```

it requires that `latex`, `bibtex` and `latexmk` are installed.

VESA input files (except for the top surface, since it will be generated
by the script) for a 200x125 size grid of a 50km x 25km domain with CO2 injection into an
aquifer at lower bottom region is also provided (see the folder
`vesa_case_dir`). By default, the script will take three input
parameters on the command line and save the generated top surface in
the provided directory `vesa_case_dir` with VESA input files. For
example the following command line
```
$ cd python
$ gen_vesa_input_file.py 5000 40000 50
```

will generate a top surface with range_x=5000, range_y=40000, and an
amplitude of 50, and save the top surface as `REFHT.IN` in
`vesa_case_dir`.

Provided you have installed the VESA simulator, you can now run the 
simulation:

```
$ cd ../vesa_case_dir
$ $VESA_INSTALL_DIR/vesa
```
The simulator generates a set of output files, among others the CO2 saturation
at the end of the simulation.
If you plot the projection of this CO2 saturation in xy-plane after some time you can get

![CO2 saturation](images/co2sat.png?raw=true&s=50)

We plan to use the script to generate multiple realizations for
different sets of the three command line parameters, then run the VESA
simulator for
each model and monitor the change in breakthrough curve for CO2. Hence, we
will get a mapping between the parameters and the resulting
breakthrough curve that can be use as training data in a machine
learning algorithm.

# References

1. S.E. Gasda, J.M. Nordbotten, and M.A. Celia.
*Vertical equilibrium with sub-scale analytical methods for geological
  CO2 sequestration.* Comput. Geosci., 13(4): 469-481, 2009.

2. Jean-Paul, Chilès, and Delfiner Pierre. *Geostatistics: modeling
spatial uncertainty.* John Wiley & Sons Inc., New Jersey (2012).

3. Nilsen, Halvor Møll, et al. *Impact of top-surface morphology on CO2
storage capacity.* International Journal of Greenhouse Gas Control, 11
(2012): 221-235.


