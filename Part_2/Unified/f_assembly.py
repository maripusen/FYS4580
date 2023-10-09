import openmc 
import matplotlib.pyplot as plt
import numpy as np
from materials_gen import urox, water,deuterium, zirc, helium, graphite, boron, lead
from regions import geometry, moderator, moderator2, water_cell, hegap, cladding, cladding2, fuel, controlrod, water, void, core, core_uni, c_cell

#Exporting a XML file wih the materials. 
materials = openmc.Materials([urox, water,deuterium, zirc, helium, graphite, boron])


#
materials.export_to_xml()
geometry.export_to_xml()




plot = openmc.Plot.from_geometry(geometry)
plot.color_by = 'material'
plot.basis = "xy"
#plot.width = [23.8, 23.8]
plot.pixels = [8640,8640]
#"""
plot.colors = {
#    moderator: 'blue',
#    moderator2: "cyan",
    water_cell: "blue",
    hegap: 'red',
    zirc: 'gray',
    fuel: 'green',
#    controlrod: 'brown',
    boron: "brown",
    water: "blue",
    void: "white",
    deuterium: "blue"
}
#"""
plot.to_ipython_image()





# OpenMC simulation parameters
settings = openmc.Settings()
settings.batches = 100
settings.inactive = 10
settings.particles = 10000


# Create an initial uniform spatial source distribution overfissionable zones
#bounds = [-11.9, -11.9, -150, 11.9, 11.9, 150]
bounds = [-23.8*3.5, -23.8*3.5, -150, 23.8*3.5, 23.8*3.5, 150]
uniform_dist = openmc.stats.Box(bounds[:3], bounds[3:],only_fissionable = True)
settings.source = openmc.IndependentSource(space=uniform_dist)

# Export to "settings.xml"
settings.export_to_xml()







#Constructing a mesh 
mesh = openmc.RegularMesh()
mesh.dimension = [200,200]
mesh.lower_left= [-23.8*3.5,-23.8*3.5]
mesh.upper_right= [23.8*3.5,23.8*3.5]



# Create mesh filter for tally
mesh_filter = openmc.MeshFilter(mesh)
#esh_filter.mesh = mesh

# Instantiate an empty Tallies object
tallies_file = openmc.Tallies()


erange = np.logspace(np.log10(10e-5), np.log10(20e6), 501)
energy_filter = openmc.EnergyFilter(erange)

# Create mesh tally to score flux and fission rate
tally = openmc.Tally(name = "Tally")
tally.filters = [mesh_filter]
tally.scores = ["flux", 'prompt-nu-fission']
tallies_file.append(tally)


tally2 = openmc.Tally(name = "Energy")
tally2.filters = [energy_filter]
tally2.scores = ["flux"]
tallies_file.append(tally2)




# Resonance Escape Probability tallies
therm_abs_rate = openmc.Tally(name='therm. abs. rate')
therm_abs_rate.scores = ['absorption']
therm_abs_rate.filters = [openmc.EnergyFilter([0.0,0.625])]
tallies_file.append(therm_abs_rate)

# Thermal Flux Utilization tallies
fuel_therm_abs_rate = openmc.Tally(name='fuel therm. abs. rate')
fuel_therm_abs_rate.scores = ['absorption']
fuel_therm_abs_rate.filters = [openmc.EnergyFilter([0.0, 0.625]),
                               openmc.CellFilter([fuel])]
tallies_file.append(fuel_therm_abs_rate)


tallies_file.export_to_xml()


if __name__ == "__main__":
    #Running the simulation
    openmc.run()
