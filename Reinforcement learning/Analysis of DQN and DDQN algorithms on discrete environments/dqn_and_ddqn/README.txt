
1>
python run_hw3_dqn.py --env_name PongNoFrameskip-v4 --exp_name dqn -gpu

#enable gpu flag to use gpu while training

2) Visualize saved tensorboard event file:

$ cd cs285/data/<your_log_dir>
$ tensorboard --logdir .

