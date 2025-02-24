import warnings

import numpy as np


class SinkhornKnopp:
    """
    Sinkhorn Knopp Algorithm

    Takes a non-negative square matrix P, where P =/= 0
    and iterates through Sinkhorn Knopp's algorithm
    to convert P to a doubly stochastic matrix.
    Guaranteed convergence if P has total support.

    For reference see original paper:
        http://msp.org/pjm/1967/21-2/pjm-v21-n2-p14-s.pdf

    Parameters
    ----------
    max_iter : int, default=1000
        The maximum number of iterations.

    epsilon : float, default=1e-3
        Metric used to compute the stopping condition,
        which occurs if all the row and column sums are
        within epsilon of 1. This should be a very small value.
        Epsilon must be between 0 and 1.

    Attributes
    ----------
    _max_iter : int, default=1000
        User defined parameter. See above.

    _epsilon : float, default=1e-3
        User defined paramter. See above.

    _stopping_condition: string
        Either "max_iter", "epsilon", or None, which is a
        description of why the algorithm stopped iterating.

    _iterations : int
        The number of iterations elapsed during the algorithm's
        run-time.

    _D1 : 2d-array
        Diagonal matrix obtained after a stopping condition was met
        so that _D1.dot(P).dot(_D2) is close to doubly stochastic.

    _D2 : 2d-array
        Diagonal matrix obtained after a stopping condition was met
        so that _D1.dot(P).dot(_D2) is close to doubly stochastic.

    Example
    -------

    .. code-block:: python
        >>> import numpy as np
        >>> from sinkhorn_knopp import sinkhorn_knopp as skp
        >>> sk = skp.SinkhornKnopp()
        >>> P = [[.011, .15], [1.71, .1]]
        >>> P_ds = sk.fit(P)
        >>> P_ds
        array([[ 0.06102561,  0.93897439],
           [ 0.93809928,  0.06190072]])
        >>> np.sum(P_ds, axis=0)
        array([ 0.99912489,  1.00087511])
        >>> np.sum(P_ds, axis=1)
        array([ 1.,  1.])

    """

    def __init__(self, max_iter=1000, epsilon=1e-3):
        assert isinstance(max_iter, int) or isinstance(max_iter, float),\
            "max_iter is not of type int or float: %r" % max_iter
        assert max_iter > 0,\
            "max_iter must be greater than 0: %r" % max_iter
        self._max_iter = int(max_iter)

        assert isinstance(epsilon, int) or isinstance(epsilon, float),\
            "epsilon is not of type float or int: %r" % epsilon
        assert epsilon > 0 and epsilon < 1,\
            "epsilon must be between 0 and 1 exclusive: %r" % epsilon
        self._epsilon = epsilon

        self._stopping_condition = None
        self._iterations = 0
        self._D1 = np.ones(1)
        self._D2 = np.ones(1)

    def fit(self, P):
        """Fit the diagonal matrices in Sinkhorn Knopp's algorithm

        Parameters
        ----------
        P : 2d array-like
        Must be a square non-negative 2d array-like object, that
        is convertible to a numpy array. The matrix must not be
        equal to 0 and it must have total support for the algorithm
        to converge.

        Returns
        -------
        A double stochastic matrix.

        """
        P = np.asarray(P)
        assert np.all(P >= 0)
        assert P.ndim == 2
        assert P.shape[0] == P.shape[1]
        self.has_support(P) #print warnings about total support

        N = P.shape[0]
        max_thresh = 1 + self._epsilon
        min_thresh = 1 - self._epsilon

        # Initialize r and c, the diagonals of D1 and D2
        r = np.ones((N, 1))
        pdotr = P.T.dot(r)

        c = 1 / pdotr
        pdotc = P.dot(c)

        r = 1 / pdotc
        del pdotr, pdotc

        P_eps = np.copy(P)
        while np.any(np.sum(P_eps, axis=1) < min_thresh) \
                or np.any(np.sum(P_eps, axis=1) > max_thresh) \
                or np.any(np.sum(P_eps, axis=0) < min_thresh) \
                or np.any(np.sum(P_eps, axis=0) > max_thresh):

            c = 1 / P.T.dot(r)
            r = 1 / P.dot(c)

            self._D1 = np.diag(np.squeeze(r))
            self._D2 = np.diag(np.squeeze(c))
            P_eps = self._D1.dot(P).dot(self._D2)

            self._iterations += 1

            if self._iterations >= self._max_iter:
                self._stopping_condition = "max_iter"
                break

        if not self._stopping_condition:
            self._stopping_condition = "epsilon"

        self._D1 = np.diag(np.squeeze(r))
        self._D2 = np.diag(np.squeeze(c))
        P_eps = self._D1.dot(P).dot(self._D2)

        return P_eps

    def has_support(self, P):
        """
            A non-negative square is said to have total
            support if A =/= 0 and if every positive element of A
            lies on a positive diagonal. A diagonal of a matrix
            is defined, for any permutation of sigma = {1,...,N},
            as a[1,sigma(1)], ..., a[N,sigma(N)], where a[i, j]
            is an element of A at the ith row and jth column.
        """
        #no support: some row is all zero
        r = np.ones((P.shape[0], 1))
        pdotr = P.T.dot(r)
        if not np.all(pdotr != 0):
            warnings.warn(
                "Matrix doesn't have total support: some col is 0", 
                 UserWarning
            )
            return False
        #no support: some col is all zero
        r = np.ones((P.shape[0], 1))
        pdotr = P.dot(r)
        if not np.all(pdotr != 0):
            warnings.warn(
                "Matrix doesn't have total support: some row is 0", 
                 UserWarning
            )
            return False

        #no support: two rows have 0s everywhere except in the same 
        #spot as one another, meaning we can't permute to a diagonal
        mask = np.ma.masked_where(P != 0, P).mask
        row_singles = np.where(np.sum(mask, axis=1) == 1)
        sliced_mask = mask[row_singles]
        cols = np.where(sliced_mask == True)[1]
        s = np.sort(cols, axis=None) #https://stackoverflow.com/q/11528078
        duplicates = s[:-1][s[1:] == s[:-1]]
        if len(duplicates) != 0:
            warnings.warn(
                "Matrix doesn't have total support: two rows are nonzero in only one shared col", 
                 UserWarning
            )
            return False 
        #no support: two rows have 0s everywhere except in the same 
        #spot as one another, meaning we can't permute to a diagonal
        mask = np.ma.masked_where(P.T != 0, P.T).mask
        row_singles = np.where(np.sum(mask, axis=1) == 1)
        sliced_mask = mask[row_singles]
        cols = np.where(sliced_mask == True)[1]
        s = np.sort(cols, axis=None) #https://stackoverflow.com/q/11528078
        duplicates = s[:-1][s[1:] == s[:-1]]
        if len(duplicates) != 0:
            warnings.warn(
                "Matrix doesn't have total support: two cols are nonzero in only one shared row", 
                 UserWarning
            )
            return False

        return True

 
