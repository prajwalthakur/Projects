![](actor_critic_inverted_pendulum.png)

![](actor_critic_HalfCheetah_VS_inverted_pendulum.png)

In general when there is linear function estimator function to estimate
the Value function the stochastic gradient desecent with TD(0) converge,
but when we move towards the non linear function approximation with
TD(0) Bootstrap this method does not converge theoritically as well as
in practice.
