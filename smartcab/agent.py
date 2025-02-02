import random
from numpy.random import choice
import math
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator

class LearningAgent(Agent):
    """ An agent that learns to drive in the Smartcab world.
        This is the object you will be modifying. """

 
    def __init__(self, env, learning=False, epsilon=1.0, alpha=0.5):
        """ Initialize the learning agent and necessary parameters. """ 
        
        super(LearningAgent, self).__init__(env)     # Set the agent in the evironment 
        self.planner = RoutePlanner(self.env, self)  # Create a route planner
        self.valid_actions = self.env.valid_actions  # The set of valid actions

        # Set parameters of the learning agent
        self.learning = learning # Whether the agent is expected to learn
        self.Q = dict()          # Create a Q-table which will be a dictionary of tuples
        self.epsilon = epsilon   # Random exploration factor
        self.alpha = alpha       # Learning factor
        self.init_Qval=10        # Starting value of Q 
        # Note, the initial Q-value was set to 10 based upon this comment in the forums:
        # https://discussions.udacity.com/t/in-which-function-do-i-update-the-q-table-and-how/204911/9

        # Trial Number
        self.trial = 0
        
        # Epsilon Decay Function Parameters
        self.n = 350
        self.n2 = 200 #midpoint for shifted sigmoid decay function (not used otherwise)
        self.epsilon_val_at_n = 0.0001
        self.exploration_type = 'sigmoid_shift'
        
        #Build exploration factor functions
        self.exploration_functions()


    def exploration_functions(self):
        """ Define exploration factor functions and parameters. """
        
        def linear(self):
            self.a = (1-self.epsilon_val_at_n)/self.n
            self.epsilon = 1 - self.a*self.trial
            
        def exponential(self):
            #Exponential (a^t equivalent to exp(-at) for this choice of a)
            #Ok res with n=200, epsilon_val_at_n=0.05, tolerance=0.001, alpha=0.04
            self.a = math.log(self.epsilon_val_at_n)/self.n
            self.epsilon = math.exp(self.a*self.trial)
        
        def exponential2(self):
            #Exponential (a^t equivalent to exp(-at) for this choice of a)
            #Ok res with n=200, epsilon_val_at_n=0.05, tolerance=0.001, alpha=0.04
            self.a = math.log(self.epsilon_val_at_n)/self.n
            self.epsilon = 0.4*math.exp(self.a*self.trial)
        
        def rational_linear(self):
            #Rational (Linear Denominator)
            self.a = (1.0-self.epsilon_val_at_n)/((self.n-1.0)*self.epsilon_val_at_n)
            self.b = 1.0-self.a
            self.epsilon = 1/(self.a*self.trial + self.b)
            
        def rational_polynomial(self):
            #Rational (Polynomial Denominator)
            self.a = (1-self.epsilon_val_at_n)/((self.n**2-1)*self.epsilon_val_at_n)
            self.b = 1-self.a
            self.epsilon = 1/(self.a*(self.trial**2) + self.b)
        
        def sigmoid(self):
            #Logistic
            self.a = math.log(((self.epsilon_val_at_n)**2)
                        /((1-self.epsilon_val_at_n)**2)) / (self.n-1.0)
            self.b = math.log((1.0-self.epsilon_val_at_n)/self.epsilon_val_at_n) - self.a
            self.epsilon = 1.0-1.0/(1.0+math.exp(self.a*self.trial+self.b))
        
        def sigmoid_shift(self):
            #Logistic
            self.a = (math.log((self.epsilon_val_at_n) /(1-self.epsilon_val_at_n)) / 
                     (self.n-self.n2))
            self.b = -self.a * self.n2
            self.epsilon = 1.0-1.0/(1.0+math.exp(self.a*self.trial+self.b))
        
        # Store in dict to facilitate switching between functions
        self.exploration_functions = {
            'linear': linear,
            'exponential': exponential,
            'exponential2': exponential2,
            'rational_linear': rational_linear,
            'rational_polynomial': rational_polynomial,
            'sigmoid': sigmoid,
            'sigmoid_shift': sigmoid_shift
        }


    def get_epsilon(self):
        """ Choose designated exploration factor function and calculate 
            epsilon """
        self.exploration_functions[self.exploration_type](self)         
  
    
    def reset(self, destination=None, testing=False):
        """ The reset function is called at the beginning of each trial.
            'testing' is set to True if testing trials are being used
            once training trials have completed. """ 

        # Select the destination as the new location to route to
        self.planner.route_to(destination)
        
        # Set testing learning rate and exploration factor
        if testing == True:
            self.alpha = 0
            self.epsilon = 0
        else:
            self.get_epsilon()
            self.trial += 1

        return None


    def createQ(self, state):
        """ The createQ function is called when a state is generated by the agent. """

        # When learning, check if the 'state' is not in the Q-table
        # If it is not, create a new dictionary for that state
        #   Then, for each action available, set the initial Q-value to 0.0
        #   For each action, set the Q-value for the state-action pair to 0
        if state not in self.Q.keys():
            action_names = [str(a) for a in self.valid_actions]
            self.Q[state] = {}
            for a in action_names:
                self.Q[state][a] = self.init_Qval #defined in init()
        return


    def build_state(self):
        """ The build_state function is called when the agent requests data from the 
            environment. The next waypoint, the intersection inputs, and the deadline 
            are all features available to the agent. """

        # Collect data about the environment
        waypoint = self.planner.next_waypoint() # The next waypoint 
        inputs = self.env.sense(self)           # Visual input - intersection light and traffic
        deadline = self.env.get_deadline(self)  # Remaining deadline


        # Set 'state' as a tuple of relevant data for the agent        
        state = (waypoint,
                inputs['light'],
                inputs['oncoming'])

        # When learning, check if the state is in the Q-table
        #   If it is not, create a dictionary in the Q-table for the current 'state'
        #   For each action, set the Q-value for the state-action pair to 0
        if self.learning == True: 
            self.createQ(state)
        
        return state


    def get_maxQ(self, state):
        """ The get_action_with_maxQ function is called when the agent is asked to find the
            maximum Q-value of all actions based on the 'state' the smartcab is in. """

        # Calculate the maximum Q-value of all actions for a given state
        maxQ = max(self.Q[state].values())

        return maxQ 
        
    def get_best_action_set(self, state):
        """ Return any actions for a given state with Q=maxQ"""

        # Calculate the maximum Q-value of all actions for a given state
        action_set = filter(lambda a: self.Q[state][a]==self.get_maxQ(state), 
                            self.Q[state].keys())
        return action_set 


    def choose_action(self, state):
        """ The choose_action function is called when the agent is asked to choose
            which action to take, based on the 'state' the smartcab is in. """

        # Set the agent state and default action
        self.state = state
        self.next_waypoint = self.planner.next_waypoint()
        action = None
        
        # Choose an action
        if self.learning == False:
            # When not learning, choose a random action
            action = random.choice(self.valid_actions)
        else:
            # When learning, choose an action with the highest Q-value for the current state
            #   Otherwise, choose a random action with probability 'epsilon' 
            if random.random() > self.epsilon: 
                #exploit
                #return key(s) associated with maxQ, then choose one of the optimal actions
                action = random.choice(self.get_best_action_set(state))
            else: 
                #explore
                
                #uniform weighted random selection
                #action = random.choice(self.valid_actions)
                
                #softmax weighted random selection
                #see Question 7 "Additional Improvements" for explanation/references
                scale = sum([math.exp(self.Q[state][a]) for a in self.Q[state]])
                action_probs = [(a,math.exp(self.Q[state][a])/scale) for a in self.Q[state]]
                action = choice([a[0] for a in action_probs],p=[a[1] for a in action_probs])
                
            action = None if action == 'None' else action
 
        return action


    def learn(self, state, action, reward):
        """ The learn function is called after the agent completes an action and
            receives a reward. This function does not consider future rewards 
            when conducting learning. """

        # When learning, implement the value iteration update rule
        #   Use only the learning rate 'alpha' (do not use the discount factor 'gamma')
        print state, action, self.Q[state]
        Qval = self.Q[state][str(action)] 
        if Qval == self.init_Qval:
            self.Q[state][str(action)] = reward #on 1st trial reward is best information
        else:
            self.Q[state][str(action)] = (1.0-self.alpha)*Qval + self.alpha*reward
        return


    def update(self):
        """ The update function is called when a time step is completed in the 
            environment for a given trial. This function will build the agent
            state, choose an action, receive a reward, and learn if enabled. """

        state = self.build_state()          # Get current state
        self.createQ(state)                 # Create 'state' in Q-table
        action = self.choose_action(state)  # Choose an action
        reward = self.env.act(self, action) # Receive a reward
        self.learn(state, action, reward)   # Q-learn

        return
        

def run():
    """ Driving function for running the simulation. 
        Press ESC to close the simulation, or [SPACE] to pause the simulation. """
    
    #Use random seed for results displayed in report
    random.seed(1902)
    
    ##############
    # Create the environment
    # Flags:
    #   verbose     - set to True to display additional output from the simulation
    #   num_dummies - discrete number of dummy agents in the environment, default is 100
    #   grid_size   - discrete number of intersections (columns, rows), default is (8, 6)
    env = Environment()
    
    ##############
    # Create the driving agent
    # Flags:
    #   learning   - set to True to force the driving agent to use Q-learning
    #    * epsilon - continuous value for the exploration factor, default is 1
    #    * alpha   - continuous value for the learning rate, default is 0.5
    agent = env.create_agent(LearningAgent,learning=True,alpha=0.4)
    
    ##############
    # Follow the driving agent
    # Flags:
    #   enforce_deadline - set to True to enforce a deadline metric
    env.set_primary_agent(agent,enforce_deadline=True)

    ##############
    # Create the simulation
    # Flags:
    #   update_delay - continuous time (in seconds) between actions, default is 2.0 seconds
    #   display      - set to False to disable the GUI if PyGame is enabled
    #   log_metrics  - set to True to log trial and simulation results to /logs
    #   optimized    - set to True to change the default log file name
    sim = Simulator(env,update_delay=0.001,display=False,log_metrics=True,optimized=True)

    ##############
    # Run the simulator
    # Flags:
    #   tolerance  - epsilon tolerance before beginning testing, default is 0.05 
    #   n_test     - discrete number of testing trials to perform, default is 0
    sim.run(n_test=100,tolerance=0.0001)


if __name__ == '__main__':
    run()
    

