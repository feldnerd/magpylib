""" getBHv wrapper codes"""

import numpy as np
from scipy.spatial.transform import Rotation as R
from magpylib._lib.fields.field_wrap_BH_level1 import getBH_level1
from magpylib._lib.exceptions import MagpylibBadUserInput


def getBHv_level2(**kwargs: dict) -> np.ndarray:
    """ Direct access to vectorized computation

    Parameters
    ----------
    kwargs: dict that describes the computation.

    Returns
    -------
    field: ndarray, shape (N,3), field at obs_pos in [mT] or [kA/m]

    Info
    ----
    - check inputs

    - secures input types (list/tuple -> ndarray)
    - test if mandatory inputs are there
    - sets default input variables (e.g. pos, rot) if missing
    - tiles 1D inputs vectors to correct dimension
    """
    # pylint: disable=too-many-branches
    # pylint: disable=too-many-statements

    # generate dict of secured inputs for auto-tiling ---------------
    #  entries in this dict will be tested for input length, and then
    #  be automatically tiled up and stored back into kwargs for calling
    #  getBH_level1().
    #  To allow different input dimensions, the tdim argument is also given
    #  which tells the program which dimension it should tile up.
    tile_params = {}

    # mandatory general inputs ------------------
    try:
        src_type = kwargs['source_type']
        poso = np.array(kwargs['observer'], dtype=float)
        tile_params['observer'] = (poso,2)    # <-- (input,tdim)

        # optional general inputs -------------------
        # if no input set pos=0
        pos = np.array(kwargs.get('position', (0,0,0)), dtype=float)
        tile_params['position'] = (pos,2)
        # if no input set rot=unit
        rot = kwargs.get('orientation', R.from_quat((0,0,0,1)))
        tile_params['orientation'] = (rot.as_quat(),2)
        # if no input set squeeze=True
        squeeze = kwargs.get('squeeze', True)

        # mandatory class specific inputs -----------
        if src_type == 'Box':
            mag = np.array(kwargs['magnetization'], dtype=float)
            tile_params['magnetization'] = (mag,2)
            dim = np.array(kwargs['dimension'], dtype=float)
            tile_params['dimension'] = (dim,2)

        elif src_type == 'Cylinder':
            mag = np.array(kwargs['magnetization'], dtype=float)
            tile_params['magnetization'] = (mag,2)
            dim = np.array(kwargs['dimension'], dtype=float)
            tile_params['dimension'] = (dim,2)

        elif src_type == 'Sphere':
            mag = np.array(kwargs['magnetization'], dtype=float)
            tile_params['magnetization'] = (mag,2)
            dia = np.array(kwargs['diameter'], dtype=float)
            tile_params['diameter'] = (dia,1)

        elif src_type == 'Dipole':
            moment = np.array(kwargs['moment'], dtype=float)
            tile_params['moment'] = (moment,2)

        elif src_type == 'Circular':
            current = np.array(kwargs['current'], dtype=float)
            tile_params['current'] = (current,1)
            dia = np.array(kwargs['diameter'], dtype=float)
            tile_params['diameter'] = (dia,1)

        elif src_type == 'Line':
            current = np.array(kwargs['current'], dtype=float)
            tile_params['current'] = (current,1)
            pos_start = np.array(kwargs['segment_start'], dtype=float)
            tile_params['segment_start'] = (pos_start,2)
            pos_end = np.array(kwargs['segment_end'], dtype=float)
            tile_params['segment_end'] = (pos_end,2)

    except KeyError as kerr:
        msg = f'Missing input keys: {str(kerr)}'
        raise MagpylibBadUserInput(msg) from kerr

    # auto tile 1D parameters ---------------------------------------

    # evaluation vector length
    ns = [len(val) for val,tdim in tile_params.values() if val.ndim == tdim]
    if len(set(ns)) > 1:
        msg = f'getBHv() bad array input lengths: {str(set(ns))}'
        raise MagpylibBadUserInput(msg)
    n = max(ns, default=1)

    # tile 1D inputs and replace original values in kwargs
    for key,(val,tdim) in tile_params.items():
        if val.ndim<tdim:
            if tdim == 2:
                kwargs[key] = np.tile(val,(n,1))
            elif tdim == 1:
                kwargs[key] = np.array([val]*n)
        else:
            kwargs[key] = val

    # change rot to Rotation object
    kwargs['orientation'] = R.from_quat(kwargs['orientation'])

    # compute and return B
    B = getBH_level1(**kwargs)

    if squeeze:
        return np.squeeze(B)
    return B


# ON INTERFACE
def getBv(**kwargs):
    """
    B-Field computation in units of [mT] from a dictionary of input vectors.

    This function avoids the object-oriented Magpylib interface and gives direct
    access to the field implementations. It is the fastet way to compute fields
    with Magpylib.

    Inputs will automatically be tiled to shape (N,x) to fit with other inputs.

    Required inputs depend on chosen src_type!

    Parameters
    ----------
    source_type: string
        Source type for computation. Must be either 'Box', 'Cylinder', 'Sphere', 'Dipole',
        'Circular' or 'Line'. Expected input parameters depend on source_type.

    position: array_like, shape (3,) or (N,3), default=(0,0,0)
        Source positions in units of [mm].

    orientation: scipy Rotation object, default=unit rotation
        Source rotations relative to the initial state (see object docstrings).

    observer: array_like, shape (3,) or (N,3)
        Observer positions in units of [mm].

    squeeze: bool, default=True
        If True, the output is squeezed, i.e. all axes of length 1 in the output are eliminated.

    magnetization: array_like, shape (3,) or (N,3)
        Only `source_type in ('Box', 'Cylinder', 'Sphere')`! Magnetization vector (mu0*M) or
        remanence field of homogeneous magnet magnetization in units of [mT].

    moment:  array_like, shape (3,) or (N,3)
        Only `source_type = 'Moment'`! Magnetic dipole moment in units of [mT*mm^3]. For
        homogeneous magnets the relation is moment = magnetization*volume.

    current: array_like, shape (N,)
        Only `source_type in ('Line', 'Circular')`! Current flowing in loop in units of [A].

    dimension: array_like
        Only `source_type in ('Box', 'Cylinder')`! Magnet dimension input in units of [mm].

    diameter: array_like, shape (N)
        Only `source_type in (Sphere, Circular)`! Diameter of source in units of [mm].

    segment_start: array_like, shape (N,3)
        Only `source_type = 'Line'`! Start positions of line current segments in units of [mm].

    segment_end: array_like, shape (N,3)
        Only `source_type = 'Line'`! End positions of line current segments in units of [mm].

    Returns
    -------
    B-field: ndarray, shape (N,3)
        B-field generated by sources at observer positions in units of [mT].
    """
    return getBHv_level2(bh=True, **kwargs)


# ON INTERFACE
def getHv(**kwargs):
    """
    H-Field computation in units of [kA/m] from a dictionary of input vectors.

    This function avoids the object-oriented Magpylib interface and gives direct
    access to the field implementations. It is the fastet way to compute fields
    with Magpylib.

    Inputs will automatically be tiled to shape (N,x) to fit with other inputs.

    Required inputs depend on chosen src_type!

    Parameters
    ----------
    source_type: string
        Source type for computation. Must be either 'Box', 'Cylinder', 'Sphere', 'Dipole',
        'Circular' or 'Line'. Expected input parameters depend on source_type.

    position: array_like, shape (3,) or (N,3), default=(0,0,0)
        Source positions in units of [mm].

    orientation: scipy Rotation object, default=unit rotation
        Source rotations relative to the initial state (see object docstrings).

    observer: array_like, shape (3,) or (N,3)
        Observer positions in units of [mm].

    squeeze: bool, default=True
        If True, the output is squeezed, i.e. all axes of length 1 in the output are eliminated.

    magnetization: array_like, shape (3,) or (N,3)
        Only `source_type in ('Box', 'Cylinder', 'Sphere')`! Magnetization vector (mu0*M) or
        remanence field of homogeneous magnet magnetization in units of [mT].

    moment:  array_like, shape (3,) or (N,3)
        Only `source_type = 'Moment'`! Magnetic dipole moment in units of [mT*mm^3]. For
        homogeneous magnets the relation is moment = magnetization*volume.

    current: array_like, shape (N,)
        Only `source_type in ('Line', 'Circular')`! Current flowing in loop in units of [A].

    dimension: array_like
        Only `source_type in ('Box', 'Cylinder')`! Magnet dimension input in units of [mm].

    diameter: array_like, shape (N)
        Only `source_type in (Sphere, Circular)`! Diameter of source in units of [mm].

    segment_start: array_like, shape (N,3)
        Only `source_type = 'Line'`! Start positions of line current segments in units of [mm].

    segment_end: array_like, shape (N,3)
        Only `source_type = 'Line'`! End positions of line current segments in units of [mm].

    Returns
    -------
    H-field: ndarray, shape (N,3)
        H-field generated by sources at observer positions in units of [kA/m].
    """
    return getBHv_level2(bh=False, **kwargs)
