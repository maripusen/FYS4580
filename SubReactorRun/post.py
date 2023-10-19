import openmc 
import matplotlib.pyplot as plt
import numpy as np
from f_assembly import erange


sp = openmc.StatePoint('statepoint.100.h5')

#"""
#energy = sp.get_tally(filters = [energy_filter])

tally = sp.tallies[1]
tally2 = sp.tallies[2]


flux = tally.get_slice(scores=['flux'])
prompt = tally.get_slice(scores=['prompt-nu-fission'])

#"""
# extracting thermal neutron absorption tallies

therm_abs_rate = sp.get_tally(id = 3)

# Compute thermal flux utilization factor using tally arithmetic
fuel_therm_abs_rate = sp.get_tally(id = 4)

therm_util = fuel_therm_abs_rate / therm_abs_rate
frame = therm_util.get_pandas_dataframe()
print(frame)

#"""



flux.std_dev.shape = (200, 200)
flux.mean.shape = (200, 200)
prompt.std_dev.shape = (200, 200)
prompt.mean.shape = (200, 200)


fig = plt.subplot(121)
fig.imshow(flux.mean)
fig2 = plt.subplot(122)
fig2.imshow(prompt.mean)
plt.show()
#"""


flx = tally2.mean.ravel()
flxu = tally2.std_dev.ravel()


plt.loglog(erange[:-1], flx)
plt.grid()
plt.xlabel("Energy eV")
plt.ylabel("Flux [n/cm-src]")
plt.title("Neutron energy spectrum")
plt.show()




