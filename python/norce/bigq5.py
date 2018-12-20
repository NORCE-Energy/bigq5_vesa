import jsoncomment
import json
import numpy as np
import os

def read_json_comment(fn):
    """ The format of the input file 'fn' should be JSON, except
    that the outermost braces '{' '}' is stripped off.
    Comments, i.e. lines starting with a '#' are also allowed.
    """
    print("Reading input parameters from {}".format(fn))
    with open(fn, 'r') as fh:
        json_str = fh.read()
    json_str = '{' + json_str + '}'
    json_dict = jsoncomment.JsonComment(json).loads(json_str)
    return json_dict
    

class Realization:
    """ Generates a realization of the top surface from a random field 
    with a normal with mean, variance, and covariance in accordance with
    the input parameters given in the dict 'cfg'.
    """
    def __init__(self, cfg):
        self.cfg = cfg
        self.set_cfg_data()
        self.gen_x_y_vectors()
        self.h_mean = 0
        self.sigma = self.calc_sigma_according_to_height_variation_and_confidence()
        self.variance = self.sigma ** 2
        if self.seed:  # skip setting seed if self.seed == 0
            np.random.seed(self.seed)
        self.num_points = ( self.nx + 1) * ( self.ny + 1)
        self.num_cells = self.nx * self.ny


    def compute_cholesky_matrix(self, cov):
        L = np.linalg.cholesky(cov)
        #print('Sparsity of covariance matrix: {}'.format(
        #    self.compute_matrix_sparsity(cov)))
        self.L = L

    def compute_covariance_matrix(self):
        [xx, yy] = np.meshgrid(self.x, self.y)
        self.xx = xx
        self.yy = yy
        cov = self.gen_covariance(xx, yy)
        return cov

    def gen_realization(self):
        H, xx, yy = self.gen_real(self.L, self.xx, self.yy)
        H = self.add_domain_tilt(H, xx)
        self.H = self.add_domain_curvature(H, yy)
        self.Z_top = -(self.reservoir_depth - self.reservoir_thickness - self.H)
        
    def gen_real(self, L, xx, yy):
        """ The cholesky factorization L of the covariance matrix for
        a multivariate standard normal distribution with given mean and 
        standard deviation is used to generate realizations with the same
        mean, correlation and standard deviation.
        See docs/cholesky.pdf for more information.
        """
        Z = np.random.standard_normal((self.num_cells, 1))
        real = self.h_mean + np.dot(L.T, Z)
        H = real.reshape((self.nx, self.ny)).T
        H, xx, yy = self.remove_artifacts_from_solution(H, xx, yy)
        return H, xx, yy

    def write_reservoir_thickness(self):
        if self.output_thickness:
            fn = 'H.IN'
            print("Writing {} ..".format(fn))
            H = self.reservoir_thickness * np.ones(self.Z_top.shape)
            fn_path = os.path.join(self.output_dir, fn)
            np.savetxt(fn_path, H.flatten())
       
    def write_top_surface(self, print_msg=True):
        fn = 'REFHT.IN'
        if print_msg:
            print("Writing {} ..".format(fn))
        fn_path = os.path.join(self.output_dir, fn)
        np.savetxt(fn_path, self.Z_top.flatten())
       
    def gen_x_y_vectors(self):
        """ Due to a bug (?), unexpected large values can be observed in the
        first row and first column of the Cholesky matrix, and hence in 
        the corresponding height realization matrix.
        TODO: Come back to this problem later, currently we do a quick fix
        and simply remove those elememts from the realization.
        See method remove_artifacts_from_solution()
        """
        self.remove_artifacts = {
            'delete_first_row': True,
            'delete_first_column': True
        }
        x_min = 0
        x_max = self.reservoir_xy_size[0]
        y_min = 0
        y_max = self.reservoir_xy_size[1]
        dx = (x_max - x_min)/self.nx
        dy = (y_max - y_min)/self.ny
        self.nx = self.nx + 1
        self.ny = self.ny + 1
        x_min = x_min - dx
        y_min = y_min - dy
        x = np.linspace(x_min + dx/2, x_max - dx/2, self.nx)
        y = np.linspace(y_min + dy/2, y_max - dy/2, self.ny)
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max
           
           
    def remove_artifacts_from_solution(self, H, x, y):
        """ Quick fix for strange problem with cholesky factorization.
        See docs/cholesky.pdf for further information.
        """
        if self.remove_artifacts['delete_first_row']:
            x = x[1:, :]
            y = y[1:, :]
            H = H[1:, :]
        if self.remove_artifacts['delete_first_column']:
            x = x[:, 1:]
            y = y[:, 1:]
            H = H[:, 1:]
        return H, x, y
           
           
    def add_domain_curvature(self, H, yy):
        """ Adds a curvature to H according to its corresponding y-coordinate.
        See docs/setup.pdf for further information
        """
        y = yy[:, 0]
        L = (self.y_max - self.y_min)/2
        curvature = self.domain['curvature']
        if curvature < 0 or curvature > 1:
            raise Exception('Bad value for domain curvature')
        if curvature == 0:
            return H
        radius = L / curvature 
        theta = np.arccos(L/radius)
        h0 = radius * np.sin(theta)
        y0 = (self.y_min + self.y_max)/2
        h = np.zeros(y.shape)
        for i, yi in enumerate(y):
            alpha = np.arccos((yi - y0)/radius)
            h[i] = radius * np.sin(alpha) - h0
        H = H + h[:,np.newaxis]
        return H
       
       
    def add_domain_tilt(self, H, xx):
        """ adds a tilt by increasing height values H according to
        their x position along the x-axis and the tilt angle
        """
        x = xx[0,:]
        tilt_factor = np.tan((self.domain['tilt_angle']/180)*np.pi)
        H = H + tilt_factor*(x-x[0])
        return H

    def compute_matrix_sparsity(self, A):
        return (A.size - np.count_nonzero(A)) / A.size;
        
    def calc_sigma_according_to_height_variation_and_confidence(self):
        """ The standard deviation, sigma, of the standard normal probability
        distribution is adjusted such that 

        hr = self.num_std_dev_confidence_delta_h * sigma
        
        where 

           hr = self.requested_delta_h

        Then the confidence level that the sample height is in the requested
        interval, [-hr, hr], can be calculated from the cummulative
        distribution function of the normal distribution. For example if 

        self.num_std_dev_confidence_delta_h = 3

        There will be a 99.7% probability that h will lie in the requested interval
        (according to the 3-sigma rule, see 

          https://en.wikipedia.org/wiki/68%E2%80%9395%E2%80%9399.7_rule

        )
        """
        sigma = self.requested_delta_h / self.num_std_dev_confidence_delta_h
        return sigma


    def gen_covariance(self, xx, yy):
        """ The covariance matrix is based on a desired variance self.variance
        and a given variogram model.
        """
    
        dist = self.calc_dist_matrix(xx, yy)
        self.variogram['range'] = self.range_x
        variogram = Variogram(self.variance, self.variogram)
        return variogram.get_gamma(dist)  #convert variogram to covariance

    def calc_dist_matrix(self, xx, yy):
        """ Calculates a distance matrix. This matrix incorporates a
        scaling of the y-coordinate according to the values of the
        input parameters self.range_x and self.range_y. In this way,
        this matrix can be used to create a covariance matrix, see
        gen_covariance() 
        """
        scale_y = self.range_x / self.range_y
        yy = scale_y * yy
        pos = np.vstack((xx.flatten('F'), yy.flatten('F'))).T
        n = pos.shape[0]
        dist = np.zeros((n, n))
    
        for i in range(n):
            dist[i, :] = np.linalg.norm(pos[i,:] - pos, axis=1)
        return dist


    def set_cfg_data(self):
        """ Imports the top level key-value items in the dict self.cfg
        as class variables
        """
        defaults = {
            'output_dir': '.',
            'output_thickness': False,
            'seed': 0
        }
            
        for key, value in defaults.items():
            setattr(self, key, value)
        for key, value in self.cfg.items():
            setattr(self, key, value)

class Variogram:
    """ Encapsulates different variogram models.
    The variogram models are constructed based on a given variance.
    See docs/variogram.pdf for more information.
    """
    def __init__(self, variance, cfg):
        """ Constructor: input arguments:
        - variance : variance
        - cfg   : dictionary of configuration parameters
        """
        self.variance = variance
        self.set_cfg_data(cfg)
    
    def set_cfg_data(self, cfg):
        for key, value in cfg.items():
            setattr(self, key, value)
        
    def get_gamma(self, dist):
        """ Compute variogram given distance matrix or vector 'dist'
        """
        if self.type == 'exponential':
            low = np.full(dist.shape, True)
        else:
            low = dist < self.range
        y = dist * 0
        getattr(self, self.type)(dist, low, y)
        return y

    def exponential(self, h, low, y):
        a = self.range / 8
        y[low] = self.variance * (np.exp(-h[low] / a))
    
    def spherical(self, h, low, y):
        y[low] = self.variance * (1 - ((3/2) * np.fabs(h[low]) / self.range
                        - (1/2) * (h[low] / self.range) ** 3))
    
    def sinxx(self, h, low, y):
        with np.errstate(divide='ignore',invalid='ignore'):
            h2 = h[low] * (np.pi/self.range)
            x = np.sin(h2) / h2
            x[np.isnan(x)] = 1
            y[low] = self.variance * x
    
    def triangle(self, h, low, y):
        y[low] = self.variance * (1 - h[low]/self.range);
    
            
