from math import sin
from matplotlib.collections import LineCollection
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import flopy.utils.binaryfile as bf
from flopy.discretization import StructuredGrid, VertexGrid, UnstructuredGrid
import flopy


sim = flopy.mf6.MFSimulation.load("plots", "hough.nam", verbosity_level=0)

ml = sim.get_model("hough")

modelgrid = ml.modelgrid
hds_f = ml.output.head().get_data(kstpkper=(99,0))
hds_s = ml.output.head().get_data(kstpkper=(0,0))

col = 100
nrow = 200
ncol = 300
c = 240
nlay = 2



slope = np.linspace(0, 2400, ncol, dtype = int)
top = np.ones((nrow, ncol), dtype = int) * slope

h1 = top[0,0]+900-350

p = (hds_f-h1)*950*9.8/1e6

sl = sin(1.3)
p_crit = -sl*0.08

print("crit", p_crit)
# print(np.where(p <= p_crit))
print(p[1,100, 90:110])

hfb_data = []
# for y,x in zip(range(140,20, -1), range(60,180)):

hfb_data.append([(2400, -2500), (2400,-600)])
hfb_data.append([(2550,-600), (2550,2050)])
hfb_data.append([(1900,-2500), (1900,1500)])
for y in range(2400, 2550):
    hfb_data.append([(y,-600), (y+1,-600)])


figure, ax = plt.subplots(figsize=(8, 8))

# pmv = flopy.plot.PlotMapView(modelgrid=modelgrid)
# pc = pmv.plot_array(ml.output.head().get_data(), alpha=0.5)
xc = flopy.plot.PlotCrossSection(modelgrid=modelgrid, line={"row": col})
pc = xc.plot_array(p, alpha=0.5)

xc.plot_grid(linewidths=0.1)

plt.colorbar(pc)
ax.add_collection(LineCollection(hfb_data, linewidths = 1.5, colors="red"))
plt.title("Cross-Section of Change in Pore Pressure")

figure, axes = plt.subplots(1,1,figsize=(8, 8), squeeze=False)
axes[0,0].title.set_text("Map View of Pore Pressure")

# pmv = flopy.plot.PlotMapView(modelgrid=modelgrid)
# pc = pmv.plot_array(ml.output.head().get_data(), alpha=0.5)
xc = flopy.plot.PlotMapView(modelgrid=modelgrid, layer=1, ax=axes[0,0])
# pc1 = xc.plot_array(p, alpha=0.5, ax = axes[1,0])

# xc = flopy.plot.PlotMapView(modelgrid=modelgrid, layer=0, ax=axes[0,:0])
pc0 = xc.plot_array(modelgrid.top, alpha=0.5, ax = axes[0,0])

xc.plot_grid(linewidths=0.1, ax = axes[0,0])
# xc.plot_grid(linewidths=0.1, ax = axes[1,0])

plt.colorbar(pc0, ax=axes[0,0])
# plt.colorbar(pc1, ax=axes[1,0])
axes[0,0].add_collection(LineCollection([[(2550,0), (2550,2400)], [(1900,0), (1900,2400)]], linewidths = 1.5, colors="red"))
# axes[1,0].add_collection(LineCollection([[(2400,0), (2400,2400)], [(1900,0), (1900,2400)]], linewidths = 1.5, colors="red"))


figure, ax = plt.subplots(figsize=(8, 8))

# pmv = flopy.plot.PlotMapView(modelgrid=modelgrid)
# pc = pmv.plot_array(ml.output.head().get_data(), alpha=0.5)
xc = flopy.plot.PlotCrossSection(modelgrid=modelgrid, line={"row": col})
pc = xc.plot_array(p, alpha=0.5)

xc.plot_grid(linewidths=0.1)

plt.colorbar(pc)
ax.add_collection(LineCollection(hfb_data, linewidths = 1.5, colors="red"))
plt.title("Cross-Section of Final Head")


# HEAD FIGURES
figure, axes = plt.subplots(2,1,figsize=(8, 8), squeeze=False)
axes[0,0].title.set_text("Map View of Final Head")

pmv = flopy.plot.PlotMapView(modelgrid=modelgrid)
# pc = pmv.plot_array(ml.output.head().get_data(), alpha=0.5)
xc = flopy.plot.PlotMapView(modelgrid=modelgrid, layer=1, ax=axes[0,0])
pc1 = xc.plot_array(hds_f, alpha=0.5, ax = axes[1,0])

xc = flopy.plot.PlotMapView(modelgrid=modelgrid, layer=0, ax=axes[0,:0])
pc0 = xc.plot_array(hds_f, alpha=0.5, ax = axes[0,0])

xc.plot_grid(linewidths=0.1, ax = axes[0,0])
xc.plot_grid(linewidths=0.1, ax = axes[1,0])

plt.colorbar(pc0, ax=axes[0,0])
plt.colorbar(pc1, ax=axes[1,0])
axes[0,0].add_collection(LineCollection([[(2550,0), (2550,2400)], [(1900,0), (1900,2400)]], linewidths = 1.5, colors="red"))
axes[1,0].add_collection(LineCollection([[(2400,0), (2400,2400)], [(1900,0), (1900,2400)]], linewidths = 1.5, colors="red"))

plt.show()