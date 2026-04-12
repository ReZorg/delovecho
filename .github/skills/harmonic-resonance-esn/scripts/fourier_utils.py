import numpy as np

def phase_coherence(X):
    """Compute phase coherence of a complex spectrum."""
    if X.ndim == 1:
        X = X[:, np.newaxis]
    
    power = np.sum(np.abs(X)**2, axis=1)
    weights = power / np.sum(power)
    
    phases = np.angle(X[:, 0])
    
    C = np.abs(np.sum(weights * np.exp(1j * phases)))
    
    return C

def spectral_flatness(power_spectrum):
    """Compute spectral flatness."""
    P = power_spectrum + 1e-10
    
    geometric_mean = np.exp(np.mean(np.log(P)))
    arithmetic_mean = np.mean(P)
    
    flatness = geometric_mean / arithmetic_mean
    
    return flatness
