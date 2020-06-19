**MODEL BASED REINFORCEMENT LEARNING**

**With On-Policy Data Collection and Ensemble Bootstrapping**

![](.//media/image1.gif)

After 0<sup>th</sup> iteration

![](.//media/image2.gif)

After 18<sup>th</sup> iteration

Model Based Reinforcement learning (MBRL) consists primarily of two
aspects: (1) learning a dynamics model and (2)using the learned dynamics
models to plan and execute actions that minimize a cost function (or
maximize a reward function).

(\*In this work, we assume access to the underlying reward function,
which we use for planning actions under the learned model.)

1\>Learning Dynamics Model

Instead of learning next state we would learn the change in state
instead :

![](.//media/image3.png)

such that:

![](.//media/image4.png)

why to train network to predict state differences, instead of directly
predicting next state?

:The functions where we learn the next state from current state-action
pair can be difficult to learn when the states s t and s t+1 are too
similar and the action has seemingly little effect on the output;this
difficulty becomes more pronounced as the time between states ∆t becomes
smaller and the state differences do not indicate the underlying
dynamics well.

We cannot increase the ∆t much as ∆t also increases the discretization
and complexity of the

underlying continuous-time dynamics, which can make the learning process
more difficult.

The training is done on data set comprising of s(t+1)-s(t) labels in a
general supervised learning with stochastic gradient descent method;
loss function is defined as follows:

![](.//media/image5.png)

2\>Action Selection

After learned dynamics the next task is to somehow choose “actions
sequence” which would maximize the return

![](.//media/image6.png)

![](.//media/image7.png)

![](.//media/image8.png)

General Model Based

Reinforcement learning algorithm with on policy data collection
something similar to DAGGER in imitation learning;

![](.//media/image9.png)

MBRL algorithm with Random Shooting method for planning:

![](.//media/image10.png)

**ALGORITHM IMPLEMENTED IN THIS WORK IS AS FOLLOWS:**

![](.//media/image11.png)

1.Same as above except for some fixed iteration (max\_iter; epochs)

2.Instead of stochastic gradient descent use mini batch gradient descent
(with train\_batch\_size)

3.number of gradient steps to optimize in this work is also fixed (
num\_agent\_train\_steps\_per\_iter

)

4\.**Ensemble learning: train multiple feed forward neural networks
(ff\_model) for model prediction to minimize the loss : Idea is that
multiple neural networks with different weights and trained on different
data sets will produce the more robust and more informed choices in
terms of choosing actions**

5.select the action using **MPC POLICY and Random shooting method **

**5.a\>**generate “n” sequence of **<span class="underline">random
action</span>** of some steps (mpc\_horizon) we are currently hoping
that among this “n” sequence of random action , one sequence will
produce maximum reward.

5**.b\> Predict** the arrived states after taking each action in a
sequence using ff\_model, and calculate the reward as well of being in
that state (using file in envs folder)

Calculate the total reward obtained from that sequence ; we will have
“n” such rewards

**5.c calculate mean\_across\_ensembles** and then choose the sequence
having maximum reward , and from the sequence choose the first action to
actually take (MPC planning)

**6.**execute this action record the next state and reward obtained**:
If our model prediction neural net is correct then generated next state
will be according to the ff\_model and thus will generate the maximum
REWARD.**

\*eqn2=Loss function as defined above

\*eqn4 same as eqn6

**RESULT of variation of hyperparameters:**

![](.//media/image12.png)

![](.//media/image13.png)
