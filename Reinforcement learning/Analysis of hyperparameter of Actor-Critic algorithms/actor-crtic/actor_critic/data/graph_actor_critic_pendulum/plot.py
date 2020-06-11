import numpy as np
from matplotlib import pyplot as plt

a = np.loadtxt("run-ac_10_10_CartPole-v0_11-06-2020_16-49-52-tag-Eval_AverageReturn.csv", skiprows=1, delimiter=",")
a = a[a[:,1]<3e6]
plt.plot(a[:,1], a[:,2],label="ntu=10;ngsptu=10")


a = np.loadtxt("run-ac_1_100_CartPole-v0_11-06-2020_16-53-07-tag-Eval_AverageReturn.csv", skiprows=1, delimiter=",")
a = a[a[:,1]<3e6]
plt.plot(a[:,1], a[:,2],label="ntu=1;ngsptu=100")

a = np.loadtxt("run-ac_1_1_CartPole-v0_11-06-2020_16-37-06-tag-Eval_AverageReturn.csv", skiprows=1, delimiter=",")
a = a[a[:,1]<3e6]
plt.plot(a[:,1], a[:,2],label="ntu=1;ngsptu=1")


a = np.loadtxt("run-ac_100_1_CartPole-v0_11-06-2020_16-54-59-tag-Eval_AverageReturn.csv", skiprows=1, delimiter=",")
a = a[a[:,1]<3e6]
plt.plot(a[:,1], a[:,2],label="ntu=100;ngsptu=1")


plt.title("Eval_AverageReturn")
plt.legend()
plt.savefig("actor_critic_inverted_pendulum.png")
plt.close()


