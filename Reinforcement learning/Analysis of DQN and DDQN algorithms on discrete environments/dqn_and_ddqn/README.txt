
1>
python dqn.py --env_name PongNoFrameskip-v4 --exp_name dqn -gpu

#enable gpu flag to use gpu while training



dqn vs ddqn
python dqn.py --env_name LunarLander-v2 --exp_name dqn_1 --seed 1

python dqn.py --env_name LunarLander-v2 --exp_name dqn_2 --seed 2

python dqn.py --env_name LunarLander-v2 --exp_name dqn_3 --seed 3


ddqn
python dqn.py --env_name LunarLander-v2 --exp_name doubledqn_1 --double_q --seed 1

python dqn.py --env_name LunarLander-v2 --exp_name doubledqn_2 --double_q --seed 2


python dqn.py --env_name LunarLander-v2 --exp_name doubledqn_3 --double_q --seed 3






2) Visualize saved tensorboard event file:

$ cd cs285/data/<your_log_dir>
$ tensorboard --logdir .

