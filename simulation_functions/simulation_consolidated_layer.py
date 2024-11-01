import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt

# Load data from 'co.mat' (assuming co.mat has variables structured for Python compatibility)
# import scipy.io
# co = scipy.io.loadmat('co.mat')

# Initialize variables
Hw = []
Tw = []
Nw = []
Mw = []

H = []
D = []
Tr = []
Trc = []
Hi = []
Hc = []

load_calc = 0

growth_curve = 1
years = 100
a = 0.7
peak_time = stats.norm(0.82, 0.06)
season_start = stats.norm(0.0, 0.01)
season_end = stats.norm(0.0, 0.03)

h2m = stats.norm(1, 0.0471)
m2n = stats.weibull_min(1.146, scale=1.991)

### Parameters of the structure
# Molikpaq configuration
water_depth = 20
hmu = 1.8
h_peak = stats.norm(hmu, hmu / 9)
wn = 40
w = 100 # width of the structure

# Ice thickness simulation
for nn in range(years):
    print(f'hmu = {hmu:.1f}  || LI -  {nn + 1}')
    
    # Sampling values
    tp = peak_time.rvs()
    hp = h_peak.rvs()
    ss = season_start.rvs()
    se = season_end.rvs()
    
    # Time vector (weeks)
    t = np.linspace(1 / wn, 1, wn)

    # normalized LI thickness
    if growth_curve == 1:
        h_n = (t / tp) ** a
    else:
        h_n = (t / tp) ** (1 - (t / tp))

    h_n[t > tp] = 1 / (1 - tp) - 1 / (1 - tp) * t[t > tp] # normalized LI thickness melt season
    h = h_n * hp # real LI thickness (multiplied by the maximum annual LI thickness)
    h = h + 0.2 * np.random.randn(len(h)) # week to week randomization of LI growth
    h = h.reshape(-1, 1)
    
    t = t + ss # shifting the whole time vector to simulate random season start
    t = t + t * se # shifting the wohle time vector to simulate random season end
    t = np.abs(t).reshape(-1, 1) # randomizing week time (just gives a nicer looking plot - more natural and resembles more the results from JP1)

    m = 6.03 + 0.51 * h # making weekly mean ridge keel draft according to the linear correlation
    m = m * h2m.rvs(size=m.shape) # introducing the variablitly
    n = 37.21 * (m - 5) ** 2.16 # making weekly number of ridges according to the power function correlation
    n = n * m2n.rvs(size=n.shape) # introducing the variablitly
    
    # creating ridges
    d = np.empty(int(np.sum(n) * 1.1))
    tr = np.empty(int(np.sum(n) * 1.1))
    hi = np.empty(int(np.sum(n) * 1.1))
    iii = 0
    
    for i in range(len(m)):
        dw = 5 + np.random.exponential(m[i] - 5, int(n[i]))
        d[iii:iii + len(dw)] = dw
        tr[iii:iii + len(dw)] = t[i] + 1 / wn * np.random.rand(len(dw))
        hi[iii:iii + len(dw)] = h[i]
        iii += len(dw)
    
    d = d[~np.isnan(d)]
    tr = tr[~np.isnan(tr)]
    hi = hi[~np.isnan(hi)]

    # Consolidated layer simulation
    trV = np.outer(tr, np.linspace(0, 1, 101))
    hV = (trV / tp ** a) * hp
    mV = 6.03 + 0.51 * hV
    dV = np.outer(d, np.ones(101))
    
    pV = 1 / (mV - 5) * np.exp(-1 / (mV - 5) * dV)
    FV = np.cumsum(pV, axis=1)
    FVn = FV / FV[:, -1][:, np.newaxis]
    
    R = np.random.rand(len(FVn))
    RV = np.tile(R, (101, 1)).T
    mi = np.abs(FVn - RV).argmin(axis=1)
    
    idx = (np.arange(len(mi)), mi)
    trc = trV[idx]

    if growth_curve == 1:
        hc = (tr - trc) / tp ** a * hp * 2
    else:
        hc = ((tr - trc) / tp) ** (1 - ((tr - trc) / tp)) * 2 * hp

    if np.any(hc < 0):
        break

    # Store yearly results
    Tw.append(t)
    Hw.append(h)
    Nw.append(n)
    Mw.append(m)

    # H.extend(hi)
    D.extend(d)
    Tr.extend(tr)
    Trc.extend(trc)
    Hi.extend(hi)
    Hc.extend(hc)

# Convert to arrays for further processing and visualization
Tw = np.array(Tw).flatten()
Hw = np.array(Hw).flatten()

# convert to arrays for further processing and visualization
D = np.array(D)
Tr = np.array(Tr)
Trc = np.array(Trc)
Hi = np.array(Hi)
Hc = np.array(Hc)

Ra = Tr - Trc
R = Hc / Hi



##### load calculation

# Parameters
years = 10  # Replace with the actual value
hmu = 0.1  # Replace with the actual value

# Define distributions equivalent to makedist
pdCr = stats.weibull_min(1.234, scale=0.245)  # Weibull distribution
pdfi = stats.uniform(20, 20)  # Uniform distribution from 20 to 40 (width 20)
pde = stats.uniform(0.2, 0.2)  # Uniform distribution from 0.2 to 0.4 (width 0.2)
pdc = stats.uniform(5000, 2000)  # Uniform distribution from 5000 to 7000 (width 2000)

# Initialize lists
FCa = []
FCam = []
FKa = []
FKam = []
Fa = []
Fam = []
CRam = []


for i in range(years):
    print(f'hmu = {hmu:.1f}  || Force simulation -  {i + 1}')
    
    # Size of Hc[i]
    if np.shape(Hc[i]) == () and not Hc[i] is None:
        cs = 1
    else:
        cs = Hc[i].shape
    
    # Initializing array `n`
    n = -0.3 * np.ones(cs)
    mask = Hc[i] < 1
    n[mask] = -0.5 + Hc[i][mask] / 5
    
    # Calculating `pg`
    pg = pdCr.rvs(size=cs) * Hc[i]**-0.16 * (w / Hc[i])**n
    
    # Calculate FC
    FC = pg * w * Hc[i]
    FC[D[i] > 16] = 0
    FCa.extend(FC.flatten())
    FCam.append(np.max(FC))
    
    # Generate random samples for other parameters
    e = pde.rvs(size=cs)
    fi = pdfi.rvs(size=cs)
    c = pdc.rvs(size=cs)
    
    mi = np.tan(np.radians(45 + fi / 2))
    gamma = (1 - e) * (1024 - 910) * 9.81
    
    # Calculate FK
    FK = mi * D[i] * w * (D[i] * mi * gamma / 2 + 2 * c) * (1 + D[i] / (6 * w)) / 1E6
    FK[D[i] > 16] = 0
    FKa.extend(FK.flatten())
    FKam.append(np.max(FK))
    
    # Total force F
    F = FK + FC
    Fa.extend(F.flatten())
    Fam.append(np.max(F))
    
    # cr test
    Cr = pdCr.rvs(size=cs)
    CRam.append(np.max(Cr))



# Plotting 
# Create the first figure
plt.figure(figsize=(6, 8))  # Adjust size as needed for clarity

# Subplot 1
plt.subplot(6, 1, 1)
plt.box(True)
plt.grid(True)
plt.xlabel('R = h_c / h_i []')
plt.ylabel('Probability density []')
plt.hist(R, bins=np.arange(0, 5.1, 0.1), density=True)
plt.title(f'R_mean = {np.mean(R[R < 2]):.2f}')

# Subplot 2
plt.subplot(6, 1, 2)
plt.box(True)
plt.grid(True)
plt.xlabel('Ice thickness [m]')
plt.ylabel('Probability density [m^-1]')
plt.hist(Hi, bins=np.arange(0, 5.05, 0.05), density=True, alpha=0.5, label='Level ice')
plt.hist(Hc, bins=np.arange(0, 5.05, 0.05), density=True, alpha=0.5, label='Consolidated layer')
plt.legend()

plt.tight_layout()  # Adjust layout to prevent overlap

plt.subplot(6, 1, 3)
plt.scatter(Tw, Hw, marker='.')
plt.xlabel('Tw')
plt.ylabel('Hw')
plt.grid(True)




# Assume Fam and CRam are already defined arrays

# Fit the generalized extreme value (GEV) distribution to the data (Fam)
shape, loc, scale = stats.genextreme.fit(Fam)

# Plot exceedance probability for Fam
x = np.linspace(40, 200, 100)  # Range for x-axis

# Compute the cumulative distribution function (CDF) for Fam
Y = stats.genextreme.cdf(Fam, shape, loc=loc, scale=scale)

# Sort Fam and corresponding CDF for plotting
Fam_sorted = np.sort(Fam)
Y_sorted = Y[np.argsort(Fam)]

plt.subplot(6, 1, 4)
plt.plot(Fam_sorted, 1 - Y_sorted, label='Exceedance Probability Curve')
plt.xlabel('Force [MN]')
plt.ylabel('Exceedance probability [MN^{-1}]')
plt.title('Exceedance Probability for Fam')
plt.grid(True)
plt.box(True)

# Plot probability plot for Fam (equivalent to epp in MATLAB)
plt.subplot(6, 1, 5)
stats.probplot(Fam, dist=stats.genextreme(shape, loc=loc, scale=scale), plot=plt)
plt.title('Probability Plot for Fam')
plt.grid(True)

# Plot probability plot for CRam
plt.subplot(6, 1, 6)
stats.probplot(CRam, dist='norm', plot=plt)  # Default distribution is normal; adjust as needed
plt.title('Probability Plot for CRam')
plt.grid(True)

plt.show()
