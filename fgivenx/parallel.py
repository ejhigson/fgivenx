import tqdm
from joblib import Parallel, delayed, cpu_count


def parallel_apply(f, array, **kwargs):
    """ Apply a function to an array with openmp parallelisation.

    Equivalent to [f(x) for x in array], but parallelised if required.

    Parameters
    ----------
    f: function
        Univariate function to apply to each element of array

    array: array-like
        Array to apply f to

    Keywords
    --------
    parallel: int or bool
        int > 0: number of processes to parallelise over
        int < 0 or bool=True: use OMP_NUM_THREADS to choose parallelisation
        bool=False or int=0: do not parallelise

    precurry: tuple
        immutable arguments to pass to f before x,
        i.e. [f(precurry,x) for x in array]

    postcurry: tuple
        immutable arguments to pass to f after x
        i.e. [f(x,postcurry) for x in array]

    Returns
    -------
    [f(precurry,x,postcurry) for x in array] parallelised according to parallel
    """

    precurry = tuple(kwargs.pop('precurry', ()))
    postcurry = tuple(kwargs.pop('postcurry', ()))
    parallel = kwargs.pop('parallel', False)
    if kwargs:
        raise TypeError('Unexpected **kwargs: %r' % kwargs)

    if not parallel:
        return [f(*(precurry + (x,) + postcurry)) for x in tqdm.tqdm(array)]
    elif parallel is True:
        nprocs = cpu_count()
    elif isinstance(parallel, int):
        if parallel < 0:
            nprocs = cpu_count()
        else:
            nprocs = parallel
    else:
        raise ValueError("parallel keyword must be an integer or bool")

    return Parallel(n_jobs=nprocs)(delayed(f)(*(precurry + (x,) + postcurry))
                                   for x in tqdm.tqdm(array))
