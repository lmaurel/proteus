#!/usr/bin/env python
"""

Test module for 2D Quadrilateral Meshes

"""
from proteus.iproteus import *
from proteus import Comm
from proteus import LinearAlgebraTools
comm = Comm.get()
Profiling.logLevel=7
Profiling.verbose=True
import numpy.testing as npt
from nose.tools import ok_ as ok
from nose.tools import eq_ as eq
from nose.tools import set_trace
from petsc4py import PETSc as p4pyPETSc
from scipy.sparse import csr_matrix
import numpy as np


def test_sparse_2_dense():
    '''
    This function tests the petsc4py_sparse_2_dense function in the
    LinearAlgebraTools module.
    '''
    from proteus import LinearAlgebraTools
    vals    = [10.,-2.,3.,9.,3.,7.,8.,7.,3.,8.,7.,5.,8.,9.,9.,13.,4.,2.,-1.]
    col_idx = [0  , 4 ,0 ,1 ,5 ,1 ,2 ,3 ,0 ,2 ,3 ,4 ,1 ,3 ,4 ,5  ,1 ,4 , 5 ]
    row_idx = [0, 2, 5, 8, 12, 16, 19]
    size_n  = len(row_idx)-1 
    petsc_mat = p4pyPETSc.Mat().createAIJ(size = (size_n,size_n), \
                                          csr  = (row_idx, col_idx, vals))
    dense_mat = LinearAlgebraTools.petsc4py_sparse_2_dense \
                (petsc_mat.getValuesCSR())
    comparison_mat = np.loadtxt('sparse_mat_1.txt')
    assert np.allclose(dense_mat,comparison_mat)

def test_Qp_mat():
    '''
    First, verify that Qp returns the correct pressure mass matrix
    Second, verfity that QpShell performs matrix multiplies correctly
    '''
    # import and run a small 2D poiseulle problem
    import stokes_2d_p
    import stokes_2d_n
    pList = [stokes_2d_p]
    nList = [stokes_2d_n]    
    so = default_so
    so.tnList = [0.,1.]
    so.name = pList[0].name
    so.sList=[default_s]
    opts.verbose=True
    opts.profile=True
    ns = NumericalSolution.NS_base(so,pList,nList,so.sList,opts)
    # *** 1 *** : test the pressure mass matrix is being created properly.
    smoother = LinearSolvers.NavierStokes3D_Qp(L=ns.modelList[0].par_jacobianList[1])
    operator_constructor = LinearSolvers.schurOperatorConstructor(smoother, 'stokes')
    Qp_raw = operator_constructor.getQp()
    Qp_dense = LinearAlgebraTools.petsc4py_sparse_2_dense(Qp_raw.getValuesCSR())
    pressure_mass_matrix = np.loadtxt('pressure_mass_matrix.txt')
    assert np.allclose(pressure_mass_matrix,Qp_dense)
    # *** 2 *** test QpShell performs a matrix vector product correctly
    ksp_dummy = p4pyPETSc.KSP().create()
    ksp_dummy.pc.setFieldSplitSchurPreType(0)
    ksp_dummy.pc.setFieldSplitSchurFactType(0)
    import pdb
    pdb.set_trace()
    smoother.setUp(ksp_dummy)
    

    # vector_x = p4pyPETSc.Vec().create()
    # vector_x1 = p4pyPETSc.Vec().create()
    # vector_y = p4pyPETSc.Vec().create()
    # vector_b = p4pyPETSc.Vec().create()
    # vector_x.setType('standard')
    # vector_x1.setType('standard')
    # vector_y.setType('standard')
    # vector_b.setType('standard')
    # vector_x.setSizes(len(pressure_mass_matrix[0]),len(pressure_mass_matrix[0]))
    # vector_x1.setSizes(len(pressure_mass_matrix[0]),len(pressure_mass_matrix[0]))
    # vector_y.setSizes(len(pressure_mass_matrix[0]),len(pressure_mass_matrix[0]))
    # vector_b.setSizes(len(pressure_mass_matrix[0]),len(pressure_mass_matrix[0]))
    # vector_x.set(1)
    # vector_b.set(1)
    # matrix.Qp_shell.mult(vector_x,vector_y)
    # matrix.QpInv_shell.mult(vector_x1,vector_b)
    

    # TODO - verify true_y
#    true_y = np.array([[0.16666667,0.333333333,0.166666667,0.33333333,0.5,1.,0.5,0.5,0.5]])
#    assert np.allclose(vector_y,true_y)


if __name__ == '__main__':
    from proteus import Comm
    comm = Comm.init()
    test_sparse_2_dense()
    test_Qp_mat()

    # test = LinearSolvers.KSP_petsc4py(ns.modelList[0].jacobianList[0],
    #                                   ns.modelList[0].par_jacobianList[0],
    #                                   Preconditioner=SimpleNavierStokes3D)