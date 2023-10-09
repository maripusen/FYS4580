import openmc 
import matplotlib.pyplot as plt
import numpy as np
from materials_gen import urox, water,deuterium, zirc, helium, graphite, boron, lead

materials = openmc.Materials([urox, water,deuterium, zirc, helium, graphite, boron, lead])


"""Defining geometry"""
#Defining cylinder regions for the pincell
inneredge = "transmission"

pinx = -0.7
piny = -0.7
pinz = -1

base = 0.4 - 0.07

urcyl = openmc.ZCylinder(r = base, boundary_type = inneredge)
hecyl2 = openmc.ZCylinder(r = base + 0.02, boundary_type = inneredge)
zirccyl2 = openmc.ZCylinder(r = base + 0.07, boundary_type = inneredge)

#"""

#making box of 1.4 cm x 1.4cm x 2cm

#defining a simple variable for box edge properties
edge = "transmission"

#"""
xmin = openmc.XPlane(pinx , boundary_type = edge)
xmax = openmc.XPlane(-pinx, boundary_type = edge)
ymin = openmc.YPlane(piny, boundary_type = edge)
ymax = openmc.YPlane(-piny, boundary_type = edge) 
#"""
zmin = openmc.ZPlane(pinz, boundary_type = edge)
zmax = openmc.ZPlane(-pinz, boundary_type = edge)

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
moderator.fill = deuterium
moderator.region = water_reg

#Defining a single waterbox to fill in cells that should be empty 
waterbox = openmc.Cell(name = "waterbox")
waterbox.fill = deuterium
waterbox.region = box

#Defining a control rod
controlrod = openmc.Cell(name = "control")
controlrod.fill = boron
#controlrod.fill = deuterium
controlrod.region = borreg

void = openmc.Cell(name = "void")
void.fill = deuterium
void.region =  he_reg

moderator2 = openmc.Cell(name = "moderator_2")
moderator2.fill = deuterium
moderator2.region = water_reg

cladding2 = openmc.Cell(name = "cladding")
cladding2.fill = zirc
cladding2.region = zircclad 


#Defining universes for the rectangular lattice 
pin_universe = openmc.Universe(cells = [fuel, hegap, cladding, moderator])
water_universe = openmc.Universe(cells = [waterbox])
controlpin = openmc.Universe(cells = [controlrod,void ,cladding2, moderator2])


#Constructing geometry
f = pin_universe
c = controlpin
w = water_universe

#universii = []

assembly_x = 17
assembly_y = 17 
assembly_z = 150

universii = np.zeros((assembly_z,assembly_x,assembly_y), dtype = openmc.Universe)

#Constructing fuelassembly geometry
for z in range(0,150):
    for i in range (0,17):
        for j in range(0,17): 
            if i in [7,8,9] and j in [7,8,9]:
                universii[z][i][j] = c
            else:
                universii[z][i][j] = f


f_assembly = openmc.RectLattice(name = "fuel_assembly")
f_assembly.lower_left = (-assembly_x*abs(pinx),-assembly_y*abs(piny),-assembly_z)
f_assembly.universes = universii
f_assembly.pitch = (1.4,1.4,2)



#Defining the outer universe for the fuelassembly
water_cell = openmc.Cell(fill = water)
outer_uni = openmc.Universe(cells = [water_cell])
f_assembly.outer = outer_uni

#Making the assembly gemometry
outedge = "reflective"
outcap= openmc.ZPlane(assembly_z, boundary_type = outedge)
outbot = openmc.ZPlane(-assembly_z, boundary_type = outedge)
outcell = openmc.rectangular_prism(width = 23.8, height = 23.8, boundary_type = outedge)
outcell = outcell &+outbot &-outcap


f_cell = openmc.Cell(fill = f_assembly, region =  outcell)
cell_list = [f_cell]
assembly_uni = openmc.Universe(cells = cell_list)

#############################
"""Making the reactor core"""
#############################


water_assembly = np.zeros((assembly_z,assembly_x,assembly_y), dtype = openmc.Universe)
water_assembly[:][:][:] = w

w_assembly = openmc.RectLattice(name = "water_fill")
w_assembly.lower_left = (-assembly_x*abs(pinx),-assembly_y*abs(piny),-assembly_z)
w_assembly.universes = water_assembly
w_assembly.outer = outer_uni
w_assembly.pitch = (1.4,1.4,2)
#ws = [openmc.Cell(fill = w_assembly, region = outcell)]

ws = openmc.Cell(name="ws", fill=w_assembly)
ws_universe = openmc.Universe(name="ws_universe")
ws_universe.add_cell(ws)


a = assembly_uni
b = ws_universe#openmc.Universe(ws)



core_config = np.zeros((7,7), dtype=openmc.Universe)
core_config[:][:] = a
core_config[0][0] = b; core_config[0][1] = b; core_config[1][0] = b  
core_config[0][-1] = b; core_config[0][-2] = b; core_config[1][-1] = b
core_config[-1][0] = b; core_config[-1][1] = b; core_config[-2][0] = b
core_config[-1][-1] = b; core_config[-1][-2] = b; core_config[-2][-1] = b
#print(np.shape(core_config))
#print(core_config[0][0][0])


edges_q = "transmission"
c_inner = openmc.ZCylinder(r = 200/2, boundary_type = "vacuum")
c_outer = openmc.ZCylinder(r = 125/2+ 50, boundary_type = edges_q)
cap1 = openmc.ZPlane(150, boundary_type = "vacuum")
cap2 = openmc.ZPlane(200, boundary_type = edges_q)
bot1 = openmc.ZPlane(-150, boundary_type = "vacuum")
bot2 = openmc.ZPlane(-200, boundary_type = edges_q)


#containment = - c_outer & + c_inner #&-cap2 & +cap1 & +bot2 &-bot1
containment = - c_outer & + c_inner
conwat = -c_inner & +bot1 & - cap1
#conwat = -c_inner


containmentcell = openmc.Cell(name = "Containment")
containmentcell.fill = lead
containmentcell.region = containment

waterfill = openmc.Cell(name = "WaterCon")
waterfill.fill = deuterium
waterfill.region = conwat



#outer_core = openmc.Universe(cells = [containmentcell,waterfill])
outer_core = openmc.Universe(cells = [waterfill])


core = openmc.RectLattice(name = "Reactor_Core")
core.lower_left = (-11.9-23.8*3,- 11.9-23.8*3)
core.universes = core_config
core.outer = outer_core
core.pitch = (23.8,23.8)


#print(core)
c_cell = openmc.Cell(fill = core, region = conwat)

core_uni = openmc.Universe(name = "Core")
core_uni.add_cell(c_cell)
#core_uni.add_cell(containmentcell)
#core_uni.add_cell(waterfill)

geometry = openmc.Geometry()
geometry.root_universe = core_uni
#geometry.root_universe = assembly_uni   


