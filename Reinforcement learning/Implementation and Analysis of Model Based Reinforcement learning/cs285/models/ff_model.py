#feed forward neural network
import tensorflow as tf

from .base_model import BaseModel
from cs285.infrastructure.utils import normalize, unnormalize
from cs285.infrastructure.tf_utils import build_mlp


class FFModel(BaseModel):

    def __init__(self, sess, ac_dim, ob_dim, n_layers, size, learning_rate=0.001, scope='dyn_model'):
        super(FFModel, self).__init__()

        # init vars
        # self.env = env
        self.sess = sess
        self.ac_dim = ac_dim
        self.ob_dim = ob_dim
        self.n_layers = n_layers
        self.size = size
        self.learning_rate = learning_rate
        self.scope = scope

        # build TF graph
        with tf.variable_scope(self.scope, reuse=tf.AUTO_REUSE):
            self.build_graph()
        self._train_op()

    #############################

    def build_graph(self):
        self._placeholders()
        self._forward_pass()

    def _placeholders(self):

        self.obs_pl = tf.placeholder(shape=[None, self.ob_dim], name="ob", dtype=tf.float32)
        self.acs_pl = tf.placeholder(shape=[None, self.ac_dim], name="ac", dtype=tf.float32)
        self.delta_labels = tf.placeholder(shape=[None, self.ob_dim], name="labels", dtype=tf.float32)

        self.obs_mean_pl = tf.placeholder(shape=[self.ob_dim], name="obs_mean", dtype=tf.float32)
        self.obs_std_pl = tf.placeholder(shape=[self.ob_dim], name="obs_std", dtype=tf.float32)
        self.acs_mean_pl = tf.placeholder(shape=[self.ac_dim], name="acs_mean", dtype=tf.float32)
        self.acs_std_pl = tf.placeholder(shape=[self.ac_dim], name="acs_std", dtype=tf.float32)
        self.delta_mean_pl = tf.placeholder(shape=[self.ob_dim], name="delta_mean", dtype=tf.float32)
        self.delta_std_pl = tf.placeholder(shape=[self.ob_dim], name="delta_std", dtype=tf.float32)

    def _forward_pass(self):
        # normalize input data to mean 0, std 1
        obs_unnormalized = self.obs_pl
        acs_unnormalized = self.acs_pl
        # using the normalize function d in infrastructure.utils for the following two lines
        obs_normalized = normalize(obs_unnormalized,self.obs_mean_pl,self.obs_std_pl)# d obs_normalized using obs_unnormalized,and self.obs_mean_pl and self.obs_std_pl
        acs_normalized = normalize(acs_unnormalized,self.acs_mean_pl,self.acs_std_pl)#  d acs_normalized using acs_unnormalized and self.acs_mean_pl and self.acs_std_pl

        # predicted change in obs
        concatenated_input = tf.concat([obs_normalized, acs_normalized], axis=1)
        # prefix delta is used in the variable below to denote changes in state, i.e. (s'-s)
        #self.delta_pred_normalized = build_mlp function and the concatenated_input above to  a neural network that predicts unnormalized delta states (i.e. change in state)
        self.delta_pred_normalized=build_mlp(concatenated_input,self.ob_dim, self.scope, self.n_layers, self.size)
       # self.delta_pred_unnormalized = Unnormalizing the the delta_pred above using the unnormalize function, and self.delta_mean_pl and self.delta_std_pl
        self.delta_pred_unormalized=unnormalize(self.delta_pred_normalized, self.delta_mean_pl , self.delta_std_pl)
       # self.next_obs_pred =Predicting next observation using current observation and delta prediction (not that next_obs here is unnormalized)
        self.next_obs_pred=obs_unnormalized+self.delta_pred_unormalized




    def _train_op(self):

        # normalize the labels
        self.delta_labels_normalized = normalize(self.delta_labels,self.delta_mean_pl,self.delta_std_pl) # normalized version of delta_labels using self.delta_labels (which are unnormalized), and self.delta_mean_pl and self.delta_std_pl

        # compared predicted deltas to labels (both should be normalized)
        self.loss=tf.losses.mean_squared_error(self.delta_labels_normalized,self.delta_pred_normalized)#  a loss function that takes as input normalized versions of predicted change in state and ground truth change in state
        self.train_op = tf.train.AdamOptimizer(self.learning_rate).minimize(self.loss)#  a train_op to minimize the loss d above. Adam optimizer will work well.

    #############################

    def get_prediction(self, obs, acs, data_statistics):
        if len(obs.shape)>1:
            observations = obs
            actions = acs
        else:
            observations = obs[None]
            actions = acs [None]
        feed_dict = {
                self.obs_pl:observations,
                self.acs_pl:actions,
                self.delta_mean_pl:data_statistics['delta_mean'],
                self.delta_std_pl:data_statistics['delta_std'],
                self.acs_mean_pl:data_statistics['acs_mean'],
                self.acs_std_pl:data_statistics['acs_std'],
                self.acs_mean_pl:data_statistics['acs_mean'],
                self.obs_mean_pl:data_statistics['obs_mean'],
                self.obs_std_pl:data_statistics['obs_std']
            }
        return self.sess.run(self.next_obs_pred,feed_dict=feed_dict) # Run model prediction on the given batch of data

    def update(self, observations, actions, next_observations, data_statistics):
        # train the model
        feed_dict = {
                self.obs_pl:observations,
                self.acs_pl:actions,
                self.acs_mean_pl:data_statistics['acs_mean'],
                self.acs_std_pl:data_statistics['acs_std'],
                self.acs_mean_pl:data_statistics['acs_mean'],
                self.obs_mean_pl:data_statistics['obs_mean'],
                self.obs_std_pl:data_statistics['obs_std'],
                self.delta_labels:next_observations-observations,
                self.delta_mean_pl:data_statistics['delta_mean'],
                self.delta_std_pl:data_statistics['delta_std']
            }

        """
        self.data_statistics = {'obs_mean': np.mean(self.replay_buffer.obs, axis=0),
                                'obs_std': np.std(self.replay_buffer.obs, axis=0),
                                'acs_mean': np.mean(self.replay_buffer.acs, axis=0),
                                'acs_std': np.std(self.replay_buffer.acs, axis=0),
                                'delta_mean': np.mean(
                                    self.replay_buffer.next_obs - self.replay_buffer.obs,
                                    axis=0),
                                'delta_std': np.std(
                                    self.replay_buffer.next_obs - self.replay_buffer.obs,
                                    axis=0),
                                }
        self.obs_pl = tf.placeholder(shape=[None, self.ob_dim], name="ob", dtype=tf.float32)
        self.acs_pl = tf.placeholder(shape=[None, self.ac_dim], name="ac", dtype=tf.float32)
        self.delta_labels = tf.placeholder(shape=[None, self.ob_dim], name="labels", dtype=tf.float32)

        self.obs_mean_pl = tf.placeholder(shape=[self.ob_dim], name="obs_mean", dtype=tf.float32)
        self.obs_std_pl = tf.placeholder(shape=[self.ob_dim], name="obs_std", dtype=tf.float32)
        self.acs_mean_pl = tf.placeholder(shape=[self.ac_dim], name="acs_mean", dtype=tf.float32)
        self.acs_std_pl = tf.placeholder(shape=[self.ac_dim], name="acs_std", dtype=tf.float32)
        self.delta_mean_pl = tf.placeholder(shape=[self.ob_dim], name="delta_mean", dtype=tf.float32)
        self.delta_std_pl = tf.placeholder(shape=[self.ob_dim], name="delta_std", dtype=tf.float32)

        """


        _, loss =self.sess.run([self.train_op,self.loss],feed_dict=feed_dict) # Run the train_op here, and also return the loss being optimized (on this batch of data)
        return loss