import numpy as np
import scipy.stats as stats
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import os

### import_module.py is a helper function to import modules from different directories, it is located in the base directory
# Get the current working directory
cwd = os.getcwd()
# Construct the path to the base directory
base_dir = os.path.join(cwd, '..')
# Add the base directory to sys.path
sys.path.insert(0, base_dir)
from import_module import import_module
### imports using the helper function import_module
myColor = import_module('myColor', 'helper_functions')
# Load data from 'co.mat' (assuming co.mat has variables structured for Python compatibility)
# import scipy.io
# co = scipy.io.loadmat('co.mat')

def consolidated_layer_simulation(w, water_depth=20, hmu=1.8, wn=40, years=1000):

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
    # years = 1000
    a = 0.7
    peak_time = stats.norm(0.82, 0.06)
    season_start = stats.norm(0.0, 0.01)
    season_end = stats.norm(0.0, 0.03)

    h2m = stats.norm(1, 0.0471)
    m2n = stats.weibull_min(1.146, scale=1.991)

    ### Parameters of the structure
    # Molikpaq configuration
    # water_depth = 20
    # hmu = 1.8
    h_peak = stats.norm(hmu, hmu / 9)
    wn = int(40 * hmu/2)
    # w = 100 # width of the structure

    # Ice thickness simulation
    for nn in range(years):
        if nn % 100 == 0:
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
        h = h + 0.2 * np.random.rand(len(h)) # week to week randomization of LI growth
        h = h.reshape(-1, 1)
        
        t = t + ss # shifting the whole time vector to simulate random season start
        t = t + t * se # shifting the wohle time vector to simulate random season end
        t = np.abs(t).reshape(-1, 1) # randomizing week time (just gives a nicer looking plot - more natural and resembles more the results from JP1)

        m_fix = 6.03 + 0.51 * h # making weekly mean ridge keel draft according to the linear correlation
        m = m_fix * h2m.rvs(size=m_fix.shape) # introducing the variablitly
        while np.any(m < 5):
            print('Error: Mean ridge keel draft below 5 m, but 5m is the threshold for a ridge in general')
            print('Trying again...')
            m = m_fix * h2m.rvs(size=m_fix.shape) # just try again, this happens only rarely
        # if np.any(m < 5):
        #     print('Error: Mean ridge keel draft below 5 m, but 5m is the threshold for a ridge in general')
        #     print(f"m_fix, m, h: {np.concatenate((m_fix, m, h), axis=1)}")
        #     # print(f"m: {m}")
        #     # print(f"h: {h}")
        #     input('Press Enter to continue...')
        n = 37.21 * (m - 5) ** 2.16 # making weekly number of ridges according to the power function correlation
        n = n * m2n.rvs(size=n.shape) # introducing the variablitly
        
        # creating ridges
        # initialize nan arrays
        d = np.empty(int(np.sum(n) * 1.1))
        d[:] = np.nan
        tr = np.empty(int(np.sum(n) * 1.1))
        tr[:] = np.nan
        hi = np.empty(int(np.sum(n) * 1.1))
        hi[:] = np.nan
        iii = 0
        
        for i in range(len(m)):
            dw = 5 + np.random.exponential(m[i] - 5, int(n[i]))
            d[iii:iii + len(dw)] = dw
            tr[iii:iii + len(dw)] = t[i] + 1 / wn * np.random.rand(len(dw))
            hi[iii:iii + len(dw)] = h[i]
            iii += len(dw)
        
        indices_to_keep = np.intersect1d(np.where(~np.isnan(d)), np.where(~np.isnan(tr)), np.where(~np.isnan(hi)))
        d = d[indices_to_keep]
        tr = tr[indices_to_keep]
        hi = hi[indices_to_keep]

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
            if np.abs(np.round(min(hc), 5)) == 0:
                # it's a numerical error, just make it to zero
                minimum_position = np.where(hc < 0)
                hc[minimum_position] = 0
            else:
                print('Error: Negative consolidated layer thickness')
                break

        # Store yearly results
        Tw.append(t) # normalized time (weekly data points)
        Hw.append(h) # LI thickness (weekly data points)
        Nw.append(n)
        Mw.append(m)

        # H.extend(hi)
        D.append(d)
        Tr.append(tr)
        Trc.append(trc)
        Hi.append(hi)
        Hc.append(hc)

    # Convert to arrays for further processing and visualization
    Tw = np.array(Tw).flatten()
    Hw = np.array(Hw).flatten()

    # convert to arrays for further processing and visualization
    D = np.concatenate(D)
    Tr = np.concatenate(Tr)
    Trc = np.concatenate(Trc)
    Hi = np.concatenate(Hi)
    Hc_vec = np.concatenate(Hc)

    Ra = Tr - Trc
    R = Hc_vec / Hi

    if np.any(np.isnan(R)):
        print('Error: NaN values in R')
        print(f"R: {R}")
        print(f"Hi: {Hi}")
        print(f"Hc_vec: {Hc_vec}")
        input('Press Enter to continue...')



    ##### load calculation

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
        if i % 100 == 0:
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
        FCam.append(np.nanmax(FC))
        
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
        FKam.append(np.nanmax(FK))
        
        # Total force F
        F = FK + FC
        Fa.extend(F.flatten())
        Fam.append(np.nanmax(F))
        
        # cr test
        Cr = pdCr.rvs(size=cs)
        CRam.append(np.nanmax(Cr))

    # Assume Fam and CRam are already defined arrays

    # remove all inf values, that are in Fam (I don't know why they are there)
    Fam = np.array(Fam)
    Fam = Fam[~np.isinf(Fam)]

    # Fit the generalized extreme value (GEV) distribution to the data (Fam)
    shape, loc, scale = stats.genextreme.fit(Fam)

    # Plot exceedance probability for Fam
    x = np.linspace(40, 200, 100)  # Range for x-axis

    # Compute the cumulative distribution function (CDF) for Fam
    Y = stats.genextreme.cdf(Fam, shape, loc=loc, scale=scale)

    # Sort Fam and corresponding CDF for plotting
    Fam_sorted = np.sort(Fam)
    Y_sorted = Y[np.argsort(Fam)]


    return R, Hi, Hc_vec, Tw, Hw, Fam, Fam_sorted, Y_sorted, CRam, shape, loc, scale 



def consolidated_layer_plot(R, Hi, Hc_vec, Tw, Hw, Fam, Fam_sorted, Y_sorted, CRam, shape, loc, scale):
    # Create subplots
    fig = make_subplots(
        rows=2, cols=3,
        specs=[[{"colspan": 1, "rowspan":1}, {"colspan": 1, "rowspan":1}, {"colspan": 1, "rowspan":1}],
               [{"colspan": 1, "rowspan":1}, {"colspan": 1, "rowspan":1}, {"colspan": 1, "rowspan":1}]
        ],
        subplot_titles=(
            'R_mean = {:.2f}'.format(np.mean(R[R < 2])),
            'LI and consolidated layer thickness',
            'Yearly level ice thickness evolution',
            'Exceedance Probability for Fam',
            'Probability Plot for Fam',
            'Probability Plot for CRam'
        )
    )

    # Subplot 1: Histogram of R
    # Create histogram of R with color myColor['dark_blue'](0.7)

    hist_numpy = np.histogram(R, bins=np.arange(0, 5, 0.1), density=True) # bins=int((5.1 - 0) / 0.1), density=True)
    hist_heights = hist_numpy[0]
    hist_points = hist_numpy[1]
    hist_R = go.Bar(
        x=hist_points[:-1],
        y=hist_heights,
        marker=dict(color= myColor.dark_blue(0.7), opacity=0.8),
        name='Relation ridge thickness and consolidated layer thickness'
    )
    # hist_R = go.Histogram(
    #     x=R,
    #     nbinsx=int((5.1 - 0) / 0.1),
    #     histnorm='probability density',
    #     name='R',
    #     marker=dict(color=myColor['dark_blue'](0.7)),
    # )
    fig.add_trace(hist_R, row=1, col=1)
    fig.update_xaxes(title_text='R = h_c / h_i [-]', row=1, col=1)
    fig.update_yaxes(title_text='Probability density []', row=1, col=1)

    # Subplot 2: Histograms of Hi and Hc_vec
    hist_numpy = np.histogram(Hi, int((5.05 - 0) / 0.05), density=True)
    hist_heights = hist_numpy[0]
    hist_points = hist_numpy[1]
    hist_Hi = go.Bar(
        x=hist_points[:-1],
        y=hist_heights,
        marker=dict(color= myColor.dark_blue(0.7), opacity=0.5),
        name='Level ice'
    )
    # hist_Hi = go.Histogram(
    #     x=Hi,
    #     nbinsx=int((5.05 - 0) / 0.05),
    #     histnorm='probability density',
    #     name='Level ice',
    #     marker=dict(color=myColor['dark_blue'](0.7)),
    #     opacity=0.5
    # )

    hist_numpy = np.histogram(Hc_vec, bins=int((5.05 - 0) / 0.05), density=True)
    hist_heights = hist_numpy[0]
    hist_points = hist_numpy[1]
    hist_Hc_vec = go.Bar(
        x=hist_points[:-1],
        y=hist_heights,
        marker=dict(color= myColor.dark_red(0.7), opacity=0.5),
        name='Consolidated layer'
    )
    # hist_Hc_vec = go.Histogram(
    #     x=Hc_vec,
    #     nbinsx=int((5.05 - 0) / 0.05),
    #     histnorm='probability density',
    #     name='Consolidated layer',
    #     marker=dict(color=myColor['dark_red'](0.7)),
    #     opacity=0.5
    # )
    fig.add_trace(hist_Hi, row=1, col=2)
    fig.add_trace(hist_Hc_vec, row=1, col=2)
    fig.update_xaxes(title_text='Thickness [m]', row=1, col=2)
    fig.update_yaxes(title_text='Probability density [m^-1]', row=1, col=2)
    fig.update_layout(barmode='overlay')
    fig.update_layout(showlegend=True)

    # Subplot 3: Scatter plot of Tw vs Hw
    scatter_Tw_Hw = go.Scatter(
        x=Tw,
        y=Hw,
        mode='markers',
        marker=dict(symbol='circle', size=5, color=myColor['dark_blue'](0.7)),
        name='Tw vs Hw',
    )
    fig.add_trace(scatter_Tw_Hw, row=1, col=3)
    fig.update_xaxes(
        title_text='Normalized time [-]',
        tickvals=[0, 1],
        ticktext=['season start', 'season end'],
        row=1, col=3
        )
    fig.update_yaxes(title_text='Weekly mean LI thickness [m]', row=1, col=3)

    # Subplot 4: Exceedance Probability Curve
    exceedance_curve = go.Scatter(
        x=Fam_sorted,
        y=1 - Y_sorted,
        mode='lines',
        line=dict(color=myColor['dark_blue'](1)),
        name='Exceedance Probability Curve'
    )
    fig.add_trace(exceedance_curve, row=2, col=1)
    fig.update_xaxes(title_text='Force [MN]', row=2, col=1)
    fig.update_yaxes(title_text='Exceedance probability [MN^{-1}]', type='log', row=2, col=1)

    # Subplot 5: Probability Plot for Fam
    (osm, osr), (slope, intercept, r) = stats.probplot(Fam, dist=stats.genextreme, sparams=(shape, loc, scale))
    probplot_Fam = go.Scatter(
        x=osm,
        y=osr,
        mode='markers',
        marker=dict(symbol='circle', size=5, color=myColor['dark_blue'](0.7)),
        name='Probability Plot for Fam'
    )
    probplot_Fam_line = go.Scatter(
        x=osm,
        y=slope * osm + intercept,
        mode='lines',
        line=dict(color=myColor['dark_red'](1)),
        name='Fit'
    )
    fig.add_trace(probplot_Fam, row=2, col=2)
    fig.add_trace(probplot_Fam_line, row=2, col=2)
    fig.update_xaxes(title_text='Theoretical Quantiles', row=2, col=2)
    fig.update_yaxes(title_text='Ordered Values', row=2, col=2)

    # Subplot 6: Probability Plot for CRam
    (osm, osr), (slope, intercept, r) = stats.probplot(CRam, dist='norm')
    probplot_CRam = go.Scatter(
        x=osm,
        y=osr,
        mode='markers',
        marker=dict(symbol='circle', size=5, color=myColor['dark_blue'](0.7)),
        name='Probability Plot for CRam'
    )
    probplot_CRam_line = go.Scatter(
        x=osm,
        y=slope * osm + intercept,
        mode='lines',
        line=dict(color=myColor['dark_red'](1)),
        name='Fit'
    )
    fig.add_trace(probplot_CRam, row=2, col=3)
    fig.add_trace(probplot_CRam_line, row=2, col=3)
    fig.update_xaxes(title_text='Theoretical Quantiles', row=2, col=3)
    fig.update_yaxes(title_text='Ordered Values', row=2, col=3)

    # Update layout
    fig.update_layout(height=600, width=1400, title_text="Consolidated Layer Plot")
    
    return fig


# plt.show()


# # Create the first figure
# plt.figure(figsize=(6, 8))  # Adjust size as needed for clarity
# plt.ion()  # Turn on interactive mode

# # Subplot 1
# # relation between ridge thickness and consolidated layer thickness
# plt.subplot(6, 1, 1)
# plt.box(True)
# plt.grid(True)
# plt.xlabel('R = h_c / h_i []')
# plt.ylabel('Probability density []')
# plt.hist(R, bins=np.arange(0, 5.1, 0.1), density=True)
# plt.title(f'R_mean = {np.mean(R[R < 2]):.2f}')

# # Subplot 2
# plt.subplot(6, 1, 2)
# plt.box(True)
# plt.grid(True)
# plt.xlabel('Ice thickness [m]')
# plt.ylabel('Probability density [m^-1]')
# plt.hist(Hi, bins=np.arange(0, 5.05, 0.05), density=True, alpha=0.5, label='Level ice')
# plt.hist(Hc_vec, bins=np.arange(0, 5.05, 0.05), density=True, alpha=0.5, label='Consolidated layer')
# plt.legend()

# plt.tight_layout()  # Adjust layout to prevent overlap

# plt.subplot(6, 1, 3)
# plt.scatter(Tw, Hw, marker='.')
# plt.xlabel('Tw')
# plt.ylabel('Hw')
# plt.grid(True)




# # Assume Fam and CRam are already defined arrays

# # Fit the generalized extreme value (GEV) distribution to the data (Fam)
# shape, loc, scale = stats.genextreme.fit(Fam)

# # Plot exceedance probability for Fam
# x = np.linspace(40, 200, 100)  # Range for x-axis

# # Compute the cumulative distribution function (CDF) for Fam
# Y = stats.genextreme.cdf(Fam, shape, loc=loc, scale=scale)

# # Sort Fam and corresponding CDF for plotting
# Fam_sorted = np.sort(Fam)
# Y_sorted = Y[np.argsort(Fam)]

# plt.subplot(6, 1, 4)
# plt.plot(Fam_sorted, 1 - Y_sorted, label='Exceedance Probability Curve')
# # y axis logaritmic
# plt.yscale('log')
# plt.xlabel('Force [MN]')
# plt.ylabel('Exceedance probability [MN^{-1}]')
# plt.title('Exceedance Probability for Fam')
# plt.grid(True)
# plt.box(True)

# # Plot probability plot for Fam (equivalent to epp in MATLAB)
# plt.subplot(6, 1, 5)
# stats.probplot(Fam, dist=stats.genextreme(shape, loc=loc, scale=scale), plot=plt)
# plt.title('Probability Plot for Fam')
# plt.grid(True)

# # Plot probability plot for CRam
# plt.subplot(6, 1, 6)
# stats.probplot(CRam, dist='norm', plot=plt)  # Default distribution is normal; adjust as needed
# plt.title('Probability Plot for CRam')
# plt.grid(True)

# # plt.show()