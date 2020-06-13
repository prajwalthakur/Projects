from .base_critic import BaseCritic
import tensorflow as tf
from dqn_and_ddqn.infrastructure.dqn_utils import minimize_and_clip, huber_loss
import pdb

class DQNCritic(BaseCritic):

    def __init__(self, sess, hparams, optimizer_spec, **kwargs):
        super().__init__(**kwargs)
        self.sess = sess
        self.env_name = hparams['env_name']
        self.ob_dim = hparams['ob_dim']

        if isinstance(self.ob_dim, int):
            self.input_shape = (self.ob_dim,)
        else:
            self.input_shape = hparams['input_shape']

        self.ac_dim = hparams['ac_dim']
        self.double_q = hparams['double_q']
        self.grad_norm_clipping = hparams['grad_norm_clipping']
        self.gamma = hparams['gamma']

        self.optimizer_spec = optimizer_spec
        self.define_placeholders()
        self._build(hparams['q_func'])

    def _build(self, q_func):

        #####################

        # q values, created with the placeholder that holds CURRENT obs (i.e., t)
        self.q_t_values = q_func(self.obs_t_ph, self.ac_dim, scope='q_func', reuse=False)
        self.q_t = tf.reduce_sum(self.q_t_values * tf.one_hot(self.act_t_ph, self.ac_dim), axis=1)

        #####################

        # target q values, created with the placeholder that holds NEXT obs (i.e., t+1)
        q_tp1_values = q_func(self.obs_tp1_ph, self.ac_dim, scope='target_q_func', reuse=False)
        

        if self.double_q:
            # You must fill this part for Q2 of the Q-learning potion of the homework.
            # In double Q-learning, the best action is selected using the Q-network that
            # is being updated, but the Q-value for this action is obtained from the
            # target Q-network. See page 5 of https://arxiv.org/pdf/1509.06461.pdf for more details.
            #TODO
            self.q_t_for_tp1_observation=q_func(self.obs_tp1_ph,self.ac_dim,scope='q_func',reuse=True)
           
            q_tp1=tf.boolean_mask(q_tp1_values,tf.one_hot(tf.argmax(self.q_t_for_tp1_observation,axis=1), self.ac_dim))
            #pdb.set_trace()
            #print(q_tp1)
        else:
            # q values of the next timestep
            q_tp1 = tf.reduce_max(q_tp1_values, axis=1)

        #####################

        # TODO calculate the targets for the Bellman error
        # HINT1: as you saw in lecture, this would be:
            #currentReward + self.gamma * qValuesOfNextTimestep * (1 - self.done_mask_ph)
        # HINT2: see above, where q_tp1 is defined as the q values of the next timestep
        # HINT3: see the defined placeholders and look for the one that holds current rewards
        
        target_q_t = self.rew_t_ph +self.gamma*q_tp1*(1-self.done_mask_ph)
        #pdb.set_trace() 
        #print(target_q_t.shape)
        
        target_q_t = tf.stop_gradient(target_q_t)  #making this constant

        #####################

        # TODO compute the Bellman error (i.e. TD error between q_t and target_q_t)
        # Note that this scalar-valued tensor later gets passed into the optimizer, to be minimized
        # HINT: use reduce mean of huber_loss (from infrastructure/dqn_utils.py) instead of squared error
        error=self.q_t-target_q_t
        
        self.total_error= tf.reduce_mean(huber_loss(error))

        #####################

        # TODO these variables should all of the 
        # variables of the Q-function network and target network, respectively
        # HINT1: see the "scope" under which thtf.GraphKeys.TRAINABLE_VARIABLESe variables were constructed in the lines at the top of this function
        # HINT2: use tf.get_collection to look for all variables under a certain scope
        q_func_vars = tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES,'q_func')
        target_q_func_vars = tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES,'target_q_func')

        #####################

        # train_fn will be called in order to train the critic (by minimizing the TD error)
        self.learning_rate = tf.placeholder(tf.float32, (), name="learning_rate")
        optimizer = self.optimizer_spec.constructor(learning_rate=self.learning_rate, **self.optimizer_spec.kwargs)
        self.train_fn = minimize_and_clip(optimizer, self.total_error,
                                          var_list=q_func_vars, clip_val=self.grad_norm_clipping)

        # update_target_fn will be called periodically to copy Q network to target Q network
        update_target_fn = []
        for var, var_target in zip(sorted(q_func_vars,        key=lambda v: v.name),
                                   sorted(target_q_func_vars, key=lambda v: v.name)):
            update_target_fn.append(var_target.assign(var))
        self.update_target_fn = tf.group(*update_target_fn)

    def define_placeholders(self):
        # set up placeholders
        # placeholder for current observation (or state)
        lander = self.env_name == 'LunarLander-v2'

        self.obs_t_ph = tf.placeholder(
            tf.float32 if lander else tf.uint8, [None] + list(self.input_shape))
        # placeholder for current action
        self.act_t_ph = tf.placeholder(tf.int32, [None])
        # placeholder for current reward
        self.rew_t_ph = tf.placeholder(tf.float32, [None])
        # placeholder for next observation (or state)
        self.obs_tp1_ph = tf.placeholder(
            tf.float32 if lander else tf.uint8, [None] + list(self.input_shape))
        # placeholder for end of episode mask
        # this value is 1 if the next state corresponds to the end of an episode,
        # in which case there is no Q-value at the next state; at the end of an
        # episode, only the current state reward contributes to the target, not the
        # next state Q-value (i.e. target is just rew_t_ph, not rew_t_ph + gamma * q_tp1)
        self.done_mask_ph = tf.placeholder(tf.float32, [None])

    def update(self, ob_no, next_ob_no, re_n, terminal_n):
        raise NotImplementedError
