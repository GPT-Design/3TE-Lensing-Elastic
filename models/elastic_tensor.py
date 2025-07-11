"""
elastic_tensor.py — Elastic Shear Tensor utilities for 3T_E

Provides:
- G-coupled elastic stress computation
- Scalar field gradient stubs for deformation field φ^I
"""

import numpy as np

def elastic_tensor_Tmunu(phi_fields, gmunu=None, shear_modulus=1e-9):
    """
    Compute elastic shear tensor T^{(elastic)}_{μν}

    Parameters:
        phi_fields: list of N scalar fields φ^I defined on a 2D/3D array (e.g. [φ1, φ2, φ3])
        gmunu: optional metric tensor (defaults to flat)
        shear_modulus: G [Pa]

    Returns:
        T_elastic: 2D numpy array (μν components)
    """
    ndim = phi_fields[0].ndim
    n_phi = len(phi_fields)

    grads = [np.gradient(phi) for phi in phi_fields]
    T = np.zeros((ndim, ndim))

    for μ in range(ndim):
        for ν in range(ndim):
            sum_terms = sum(grads[i][μ] * grads[i][ν] for i in range(n_phi))
            trace_term = sum(grads[i][α] @ grads[i][α] for i in range(n_phi) for α in range(ndim))
            T[μ, ν] = shear_modulus * (sum_terms - (1/3) * (trace_term if gmunu is None else gmunu[μ][ν] * trace_term))

    return T

 
 
