import numpy as np
import flopy


# setting variables
nrow = 200 # num of rows
ncol = 300 # num of cols
c = 240 # location of wwf in cols
nlay = 2 # num of layers
Lx = 3000 # total length of x (m)
Ly = 2000 # total lengtth of y (m)
z = 1090 # max height of first layer

# calculating the change in x and y per column/row
delr = np.ones((ncol,)) * (Lx / ncol)
delc = np.ones((nrow,)) * (Ly / nrow)

# set slope of first layer
slope = np.linspace(0, z, ncol, dtype = int)

# set initial bottom of oil layer
oil_bot = np.ones((nrow, ncol), dtype = int)*-1200
# claculate slope of rhs of bottom of oil layer
oil_slope = np.linspace(0, 1300, c-140, dtype = int)
# apply slope and constants to correct parts of oil bottom
oil_bot[:, 140:c] -= oil_slope
oil_bot[:, c:] -= 1300

# array of elevation of top layer
top = np.ones((nrow, ncol), dtype = int) * slope
# array of arrays of bottom elevation for each layer
botm = np.array([np.ones((nrow, ncol), dtype = int)*-600, oil_bot])

# starting head
h1 = top[0,0]+900-350
print("h1", h1)

# sim obj
sim = flopy.mf6.MFSimulation(
    sim_name="hough", exe_name="binary/mf6", version="mf6", sim_ws="."
)

# time obj - setting time to 100 days, 200 time periods
tdis = flopy.mf6.ModflowTdis(
    sim, pname="tdis", time_units="days", nper=1, perioddata=[(100, 200, 1.0)]
)

# ground water flow obj
gwf = flopy.mf6.ModflowGwf(sim, modelname="hough", model_nam_file="hough.nam")

# Create the Flopy iterative model solver (ims) Package object
ims = flopy.mf6.modflow.mfims.ModflowIms(sim, pname="ims", complexity="SIMPLE")

#discretization - setting variables from above
dis = flopy.mf6.modflow.mfgwfdis.ModflowGwfdis(gwf, 
    pname="dis",
    nlay=nlay,
    nrow=nrow, 
    ncol=ncol, 
    delr=delr,
    delc=delc, 
    top=top, 
    botm=botm)


# Create the initial conditions package
start = h1 * np.ones((nlay, nrow, ncol)) # all cells start with head h1
ic = flopy.mf6.modflow.mfgwfic.ModflowGwfic(gwf, 
    pname="ic", 
    strt=start)

# set hydraulic conductivity to 0.2
k = np.ones((nlay, nrow, ncol))*0.2
# in cells with vertical no flow boundary, set conductivity very low
k[0,:,240:256] = 0.000001

# Create the node property flow package - vertical conductivity is 0.1 of horizontal
npf = flopy.mf6.modflow.mfgwfnpf.ModflowGwfnpf(
    gwf, 
    pname="npf", 
    icelltype=1, 
    k=k, 
    k22 = 0.1, 
    k22overk=True,
    save_flows=True
)

# set all edges to have a constant head of h1
chd_rec = []        
for layer in range(nlay):
    for row in range(nrow):
        chd_rec.append(((layer, row, 0), h1))
        chd_rec.append(((layer, row, ncol-1), h1))
    for col in range(ncol):
        if col != 0 and col != ncol-1:
            chd_rec.append(((layer, 0, col), h1))
            chd_rec.append(((layer, nrow-1, col), h1))
# constant head obj
chd = flopy.mf6.modflow.mfgwfchd.ModflowGwfchd(
    gwf,
    pname="chd",
    maxbound=len(chd_rec),
    stress_period_data=chd_rec,
    save_flows=True,
)

# Create the output control package - saving head
oc = flopy.mf6.modflow.mfgwfoc.ModflowGwfoc(
    gwf,
    pname="oc",
    saverecord=[("HEAD", "ALL"), ("BUDGET", "ALL")],
    head_filerecord=["hough.hds"],
    budget_filerecord=["hough.cbb"],
)

# create array of horizontal flow boundaries
hfb_data = []
for x in range(nrow-1):
    for y in range(240,255):
        # set no flow boundary in layer 1 from cols 240 to 255 (replicating diagonal boundary)
        hfb_data.append([(1, x, y), (1, x+1, y), 0.000001])
    for y in range(255,ncol):
        # no flow in upper layer from col 255 on
        hfb_data.append([(0, x, y), (0, x+1, y), 0.000001])
    # no flow on left edge for both layers
    hfb_data.append([(0, x, 0), (0, x+1, 0), 0.000001])
    hfb_data.append([(1, x, 0), (1, x+1, 0), 0.000001])
    # no flow from splay fault
    hfb_data.append([(0, x, 190), (0, x+1, 190), 0.000001])
    hfb_data.append([(1, x, 190), (1, x+1, 190), 0.000001])

# horizontal flow boundary obj
hfb = flopy.mf6.modflow.ModflowGwfhfb(
    gwf,
    pname="hfb",
    maxhfb=len(hfb_data),
    stress_period_data= hfb_data
)


# data = np.genfromtxt('welldata.csv', delimiter=",")1
# data[0,0] = 1
# data = data.astype(int).tolist()
# data = {0: data}

# data for well, where q is -1000/day (in SI)
well_data = {0: [1, int(nrow/2), int(0.8/2.4*ncol), -1000]}

# well obj
wel = flopy.mf6.ModflowGwfwel(
    gwf,
    pname="wel",
    print_input=True,
    print_flows=True,
    stress_period_data=well_data,
    boundnames=True,
    save_flows=True,
)


# Write the datasets
sim.write_simulation()
success, mfoutput = sim.run_simulation()
if not success:
        raise Exception("MODFLOW did not terminate normally.")


# # h = gwf.output.head().get_data(kstpkper=(0, 0))
# # x = np.linspace(0, 1000*170, 170)
# # y = np.linspace(0, 1000*240, 240)
# # vmin, vmax = 800, 1400
# # contour_intervals = np.arange(800, 1401, 1.0)

# # fig = plt.figure(figsize=(6, 6))
# # ax = fig.add_subplot(1, 1, 1, aspect="equal")
# # c = ax.contour(x, y, h[0], contour_intervals, colors="black")
# # plt.clabel(c, fmt="%2.1f")

# # plt.show()
    

