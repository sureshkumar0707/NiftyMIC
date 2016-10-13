
## Import libraries 
from scipy.sparse.linalg import LinearOperator

import SimpleITK as sitk
import itk
import numpy as np
from scipy.optimize import minimize
from scipy.optimize import leastsq
from scipy import ndimage
import unittest
import matplotlib.pyplot as plt
import sys
import time
import datetime

## Add directories to import modules
dir_src_root = "../../src/"
# sys.path.append(dir_src_root)
sys.path.append(dir_src_root + "base/")
sys.path.append(dir_src_root + "preprocessing/")
sys.path.append(dir_src_root + "reconstruction/")
sys.path.append(dir_src_root + "reconstruction/solver/")
sys.path.append(dir_src_root + "reconstruction/regularization_parameter_estimator/")

## Import modules
import SimpleITKHelper as sitkh
import DataPreprocessing as dp
import Stack as st
import StackManager as sm
import ScatteredDataApproximation as sda
import TikhonovSolver as tk
import TVL2Solver as tvl2
import AnalysisRegularizationParameterEstimator as arpe


"""
Functions
"""

def read_input_data():
    ## Fetal Neck Images:
    dir_input = "../../data/fetal_neck_mass_brain/"
    # filenames = [
    #     "20150115_161038s006a1001_crop",
    #     "20150115_161038s003a1001_crop",
    #     "20150115_161038s004a1001_crop",
    #     "20150115_161038s005a1001_crop",
    #     "20150115_161038s007a1001_crop",
    #     "20150115_161038s5005a1001_crop",
    #     "20150115_161038s5006a1001_crop",
    #     "20150115_161038s5007a1001_crop"
    #     ]

    filenames = [str(i) for i in range(0, 8)]
    filenames.remove("6")

    filenames = [str(i) for i in range(0, 3)]

    return dir_input, filenames


"""
Main Function
"""
if __name__ == '__main__':

    np.set_printoptions(precision=3)

    target_stack_number = 0
    mask_template_number = target_stack_number
    dilation_radius = 0
    extra_frame_target = 5
    SDA_sigma = 0.7


    dir_input_data, filenames_data = read_input_data()

    ## Data Preprocessing from data on HDD
    data_preprocessing = dp.DataPreprocessing.from_filenames(dir_input_data, filenames_data, suffix_mask="_mask")
    data_preprocessing.set_dilation_radius(dilation_radius)
    data_preprocessing.use_N4BiasFieldCorrector(False)
    data_preprocessing.run_preprocessing(boundary=0, mask_template_number=mask_template_number)

    stacks = data_preprocessing.get_preprocessed_stacks()

    ## Get initial value for reconstruction
    stack_manager = sm.StackManager.from_stacks(stacks)

    HR_volume_ref_frame = stacks[target_stack_number].get_isotropically_resampled_stack(extra_frame=extra_frame_target)

    SDA = sda.ScatteredDataApproximation(stack_manager, HR_volume_ref_frame)
    SDA.set_sigma(SDA_sigma)
    SDA.run_reconstruction()

    HR_volume_init = SDA.get_HR_volume()
    # HR_volume_init.show()



    ## Super-Resolution Reconstruction
    SRR_alpha_cut = 3 
    SRR_approach = "TK1"
    SRR_alpha = 0.02
    SRR_iter_max = 3

    SRR_rho = 0.5
    SRR_ADMM_iterations = 2
    SRR_ADMM_iterations_output_dir = "/tmp/TV-L2_ADMM_iterations/"
    

    # SRR_tolerance = 1e-5
    # SRR_DTD_computation_type = "FiniteDifference"
    # HR_volume = st.Stack.from_stack(HR_volume_init)
    # SRR = ips.InverseProblemSolver(stacks, HR_volume)
    # SRR.set_regularization_type(SRR_approach)
    # SRR.set_alpha_cut(SRR_alpha_cut)
    # SRR.set_tolerance(SRR_tolerance)
    # SRR.set_alpha(SRR_alpha)
    # SRR.set_iter_max(SRR_iter_max)
    # SRR.set_DTD_computation_type(SRR_DTD_computation_type)
    # SRR.run_reconstruction()

    # HR_volume = SRR.get_HR_volume()
    # HR_volume.show()

    # SRR = tk.TikhonovSolver(stacks, HR_volume_init)
    # SRR.set_regularization_type(SRR_approach)

    # # SRR = tvl2.TVL2Solver(stacks, HR_volume_init)
    # # SRR.set_rho(SRR_rho)
    # # SRR.set_ADMM_iterations(SRR_ADMM_iterations)
    # # SRR.set_ADMM_iterations_output_dir(SRR_ADMM_iterations_output_dir)

    # SRR.set_alpha(SRR_alpha)
    # SRR.set_iter_max(SRR_iter_max)
    # SRR.run_reconstruction()
    # SRR.compute_statistics()
    # SRR.print_statistics()

    # HR_volume = SRR.get_HR_volume()
    # HR_volume.show()


    """
    Regularization Parameter Estimation
    """
    alphas = np.array([0.001, 0.005, 0.01, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1, 2, 3,4,5,6,7,8,9,10])
    alphas = alphas[::2]
    alphas = alphas[:3]
    rhos = [1,2]
    ADMM_iterations=1
    print("Compute %s iterations with alpha in %s" %(len(alphas),str(alphas)))
    # regularization_types = ["TK0", "TK1", "TV-L2"]
    # regularization_types = ["TV-L2"]
    # regularization_types = ["TK1"]
    dir_output = "/tmp/RegularizationParameterEstimation/"
    filenames = []

    # regularization_parameter_estimator = tkrpe.TikhonovRegularizationParameterEstimator(stacks, HR_volume_init, alpha_cut=SRR_alpha_cut, iter_max=SRR_iter_max, alpha_array=alphas, dir_results=dir_output, reg_type=SRR_approach)

    # regularization_parameter_estimator = tvl2rpe.TikhonovRegularizationParameterEstimator(stacks, HR_volume_init, alpha_cut=SRR_alpha_cut, iter_max=SRR_iter_max, alpha_array=alphas, dir_results=dir_output, ADMM_iterations=ADMM_iterations, rho_array=rhos, ADMM_iterations_output_dir="TV-L2_ADMM_iterations/", ADMM_iterations_output_filename_prefix="TV-L2")

    # regularization_parameter_estimator.run_reconstructions(save_flag=1)
    # filename = regularization_parameter_estimator.get_filename_of_txt_file()

    # filenames.append(filename)


    analysis_regularization_parameter_estimator = arpe.AnalysisRegularizationParameterEstimator(stacks, HR_volume_init, dir_results=dir_output, alpha_cut=SRR_alpha_cut, iter_max=SRR_iter_max, alpha_array=alphas, rho_array=rhos, ADMM_iterations=ADMM_iterations, ADMM_iterations_output_dir="TV-L2_ADMM_iterations/", ADMM_iterations_output_filename_prefix="TV-L2")
    analysis_regularization_parameter_estimator.set_regularization_types(["TK0","TK1","TV-L2"])

    analysis_regularization_parameter_estimator.run_reconstructions()
    analysis_regularization_parameter_estimator.show_L_curves()

    # regularization_parameter_estimation = rpe.RegularizationParameterEstimation(stacks, HR_volume_init)
    # regularization_parameter_estimation.set_alpha_array(alphas)
    # regularization_parameter_estimation.set_rho(rho)
    # regularization_parameter_estimation.set_ADMM_iterations(5)
    # regularization_parameter_estimation.set_regularization_types(regularization_types)

    # # regularization_parameter_estimation.run_reconstructions(save_flag=1)

    # L_curve_files_TK = [
    #      "RegularizationParameterEstimation/TK0-Regularization_itermax30"
    #     ,"RegularizationParameterEstimation/TK1-Regularization_itermax30"
    #     ]
    # L_curve_files_TV = [
    #      "RegularizationParameterEstimation/TV-L2-Regularization_rho0.5_ADMM_iterations15_TK1itermax10"
    #     ,"RegularizationParameterEstimation/TV-L2-Regularization_rho1_ADMM_iterations15_TK1itermax10"
    #     ,"RegularizationParameterEstimation/TV-L2-Regularization_rho1.5_ADMM_iterations15_TK1itermax10"
    #     ,"RegularizationParameterEstimation/TV-L2-Regularization_rho0.5_ADMM_iterations5_TK1itermax10"
    #     ,"RegularizationParameterEstimation/TV-L2-Regularization_rho1_ADMM_iterations5_TK1itermax10"
    #     ,"RegularizationParameterEstimation/TV-L2-Regularization_rho1.5_ADMM_iterations5_TK1itermax10"
    #     ]

    # regularization_parameter_estimation.analyse(from_files=L_curve_files_TV, save_flag=0)



