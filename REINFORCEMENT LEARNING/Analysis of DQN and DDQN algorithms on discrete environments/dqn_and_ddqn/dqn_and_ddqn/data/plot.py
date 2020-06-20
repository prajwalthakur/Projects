
import numpy as np
from matplotlib import pyplot as plt

dat = []
def adddata(path):
    a = np.loadtxt(path, skiprows=1, delimiter=",")
    xaxis = np.asarray(a[:,1])
    dat.append(a[:,2])
    return xaxis

xaxis = adddata("run-dqn_dqn_1_LunarLander-v2_15-06-2020_20-13-02-tag-Train_AverageReturn.csv")
adddata("run-dqn_dqn_2_LunarLander-v2_15-06-2020_20-44-55-tag-Train_AverageReturn.csv")
plt.plot(xaxis, np.mean(dat, axis=0), label="DQN")

dat = []
adddata("run-dqn_double_q_doubledqn_1_LunarLander-v2_15-06-2020_21-22-04-tag-Train_AverageReturn.csv")
adddata("run-dqn_double_q_doubledqn_2_LunarLander-v2_15-06-2020_21-53-33-tag-Train_AverageReturn.csv")
plt.plot(xaxis, np.mean(dat, axis=0), label="Double DQN")
plt.legend()
plt.title("LunarLander")
plt.savefig("DQNvsDDQN.png")
plt.close()


dat = []
xaxis = adddata("run-dqn_double_q_doubledqn_1_LunarLander-v2_15-06-2020_21-22-04-tag-Train_AverageReturn.csv")
adddata("run-dqn_double_q_doubledqn_2_LunarLander-v2_15-06-2020_21-53-33-tag-Train_AverageReturn.csv")
plt.plot(xaxis, dat[0])
plt.plot(xaxis, dat[1])
plt.title("DDQN trials")
plt.savefig("DDQN.png")
plt.close()

