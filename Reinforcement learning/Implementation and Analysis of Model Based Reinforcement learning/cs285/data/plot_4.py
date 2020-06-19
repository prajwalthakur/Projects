import numpy as np
from matplotlib import pyplot as plt

a = np.loadtxt("run-mb_q5_reacher_horizon5_reacher-cs285-v0_16-06-2020_20-28-03-tag-Eval_AverageReturn.csv", skiprows=1, delimiter=",")
plt.plot(a[:,1], a[:,2], label="Horizon=5")
a = np.loadtxt("run-mb_q5_reacher_horizon15_reacher-cs285-v0_16-06-2020_20-56-49-tag-Eval_AverageReturn.csv", skiprows=1, delimiter=",")
plt.plot(a[:,1], a[:,2], label="Horizon=15")
a = np.loadtxt("run-mb_q5_reacher_horizon30_reacher-cs285-v0_16-06-2020_21-32-11-tag-Eval_AverageReturn.csv", skiprows=1, delimiter=",")
plt.plot(a[:,1], a[:,2], label="Horizon=30")
plt.title("variation Reacher - Horizon on average return")
plt.legend()
plt.savefig("41.png")
plt.close()

a = np.loadtxt("run-mb_q5_reacher_numseq100_reacher-cs285-v0_16-06-2020_22-30-47-tag-Eval_AverageReturn.csv", skiprows=1, delimiter=",")
plt.plot(a[:,1], a[:,2], label="Action seq=100")
a = np.loadtxt("run-mb_q5_reacher_numseq1000_reacher-cs285-v0_16-06-2020_22-53-23-tag-Eval_AverageReturn.csv", skiprows=1, delimiter=",")
plt.plot(a[:,1], a[:,2], label="Action seq=1000")
plt.title(" variation of eval_avg return on Reacher env  -by Num. Action Sequences")
plt.legend()
plt.savefig("42.png")
plt.close()

a = np.loadtxt("run-mb_q5_reacher_ensemble1_reacher-cs285-v0_16-06-2020_23-20-02-tag-Eval_AverageReturn.csv", skiprows=1, delimiter=",")
plt.plot(a[:,1], a[:,2], label="Ensemble=1")
a = np.loadtxt("run-mb_q5_reacher_ensemble3_reacher-cs285-v0_16-06-2020_23-55-15-tag-Eval_AverageReturn.csv", skiprows=1, delimiter=",")
plt.plot(a[:,1], a[:,2], label="Ensemble=3")
a = np.loadtxt("run-mb_q5_reacher_ensemble5_reacher-cs285-v0_17-06-2020_00-39-38-tag-Eval_AverageReturn.csv", skiprows=1, delimiter=",")
plt.plot(a[:,1], a[:,2], label="Ensemble=5")
plt.title("Reacher - Num. Model Ensembles (eval_average_return)")
plt.legend()
plt.savefig("43.png")
plt.close()
