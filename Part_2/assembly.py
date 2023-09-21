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
water.set_density("g/cm3", 1.11)

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

#Defining controlrod material
boron = openmc.Material(6, "Boron")
boron.add_element("B" , 1.0)
boron.set_density("g/cm3", 2.3)

#Exporting a XML file wih the materials. 
materials = openmc.Materials([urox, water, zirc, helium, graphite, boron])
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
edge = "transmission"

#"""
xmin = openmc.XPlane(-0.7 , boundary_type = edge)
xmax = openmc.XPlane(0.7, boundary_type = edge)
ymin = openmc.YPlane(-0.7, boundary_type = edge)
ymax = openmc.YPlane(0.7, boundary_type = edge) 
#"""
zmin = openmc.ZPlane(-150, boundary_type = edge)
zmax = openmc.ZPlane(150, boundary_type = edge)

box = +xmin & - xmax & +ymin & - ymax & +zmin & - zmax


"""Making fuel cells and other material regions"""
fuel_reg = - urcyl & -zmax & +zmin
he_reg = + urcyl & - hecyl2 & -zmax & +zmin
zircclad = + hecyl2 & - zirccyl2 & -zmax & +zmin
borreg = fuel_reg
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

#Defining a single waterbox to fill in cells that should be empty 
waterbox = openmc.Cell(name = "waterbox")
waterbox.fill = water
waterbox.region = box


#Defining a control rod
controlrod = openmc.Cell(name = "control")
controlrod.fill = boron
controlrod.region = borreg

void = openmc.Cell(name = "void")
void.region =  he_reg

moderator2 = openmc.Cell(name = "moderator")
moderator2.fill = water
moderator2.region = water_reg

cladding2 = openmc.Cell(name = "cladding")
cladding2.fill = zirc
cladding2.region = zircclad 


#Defining universes
pin_universe = openmc.Universe(cells = [fuel, hegap, cladding, moderator])
water_universe = openmc.Universe(cells = [waterbox])
controlpin = openmc.Universe(cells = [controlrod,void,cladding2, moderator2])


#Constructing geometry
f = pin_universe
c = controlpin
w = water_universe

universii = []

for i in range (1,18):
    
    if i in [8,9,10]:
        universii.append([f] * 7 + [c]*3 + [f] * 7)
    else:
        universii.append([f]*17)



f_assembly = openmc.RectLattice(name = "fuel_assembly")
f_assembly.lower_left = [-11.9,-11.9]
f_assembly.upper_right = [11.9, 11.9]
f_assembly.universes = universii
f_assembly.pitch = [1.4,1.4]

water_cell = openmc.Cell(fill = water)
outer_uni = openmc.Universe(cells = [water_cell])

f_assembly.outer = outer_uni
print(f_assembly)

outedge = "vacuum"
outcap= openmc.ZPlane(0, boundary_type = outedge)
outbot = openmc.ZPlane(-300, boundary_type = outedge)
outcell = openmc.rectangular_prism(width = 23.8, height = 23.8, boundary_type = outedge)
#outcell = openmc.ZCylinder(r = 12, boundary_type = outedge)
#outcell = -outcell
#inner = outcell & +outbot
#outer_top = outcell & -outcap
#outer_bottom = -outbot

#outer = (outer_top & outer_bottom) - inner



f_cell = openmc.Cell(fill = f_assembly, region =  outcell)
cell_list = [f_cell, fuel, hegap, cladding, moderator, controlrod, void, moderator2]
assembly_uni = openmc.Universe(cells = cell_list)
geometry = openmc.Geometry()
geometry.root_universe = assembly_uni

geometry.export_to_xml()


plot = openmc.Plot.from_geometry(geometry)
plot.color_by = 'material'
plot.basis = "xz"
plot.width = [23.8, 600]
plot.pixels = [1080,1080]
#"""
plot.colors = {
    moderator: 'blue',
    moderator2: "blue",
    water_cell: "blue",
    hegap: 'red',
    cladding: 'gray',
    fuel: 'green',
    controlrod: 'brown',
    water: "blue",
    void: "white"
}
#"""

plot.to_ipython_image()

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




#openmc.run()