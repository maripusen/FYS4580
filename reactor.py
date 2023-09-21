import openmc 
import matplotlib.pyplot as plt
import numpy as np

#Defining uranium oxide material, set to real life density

urox = openmc.Material(1, "uo2")
urox.add_nuclide("U235", 0.02)
urox.add_nuclide("U238", 0.98)
urox.add_element("O", 2.0)
urox.set_density("g/cm3", 10.97)


#defining water-moderator material
water = openmc.Material(2, "h2o")
water.add_nuclide("H2", 2.0)
water.add_element("O",1)
water.add_s_alpha_beta('c_D_in_D2O')
water.set_density("g/cm3", 1.1)

#Defining a zircaloy 
zirc = openmc.Material(3, "Zr")
zirc.add_element("Zr", 1.0)
zirc.set_density("g/cm3", 6.49)

#defining helium gas
helium = openmc.Material(4,"He")
helium.add_element("He",1.0)
helium.set_density("g/cm3",0.000178)

#defining a graphite moderator
graphite = openmc.Material(5, "Graph")
graphite.add_element("C", 1.0)
graphite.set_density("g/cm3", 2.09)

weird = openmc.Material(6, "Weird")
weird.add_element("C", 1.0)
weird.set_density("g/cm3", 1.0)

#Exporting a XML file wih the materials. 
materials = openmc.Materials([urox, water, zirc, helium, graphite])
materials.export_to_xml()


"""""Defining geometry"""
#Defining cylinder regions for the pincell
inneredge = "transmission"

base = 0.4 - 0.07

urcyl = openmc.ZCylinder(r = base, boundary_type = inneredge)
hecyl2 = openmc.ZCylinder(r = base + 0.02, boundary_type = inneredge)
zirccyl2 = openmc.ZCylinder(r = base + 0.07, boundary_type = inneredge)

#"""

#making box of 1.4 cm x 1.4cm x 2cm

#defining a simple variable for box edge properties
edge = "reflective"

#"""
xmin = openmc.XPlane(-0.7 , boundary_type = edge)
xmax = openmc.XPlane(0.7, boundary_type = edge)
ymin = openmc.YPlane(-0.7, boundary_type = edge)
ymax = openmc.YPlane(0.7, boundary_type = edge) 
#"""
zmin = openmc.ZPlane(-1, boundary_type = edge)
zmax = openmc.ZPlane(1, boundary_type = edge)

box = +xmin & - xmax & +ymin & - ymax & +zmin & - zmax


"""Making fuel cells and other material regions"""
fuel_reg = - urcyl & -zmax & +zmin
he_reg = + urcyl & - hecyl2 & -zmax & +zmin
zircclad = + hecyl2 & - zirccyl2 & -zmax & +zmin
water_reg = +zirccyl2 & box



fuel = openmc.Cell(name = "fuel")
fuel.fill = urox
fuel.region = fuel_reg

hegap = openmc.Cell(name = "hegap")
hegap.fill = helium
hegap.region = he_reg

cladding = openmc.Cell(name = "cladding")
cladding.fill = zirc
cladding.region = zircclad 

moderator = openmc.Cell(name = "moderator")
moderator.fill = water
moderator.region = water_reg


#Defining 
root_universe = openmc.Universe(cells = [fuel, hegap, cladding, moderator])

#Export geometry
geometry = openmc.Geometry()
geometry.root_universe = root_universe
geometry.export_to_xml()


#"""
if __name__ == "__main__":
    root_universe.plot(basis = "xy", 
              colors = {fuel: "green", hegap: "brown", 
                        cladding: "gray", moderator: "cyan"})
    plt.show()

    root_universe.plot(basis = "xz", 
              colors = {fuel: "green", hegap: "brown", 
                        cladding: "gray", moderator: "cyan"})
    plt.show()

#"""

# OpenMC simulation parameters
settings = openmc.Settings()
settings.batches = 100
settings.inactive = 10
settings.particles = 10000


# Create an initial uniform spatial source distribution overfissionable zones
bounds = [-0.7, -0.7, -1, 0.7, 0.7, 1]
uniform_dist = openmc.stats.Box(bounds[:3], bounds[3:],only_fissionable=True)
settings.source = openmc.IndependentSource(space=uniform_dist)

# Export to "settings.xml"
settings.export_to_xml()



#extracting mesh coords
meshcor = box.bounding_box

#Constructing a mesh 
mesh = openmc.RegularMesh()
mesh.dimension = [100,100]
mesh.lower_left= [-0.7,-0.7]
mesh.upper_right= [0.7,0.7]



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

