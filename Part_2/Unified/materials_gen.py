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
water.add_nuclide("H1", 2.0)
water.add_element("O",1)
water.add_s_alpha_beta('c_H_in_H2O')
water.set_density("g/cm3", 1.0)

#Defining deuterium
deuterium = openmc.Material(3,"d20")
deuterium.add_nuclide("H2", 2.0)
deuterium.add_element("O",1.0)
deuterium.add_s_alpha_beta("c_D_in_D2O")
deuterium.set_density("g/cm3",1.11)

#Defining a zircaloy 
zirc = openmc.Material(4, "Zr")
zirc.add_element("Zr", 1.0)
zirc.set_density("g/cm3", 6.49)

#defining helium gas
helium = openmc.Material(5,"He")
helium.add_element("He",1.0)
helium.set_density("g/cm3",0.000178)

#defining a graphite moderator
graphite = openmc.Material(6, "Graph")
graphite.add_element("C", 1.0)
graphite.set_density("g/cm3", 2.09)

#Defining controlrod material
boron = openmc.Material(7, "Boron")
boron.add_element("B" , 1.0)
boron.set_density("g/cm3", 2.3)

#Defining lead

lead = openmc.Material(8, "Lead")
lead.add_element("Pb",1.0)
lead.set_density("g/cm3", 11.33)
 