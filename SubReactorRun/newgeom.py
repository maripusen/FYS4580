import openmc 
import matplotlib.pyplot as plt
import numpy as np
from materials_gen import urox, water,deuterium, zirc, helium, graphite, boron, lead, plutonium, metal_fuel, rodmat, deuterium_bor, ht_steel

#exporting materials to xml
materials = openmc.Materials([urox, water,deuterium, zirc, helium, graphite, boron, lead, plutonium, metal_fuel, rodmat, deuterium_bor])
materials.export_to_xml()

"""Defining the pincell"""

#deuterium = water

#making the fuel pin
radii = 0.12
h1 = 2.0
edge = "transmission"

def plusgeom(radii, h1, le1, be1):

    c1 = openmc.ZCylinder(x0 = 0, y0 = radii ,r = radii, boundary_type = edge)
    c2 = openmc.ZCylinder(x0 = radii, y0 = 0 ,r = radii, boundary_type = edge)
    c3 = openmc.ZCylinder(x0 = 0, y0 = -radii ,r = radii, boundary_type = edge)
    c4 = openmc.ZCylinder(x0 = -radii, y0 = 0 ,r = radii, boundary_type = edge)
    b1 = openmc.rectangular_prism(width = radii, height = radii, boundary_type = edge)

    #making the helium gap
    gap = 0.03
    cg1 = openmc.ZCylinder(x0 = 0, y0 = radii ,r = radii+ gap, boundary_type = edge)
    cg2 = openmc.ZCylinder(x0 = radii, y0 = 0 ,r = radii + gap, boundary_type = edge)
    cg3 = openmc.ZCylinder(x0 = 0, y0 = -radii ,r = radii + gap, boundary_type = edge)
    cg4 = openmc.ZCylinder(x0 = -radii, y0 = 0 ,r = radii + gap, boundary_type = edge)
    bg1 = openmc.rectangular_prism(width = radii+ gap, height = radii + gap, boundary_type = edge)

    #making cladding region

    gap2 = 0.08
    cc1 = openmc.ZCylinder(x0 = 0, y0 = radii ,r = radii+ gap2, boundary_type = edge)
    cc2 = openmc.ZCylinder(x0 = radii, y0 = 0 ,r = radii + gap2, boundary_type = edge)
    cc3 = openmc.ZCylinder(x0 = 0, y0 = -radii ,r = radii + gap2, boundary_type = edge)
    cc4 = openmc.ZCylinder(x0 = -radii, y0 = 0 ,r = radii + gap2, boundary_type = edge)
    bc1 = openmc.rectangular_prism(width = radii+gap2, height = radii+gap2, boundary_type = edge)

    pinedge = "reflective"
    box = openmc.rectangular_prism(width = le1, height = be1, boundary_type = pinedge)
    cap = openmc.ZPlane(z0 = h1/2, boundary_type = pinedge)
    bot = openmc.ZPlane(z0 = -h1/2, boundary_type = pinedge)


    box = box & +bot & -cap


    #Defining fuel region
    c1 = -c1 & +bot & -cap
    c2 = -c2 & +bot & -cap
    c3 = -c3 & +bot & -cap
    c4 = -c4 &+bot & -cap
    b1 = b1 & +bot & -cap

    fuel_reg = b1 | c1 | c2 | c3 | c4 

    #Defining helium gap
    cg1 = -cg1 & +bot & -cap
    cg2 = -cg2 & +bot & -cap
    cg3 = -cg3 & +bot & -cap
    cg4 = -cg4 &+bot & -cap
    bg1 = bg1 & +bot & -cap

    hereg = bg1 | cg1 | cg2 | cg3 | cg4 
    hereg = ~fuel_reg & hereg 

    #Defining cladding region
    cc1 = -cc1 & +bot & -cap
    cc2 = -cc2 & +bot & -cap
    cc3 = -cc3 & +bot & -cap
    cc4 = -cc4 &+bot & -cap
    bc1 = bc1 & +bot & -cap


    cladding = bc1 | cc1 | cc2 | cc3 | cc4 
    clad_reg = ~hereg &~fuel_reg & cladding

    box = box &~ clad_reg &~ hereg &~ fuel_reg

    return box, fuel_reg, hereg, clad_reg, bot, cap

le1 = 3.5 
be1 = 3.5
box, fuel_reg, hereg, clad_reg, bot, cap = plusgeom(radii, h1, le1, be1)

"""Making a pincell that is rotated 0 degrees"""
fuel = openmc.Cell(name = "fuel")
fuel.fill = metal_fuel
fuel.region = fuel_reg

hegap = openmc.Cell(name = "helium")
hegap.fill = helium
hegap.region = hereg

cladding = openmc.Cell(name = "cladding")
cladding.fill = zirc
cladding.region = clad_reg

moderator = openmc.Cell(name = "moderator")
moderator.fill = deuterium_bor
moderator.region = box

"""Making the clones for the 45 degree rotated pincell"""

fuel_reg45 = fuel_reg.clone()
fuel_reg45 = fuel_reg45.rotate((0,0,45))

hereg45 = hereg.clone()
hereg45 = hereg45.rotate((0,0,45))

clad_reg45 = clad_reg.clone()
clad_reg45 = clad_reg45.rotate((0,0,45))

box45 = openmc.rectangular_prism(width = 3.5, height = 3.5, boundary_type = edge)
box45 = box45 & +bot & -cap
box45 = box45 &~ clad_reg45 &~ hereg45 &~ fuel_reg45


"""Making the new cells for the 45 degree pins"""

fuel2 = openmc.Cell(name = "fuel2")
fuel2.fill = metal_fuel
fuel2.region = fuel_reg45

hegap2 = openmc.Cell(name = "helium2")
hegap2.fill = helium
hegap2.region = hereg45

cladding2 = openmc.Cell(name = "cladding2")
cladding2.fill = zirc
cladding2.region = clad_reg45

moderator2 = openmc.Cell(name = "moderator2")
moderator2.fill = deuterium_bor
moderator2.region = box45


#defining an empty cell to be used 
emptybox = openmc.rectangular_prism(width = 3.5, height = 3.5, boundary_type = edge)
emptybox = emptybox & + bot & - cap

empty = openmc.Cell(name  =  "filler")
empty.fill = deuterium_bor
empty.region = emptybox

#making the simple pincell universes where p1 is unrotated the p2 is and p3 is just water
p1 = openmc.Universe(cells = [fuel,hegap,cladding,moderator])
p2 = openmc.Universe(cells = [fuel2, hegap2,cladding2,moderator2])
p3 = openmc.Universe(cells = [empty])




#"""
if __name__ == "__main__":
    
    p1.plot(basis = "xy", pixels = [800,800],
              colors = {fuel: "green", hegap: "brown", 
                        cladding: "gray", moderator : "blue"})
    plt.show()

    p1.plot(basis = "xz", pixels = [800,800],
              colors = {fuel: "green", hegap: "brown", 
                        cladding: "gray", moderator : "blue"})
    plt.show()

    p2.plot(basis = "xy", pixels = [800,800],
              colors = {fuel2: "green", hegap2: "brown", 
                        cladding2: "gray", moderator2: "blue"})
    plt.show()

    p2.plot(basis = "xz", pixels = [800,800],
              colors = {fuel2: "green", hegap2: "brown", 
                        cladding2: "gray", moderator2: "blue"})
    plt.show()
#"""

"""Making the controlrod"""
le1 = 3.5
be1 = 3.5
radiirod = 0.75
hrod = 2

box1, rod_reg, dgap1, clad_reg1, v1,v2 = plusgeom(radiirod, hrod, le1,be1)

controlrod = openmc.Cell(name = "controlrod")
controlrod.fill = rodmat
controlrod.region = rod_reg

cgap = openmc.Cell(name = "gap")
cgap.fill = deuterium_bor
cgap.region = dgap1

cclad = openmc.Cell(name = "rod_cladding")
cclad.fill = zirc
cclad.region = clad_reg1

cwater = openmc.Cell(name = "cladwater")
cwater.fill = deuterium_bor
cwater.region = box1

"""Making an retracted controlrod"""
#"""

box2, rod_reg2, dgap2, clad_reg2, v11,v22 = plusgeom(0.75, 2, 3.5, 3.5)


rrod = openmc.Cell(name = "controlrod_2")
rrod.fill = deuterium_bor
rrod.region = rod_reg2

cgap2 = openmc.Cell(name = "gap_2")
cgap2.fill = deuterium_bor
cgap2.region = dgap2

cclad2 = openmc.Cell(name = "rod_cladding_2")
cclad2.fill = zirc
cclad2.region = clad_reg2

cwater2 = openmc.Cell(name = "cladwater_2")
cwater2.fill = deuterium_bor
cwater2.region = box2

retrod = openmc.Universe(cells = [rrod, cgap2, cclad2, cwater2])
r2 = retrod
#"""
rod = openmc.Universe(cells = [controlrod, cgap, cclad, cwater])

r1 = rod


"""Constructing fuel assemblies"""
assembly_x = 9
assembly_y = 9 
assembly_z = 50
universii = np.zeros((assembly_z,assembly_x,assembly_y), dtype = openmc.Universe)
universii.fill(p2)
#Constructing fuelassembly geometry
for z in range(0,assembly_z):
    for i in range (0,assembly_x):
        for j in range(0,assembly_y):
            if i in [0,2,4,6,8] and j in [0,2,4,6,8]:
                universii[z][i][j] = p1
            elif i in [1,3,5,7] and j in [1,3,5,7]:
                universii[z][i][j] = p1
            #adding in some cells for controlrods and just moderator
            if i == 2 and j == 4:
                universii[z][i][j] = r2
            if i == 4 and j in [2,6]:
                universii[z][i][j] = r1
            if i == 4 and j == 4:
                universii[z][i][j] = r2
            if i == 4 and j == 4 and z > 24:
                universii[z][i][j] = r1
            if i == 6 and j == 4:
                universii[z][i][j] = r2



"""Constructing diagonal corner matrices for the core"""
universtr = np.zeros((assembly_z,assembly_x,assembly_y), dtype = openmc.Universe)
universtl = np.zeros((assembly_z,assembly_x,assembly_y), dtype = openmc.Universe)
universll = np.zeros((assembly_z,assembly_x,assembly_y), dtype = openmc.Universe)
universlr = np.zeros((assembly_z,assembly_x,assembly_y), dtype = openmc.Universe)
universtr.fill(p2)
universtl.fill(p2)
universlr.fill(p2)
universll.fill(p2)

for z in range(0,assembly_z):
    for i in range (0,assembly_x):
        for j in range(0,assembly_y):
            if j >i:
                universtr[z][i][j] = p3
#            if j == i: 
#                universtr[z][i][j] = 2
            elif i == 1 and j == 0:
                universtr[z][i][j] = p1
            elif i == 2 and j == 1: 
                universtr[z][i][j] = p1
            elif i == 3 and j in [0,2]:
                universtr[z][i][j] = p1
            elif i == 4 and j in [1,3]:
                universtr[z][i][j] = p1
            elif i == 5 and j in [0,2,4]:
                universtr[z][i][j] = p1
            elif i == 6 and j in [1,3,5]:
                universtr[z][i][j] = p1
            elif i == 7 and j in [0,2,4,6]:
                universtr[z][i][j] = p1
            elif i == 8 and j in [1,3,5,7]:
                universtr[z][i][j] = p1
                
universtr[0][0][0] = r1
universtr[0][-1][0] = r2;
universtr[0][-1][-1] = r1
universtr[0][4][4] = r1
universtr[:] = universtr[0]

universtl[:] = np.rot90(universtr[0])
universll[:] = np.rot90(universtl[0])
universlr[:] = np.rot90(universll[0])




"""Making the corner matrices for a simple core """

########################### top right

tr_assembly = openmc.RectLattice(name = "fuel_assembly")
tr_assembly.lower_left = (-assembly_x*abs(1.75),-assembly_y*abs(1.75),-assembly_z)
tr_assembly.universes = universtr
tr_assembly.pitch = (3.5,3.5,2)

#Defining the outer universe for the fuelassembly of all configurations
water_cell = openmc.Cell(fill = water)
outer_uni = openmc.Universe(cells = [water_cell])
tr_assembly.outer = outer_uni

########################### top left

tl_assembly = openmc.RectLattice(name = "fuel_assembly")
tl_assembly.lower_left = (-assembly_x*abs(1.75),-assembly_y*abs(1.75),-assembly_z)
tl_assembly.universes = universtl
tl_assembly.pitch = (3.5,3.5,2)

#Defining the outer universe for the fuelassembly of all configurations
tl_assembly.outer = outer_uni

########################### lower left

ll_assembly = openmc.RectLattice(name = "fuel_assembly")
ll_assembly.lower_left = (-assembly_x*abs(1.75),-assembly_y*abs(1.75),-assembly_z)
ll_assembly.universes = universll
ll_assembly.pitch = (3.5,3.5,2)

#Defining the outer universe for the fuelassembly of all configurations
ll_assembly.outer = outer_uni

########################### lower right

lr_assembly = openmc.RectLattice(name = "fuel_assembly")
lr_assembly.lower_left = (-assembly_x*abs(1.75),-assembly_y*abs(1.75),-assembly_z)
lr_assembly.universes = universlr
lr_assembly.pitch = (3.5,3.5,2)

#Defining the outer universe for the fuelassembly of all configurations
ll_assembly.outer = outer_uni



"""Making a simple assembly for the central positions"""
f_assembly = openmc.RectLattice(name = "fuel_assembly")
f_assembly.lower_left = (-assembly_x*abs(1.75),-assembly_y*abs(1.75),-assembly_z)
f_assembly.universes = universii
f_assembly.pitch = (3.5,3.5,2)


f_assembly.outer = outer_uni


#Making the assembly gemometry
outedge = "vacuum"
outcap= openmc.ZPlane(assembly_z, boundary_type = outedge)
outbot = openmc.ZPlane(-assembly_z, boundary_type = outedge)
outcell = openmc.rectangular_prism(width = 31.5, height = 31.5, boundary_type = outedge)
outcell = outcell &+outbot &-outcap

#Making the cells for the assembly
f_cell = openmc.Cell(fill = f_assembly, region =  outcell)
cell_list = [f_cell]
assembly_unic = openmc.Universe(cells = cell_list)

#Making the top right cell
tr_cell = openmc.Cell(fill = tr_assembly, region =  outcell)
cell_tr = [tr_cell]
assembly_unitr = openmc.Universe(cells = cell_tr)

#Making the top left cell
tl_cell = openmc.Cell(fill = tl_assembly, region =  outcell)
cell_tl = [tl_cell]
assembly_unitl = openmc.Universe(cells = cell_tl)

#Making the lower left cell
ll_cell = openmc.Cell(fill = ll_assembly, region =  outcell)
cell_ll = [ll_cell]
assembly_unill = openmc.Universe(cells = cell_ll)

#making the lower right cell
lr_cell = openmc.Cell(fill = lr_assembly, region =  outcell)
cell_lr = [lr_cell]
assembly_unilr = openmc.Universe(cells = cell_lr)




"""------------Making the coooooreeeeee------------"""

core_config = np.zeros((3,3), dtype=openmc.Universe)
core_config.fill(assembly_unic)

core_config[0][0] = assembly_unitl; core_config[0][-1] = assembly_unitr
core_config[-1][0] = assembly_unill; core_config[-1][-1] = assembly_unilr

#Making the containment structure
edges_out = "vacuum"
edges_in = "transmission"
con_r = 52
gap_r = 10
c_inner = openmc.ZCylinder(r = con_r, boundary_type = edges_in)
c_outer = openmc.ZCylinder(r = con_r + gap_r, boundary_type = edges_out)
cap1 = openmc.ZPlane(assembly_z, boundary_type = edges_in)
cap2 = openmc.ZPlane(assembly_z+gap_r, boundary_type = edges_out)
bot1 = openmc.ZPlane(-assembly_z, boundary_type = edges_in)
bot2 = openmc.ZPlane(-assembly_z-gap_r, boundary_type = edges_out)


#containment = - c_outer & + c_inner #&-cap2 & +cap1 & +bot2 &-bot1
containment = - c_outer & +bot2 &-cap2
conwat = -c_inner & +bot1 & - cap1
containment = containment &~conwat
#conwat = -c_inner


containmentcell = openmc.Cell(name = "Containment")
containmentcell.fill = ht_steel
containmentcell.region = containment

waterfill = openmc.Cell(name = "WaterCon")
waterfill.fill = deuterium_bor
waterfill.region = conwat



#outer_core = openmc.Universe(cells = [containmentcell,waterfill])
outer_core = openmc.Universe(cells = [waterfill])


core = openmc.RectLattice(name = "Reactor_Core")
core.lower_left = (-(9*le1) * 1.5,-(9*be1) * 1.5)
core.universes = core_config
core.outer = outer_core
core.pitch = ((9*le1),(9*be1))


#print(core)
core_cell = openmc.Cell(fill = core, region = conwat)

core_uni = openmc.Universe(name = "Core")
core_uni.add_cell(core_cell)
core_uni.add_cell(containmentcell)

geometry = openmc.Geometry()
#geometry.root_universe = core_uni
#geometry.root_universe = assembly_universe
geometry.root_universe = p1

