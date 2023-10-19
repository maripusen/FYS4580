import openmc 
import openmc.deplete
import matplotlib.pyplot as plt
import numpy as np
#from materials_gen import urox, water,deuterium, zirc, helium, graphite, boron, lead
from materials_gen import urox, water,deuterium, zirc, helium, graphite, boron, lead, plutonium, metal_fuel, rodmat, deuterium_bor, ht_steel

from newgeom import geometry, fuel, fuel2, rod, retrod, radii, radiirod, moderator, moderator2, hegap, cladding, hegap2, cladding2, empty, controlrod, cgap, cclad, cwater,rrod, cgap2, cclad2, cwater2, containmentcell, waterfill

#Exporting a XML file wih the materials. 
#materials = openmc.Materials([urox, water,deuterium, zirc, helium, graphite, boron])
volume0 = (2 * np.pi * radii ** 2 + (2*radii)**2) * 100  * 260
volume45 = (2 * np.pi * radii ** 2 + (2*radii)**2) * 100 * 284
metal_fuel.volume = volume0 + volume45

rodvolume = (2 * np.pi * radiirod ** 2 + (2*radiirod)**2) * 100 * (2.5 + 22)
rodmat.volume = rodvolume 

watervolume = (np.pi * 52**2) * 100 - volume0 - volume45 - rodvolume 
deuterium_bor.volume = watervolume 

materials = openmc.Materials([water,deuterium, zirc, helium, graphite, boron, lead, metal_fuel, rodmat, deuterium_bor, ht_steel])


#
materials.export_to_xml()
geometry.export_to_xml()




plot = openmc.Plot.from_geometry(geometry)
#plot.color_by = 'material'
plot.color_by = 'cell'

plot.basis = "xy"
#plot.width = [23.8, 23.8]
#plot.pixels = [8640,8640]
plot.pixels = [1080,1080]
#"""
plot.colors = {
    fuel : "green",
    fuel2 : "green",
    hegap : "green",
    moderator : "green",
    cladding : "green",
    hegap2 : "green",
    cladding2 : "green",
    moderator2: "green",
    empty: "blue",
    waterfill: "blue",
    controlrod : "yellow",
    cgap : "yellow",
    cclad: "yellow",
    cwater:"yellow",
    rrod : "red",
    cgap2: "red",
    cclad2: "red",
    cwater2: "red",
    containmentcell: "black"

}

"""
plot.colors = {
    metal_fuel : "green",
    deuterium_bor : "blue",
    water: "blue",
    zirc : "gray",
    helium: "red",
    rodmat: "yellow",
    ht_steel: "brown"
}
#"""

plot.to_ipython_image()


# OpenMC simulation parameters
settings = openmc.Settings()
settings.batches = 100
settings.inactive = 10
settings.particles = 1000


# Create an initial uniform spatial source distribution overfissionable zones
#bounds = [-11.9, -11.9, -150, 11.9, 11.9, 150]
#bounds = [-15.75 -31.5, -15.75 -31.5, -50, 15.75 + 31.5, 15.75+ 31.5, 50]
bounds = [-1.75, -1.75, -1, 1.75, 1.75, 1]

uniform_dist = openmc.stats.Box(bounds[:3], bounds[3:],only_fissionable = True)
settings.source = openmc.IndependentSource(space=uniform_dist)

# Export to "settings.xml"
settings.export_to_xml()







#Constructing a mesh 
mesh = openmc.RegularMesh()
mesh.dimension = [200,200]
#mesh.lower_left= [-15.75*3,-15.75*3]
#mesh.upper_right= [15.75*3,15.75*3]
mesh.lower_left= [-1.75,-1.75]
mesh.upper_right= [1.75,1.75]



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
#fuel_therm_abs_rate.filters = [openmc.EnergyFilter([0.0, 0.625])]
fuel_therm_abs_rate.filters = [openmc.EnergyFilter([0.0, 0.625]),
                               openmc.CellFilter([fuel])]
tallies_file.append(fuel_therm_abs_rate)
tallies_file.export_to_xml()


"""Making the simulation to a model for a depletion simulation"""

#sub_model = openmc.model.Model()
sub_model = openmc.Model()
sub_model.geometry = geometry
sub_model.materials = materials
sub_model.settings = settings
sub_model.tallies = tallies_file


"""Making a depletion complication"""




chain = openmc.deplete.Chain.from_xml("./chain_endfb80_pwr.xml")
#chain.nuclide_dict

operator = openmc.deplete.CoupledOperator(sub_model, "./chain_endfb80_pwr.xml")

power = 190e6

time_steps = [30 * 24 * 60 * 60] * 6

integrator = openmc.deplete.PredictorIntegrator(operator, time_steps, power)


if __name__ == "__main__":
    #Running the simulation
    openmc.run()
    #integrator.integrate()
    pass