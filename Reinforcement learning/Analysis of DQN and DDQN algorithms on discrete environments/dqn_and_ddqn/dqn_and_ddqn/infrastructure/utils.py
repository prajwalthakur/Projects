import numpy as np
import time

############################################
############################################

def sample_trajectory(env, policy, max_path_length, render=False, render_mode=('rgb_array')):

    # TODO: GETTHIS from HW2

    # initialize env for the beginning of a new rollout
    ob = env.reset()
    obs, acs, rewards, next_obs, terminals, image_obs = [], [], [], [], [], []
    steps = 0
    while True:

        # render image of the simulated env
        if render:
            if 'rgb_array' in render_mode:
                if hasattr(env, 'sim'):
                    if 'track' in env.env.model.camera_names:
                        image_obs.append(env.sim.render(camera_name='track', height=500, width=500)[::-1])
                    else:
                        image_obs.append(env.sim.render(height=500, width=500)[::-1])
                else:
                    image_obs.append(env.render(mode=render_mode))
            if 'human' in render_mode:
                env.render(mode=render_mode)
                time.sleep(env.model.opt.timestep)

        # use the most recent ob to decide what to do
        obs.append(ob)
        ac = policy.get_action(ob) # TODO: GETTHIS from HW1
        #print("ac",ac)
        ac = ac[0]
        acs.append(ac)

        # take that action and record results
        #print("action=",ac)
        ob, rew, done, _ = env.step(ac)

        # record result of taking that action
        steps += 1
        next_obs.append(ob)
        rewards.append(rew)

        # End the rollout if the rollout ended 
        # Note that the rollout can end due to done, or due to max_path_length
        if done==True or steps==max_path_length:
            rollout_done = 1 
            # HINT: this is either 0 or 1
        else:
                rollout_done=0
        terminals.append(rollout_done)
        
        if rollout_done: 
            break

    return Path(obs, image_obs, acs, rewards, next_obs, terminals)




def sample_trajectories(env, policy, min_timesteps_per_batch, max_path_length, render=False, render_mode=('rgb_array')):

    # TODO: GETTHIS from HW1 or HW2
    #this would run for n_itr=200 ; total dataset = 64*200 samples
    #MIN_Timesteps_per_batch=I should say this maximum steps that need to be taken for one batch , max path length is 
    #the maximum path that can be achieved in a single go
    timesteps_this_batch = 0
    paths = []
    while timesteps_this_batch < min_timesteps_per_batch:
        path=sample_trajectory(env, policy, max_path_length, render, render_mode)
        paths.append(path)
        timesteps_this_batch+=get_pathlength(path)
    return paths, timesteps_this_batch #ideally timesteps_this_batch should be constant for every batch but this  can vary 


def sample_n_trajectories(env, policy, ntraj, max_path_length, render=False, render_mode=('rgb_array')):
    
    # TODO: GETTHIS from HW1 or HW2
    paths=[]
    for _ in range(ntraj):
        paths.append(sample_trajectory(env, policy,max_path_length, render, render_mode))
    return paths


############################################
############################################

def Path(obs, image_obs, acs, rewards, next_obs, terminals):
    """
        Take info (separate arrays) from a single rollout
        and return it in a single dictionary
    """
    if image_obs != []:
        image_obs = np.stack(image_obs, axis=0)
    return {"observation" : np.array(obs, dtype=np.float32),
            "image_obs" : np.array(image_obs, dtype=np.uint8),
            "reward" : np.array(rewards, dtype=np.float32),
            "action" : np.array(acs, dtype=np.float32),
            "next_observation": np.array(next_obs, dtype=np.float32),
            "terminal": np.array(terminals, dtype=np.float32)}


def convert_listofrollouts(paths):
    """
        Take a list of rollout dictionaries
        and return separate arrays,
        where each array is a concatenation of that array from across the rollouts
    """
    observations = np.concatenate([path["observation"] for path in paths])
    actions = np.concatenate([path["action"] for path in paths])
    next_observations = np.concatenate([path["next_observation"] for path in paths])
    terminals = np.concatenate([path["terminal"] for path in paths])
    concatenated_rewards = np.concatenate([path["reward"] for path in paths])
    unconcatenated_rewards = [path["reward"] for path in paths]
    return observations, actions, next_observations, terminals, concatenated_rewards, unconcatenated_rewards

############################################
############################################

def get_pathlength(path):
    return len(path["reward"])
