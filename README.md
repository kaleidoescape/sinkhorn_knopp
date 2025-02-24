sinkhorn_knopp
--------

Convert non-negative square matrices with total support into doubly stochastic matrices. 

Note: This fork differs in that it makes a few extra checks for total support that were missing in the original to inform the user of likely problems.

```python
    >> import numpy as np
    >> from sinkhorn_knopp import sinkhorn_knopp as skp
    >> sk = skp.SinkhornKnopp()
    >> P = [[.011, .15], [1.71, .1]]
    >> P_ds = sk.fit(P)
    >> print P_ds
        [[ 0.06102561  0.93897439]
        [ 0.93809928  0.06190072]]
    >> print np.sum(P_ds, axis=0)
        [ 0.99912489  1.00087511]
    >> print np.sum(P_ds, axis=1)
        [ 1.,  1.]
```

See http://msp.org/pjm/1967/21-2/pjm-v21-n2-p14-s.pdf for reference.

## Install

```sh
git clone https://github.com/kaleidoescape/sinkhorn_knopp
cd sinkhorn_knopp
pip install -e .
```

## Uninstall

```sh
pip uninstall sinkhorn_knopp
```
