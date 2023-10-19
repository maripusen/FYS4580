import openmc 
import openmc.deplete
import matplotlib.pyplot as plt
import numpy as np

#Doing depletion calculations: 
depresults = openmc.deplete.Results("./depletion_results.h5")

time, k = depresults.get_keff()
time /= (24 * 60 * 60)

print(k)

plt.errorbar(time, k[:, 0], yerr=k[:, 1], label = "$k_{eff}\pm \sigma$", ecolor = "r")
plt.xlabel("Time [d]")
plt.ylabel("$k_{eff}\pm \sigma$");
plt.legend()
plt.show()


_time, u5 = depresults.get_atoms(mat = "16",nuc =  "U235")
_time, xe135 = depresults.get_atoms(mat = "16",nuc =  "Xe135")
_time, sm149 = depresults.get_atoms(mat = "16",nuc =  "Sm149")

plt.plot(time, u5, label="U235")
plt.xlabel("Time [d]")
plt.ylabel("Number of atoms - U235");
plt.legend()
plt.show()


plt.plot(time, xe135, label="Xe135")
plt.plot(time, sm149, label="Sm149")
plt.title("Production of Xenon - 135 and Samarium - 149 in the reactor")
plt.xlabel("Time [d]")
plt.ylabel("Number of atoms - Xe135");
plt.legend()
plt.show()



_time, u5_fission = depresults.get_reaction_rate(mat = "16",nuc = "U235", rx = "fission")
plt.plot(time, u5_fission)
plt.yscale("log")
plt.xlabel("Time [d]")
plt.ylabel("Fission reactions / s");
plt.legend()
plt.show()


#"""
_time, u5_abs = depresults.get_atoms(mat = "16",nuc = "U235")
_time, Pu5_abs = depresults.get_atoms(mat = "16",nuc = "Pu239")
plt.plot(time, Pu5_abs, label = "Plutonium 239")
plt.plot(time, u5_abs, label = "Uranium 235")
plt.xlabel("Time [d]")
plt.ylabel("Number of nuclides [N]");
plt.legend()
plt.show()
#"""


_time, u5_abs = depresults.get_atoms(mat = "16",nuc = "U235")
_time, Pu5_abs = depresults.get_atoms(mat = "16",nuc = "Pu239")
ratio = Pu5_abs/u5_abs
plt.plot(time, ratio, label = "Plutonium 239")
plt.xlabel("Time [d]")
plt.ylabel("Fraction of [N_Pu239 / N_U235]");
plt.show()