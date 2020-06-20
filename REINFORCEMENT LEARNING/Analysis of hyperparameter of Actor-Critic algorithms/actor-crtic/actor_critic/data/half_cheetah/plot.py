import numpy as np
from matplotlib import pyplot as plt

a = np.loadtxt("run-ac_10_10_CartPole-v0_11-06-2020_16-49-52-tag-Eval_AverageReturn.csv", skiprows=1, delimiter=",")
a = a[a[:,1]<3e6]
plt.plot(a[:,1], a[:,2],label="Cartpole")


a = np.loadtxt("run-ac_10_10_HalfCheetah-v2_11-06-2020_17-05-28-tag-Eval_AverageReturn.csv", skiprows=1, delimiter=",")
a = a[a[:,1]<3e6]
plt.plot(a[:,1], a[:,2],label="HalfCheetah")


plt.title("Eval_AverageReturn,ntu=10,ngsptu=10")
plt.legend()
plt.savefig("actor_critic_HalfCheetah_VS_inverted_pendulum.png")
plt.close()


