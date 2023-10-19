import openmc 
import matplotlib.pyplot as plt
import numpy as np


#Defining uranium oxide material, set to real life density

urox = openmc.Material(name = "uo2")
urox.add_nuclide("U235", 0.3)
urox.add_nuclide("U238", 0.7)
#urox.add_element("O", 2.0)
urox.set_density("g/cm3", 19.0)


#defining water-moderator material
water = openmc.Material(name = "h2o")
water.add_nuclide("H1", 2.0)
water.add_element("O",1)
water.add_s_alpha_beta('c_H_in_H2O')
water.set_density("g/cm3", 1.0)

#Defining deuterium
deuterium = openmc.Material(name = "d20")
deuterium.add_nuclide("H2", 2.0)
deuterium.add_element("O",1.0)
#deuterium.add_s_alpha_beta("c_D_in_D2O")
deuterium.set_density("g/cm3",1.11)

#Defining a zircaloy 
zirc = openmc.Material(name = "Zr")
zirc.add_element("Zr", 0.975)
zirc.add_element("Nb", 0.025)
zirc.set_density("g/cm3", 6.49)

#defining helium gas
helium = openmc.Material(name = "He")
helium.add_element("He",1.0)
helium.set_density("g/cm3",0.000178)

#defining a graphite moderator
graphite = openmc.Material(name = "Graph")
graphite.add_element("C", 1.0)
graphite.set_density("g/cm3", 2.09)

#Defining controlrod material
boron = openmc.Material(name = "Boron")
boron.add_element("B" , 1.0)
boron.set_density("g/cm3", 2.3)

#Defining lead

lead = openmc.Material(name = "Lead")
lead.add_element("Pb",1.0)
lead.set_density("g/cm3", 11.33)
 


plutonium = openmc.Material(name = "Plutonium")
plutonium.add_nuclide("Pu239",0.72)
plutonium.add_nuclide("Pu238",0.01)
plutonium.add_nuclide("Pu242",0.04)
plutonium.add_nuclide("Pu240",0.14)
plutonium.add_nuclide("Pu241",0.07)
plutonium.add_nuclide("Am241",0.02)
plutonium.set_density("g/cm3",19.8)


silver = openmc.Material(name = "Silver")
silver.add_element("Ag",1.0)
silver.set_density("g/cm3", 10.49)
 

cadmium = openmc.Material(name = "Cadmium")
cadmium.add_element("Cd",1.0)
cadmium.set_density("g/cm3", 8.65)
 
boric_acid = openmc.Material(name = "boric_acid")
boric_acid.add_element("H",3.0)
boric_acid.add_element("B",1.0)
boric_acid.add_element("O",3.0)
boric_acid.depletable = True
boric_acid.set_density("g/cm3",1.435)

boron_carbide = openmc.Material(name = "B-Carbide")
boron_carbide.add_element("C",1.0)
boron_carbide.add_element("B",4.0)
boron_carbide.set_density("g/cm3",2.5)

ht_steel = openmc.Material(name = "high_tensile_steel")
#Known components of 980X high tensile steel
ht_steel.add_element("C", 0.0026)
ht_steel.add_element("Mn", 0.0165)
ht_steel.add_element("P", 0.0004)
ht_steel.add_element("S", 0.0004)
ht_steel.add_element("Si", 0.009)
ht_steel.add_element("Fe", 0.971)
ht_steel.set_density("g/cm3", 7.9)





deuterium_bor = openmc.Material.mix_materials([deuterium,boric_acid],[0.99999, 0.00001],"ao")
#rodmat = openmc.Material.mix_materials([boron, silver, cadmium], [0.35, 0.5, 0.15],"ao")
rodmat = boron_carbide
rodmat.depletable = True
metal_fuel = openmc.Material.mix_materials([urox, plutonium], [0.9,0.1], "ao")
