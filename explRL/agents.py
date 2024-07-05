# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/agents.ipynb.

# %% auto 0
__all__ = ['Policy', 'flexiblePolicy', 'RL', 'Agent', 'flexibleAgent']

# %% ../nbs/agents.ipynb 2
import numpy as np

# %% ../nbs/agents.ipynb 4
class Policy:
    '''This Policy Class specifies a general architecture. '''
    def __init__(self):
        self.theta = None
        self.actions = None
        self.pi = None



# %% ../nbs/agents.ipynb 5
class flexiblePolicy(Policy):
    '''This flexiblePolicy Class specifies a fully flexible policy with a set of basis functions 
    and a learnable set of weights. '''
    def __init__(self):
        super().__init__()
        self.omega = None   # vector of weights
        self.fk = None  # basis functions
        self.wParams = None # a vector of parameters used to specify nonlinear transformations of the weights
        self.integ = None    # an integrator signal used in the drift diffusion process to generate fixations


# %% ../nbs/agents.ipynb 6
class RL:
    '''This RL Class performs reinforcement learning: after taking an action, update parameters 
    based on feedback from the environment.
    '''
    def __init__(self,policy):
        self.policy = policy
        
    def chooseAction(self):
        pass
        return self.act
    
    def updateParams(self):
        pass
        return self.params

# %% ../nbs/agents.ipynb 7
class Agent:
    '''This Class specifies agents with a defined policy and reinforcement learning algorithm. '''
    def __init__(self,theta,goal,policy,rl,params):
        self.theta = theta   # current heading
        self.goal = goal
        self.policy = policy
        self.rl = rl
        self.params = params  # structure containing simulation parameters
        self.dx = None  # change in heading
        self.dt = None  # change in time 
        self.integ = None # an integrator signal used in the drift diffusion process to generate fixations
        
        
    def samplePolicy(self):
        raise NotImplementedError("Override me")

# %% ../nbs/agents.ipynb 8
class flexibleAgent(Agent):
    '''This Agent Class specifies agents using a fully flexible policy and reinforcement learning algorithm. '''
    def __init__(self):
        super().__init__()
        self.omega = None # vector of weights
        self.fk = None # basis functions       
        self.wParams = None # a vector of parameters used to specify nonlinear transformations of the weights

    def samplePolicy(self):
        '''samples a change in heading over a change in time to use in training'''
        
        nx       = self.params.nx
        thetaVec = np.linspace(0,2*np.pi,num=nx+1)
        ind      = np.argmin(np.square(self.theta-thetaVec[:-1]))

        # update integrator
        nu,pR      = self.convertParams(self.omega,self.fk[:,ind],self.wParams)
        self.integ = self.integ + np.random.normal(nu*self.params.delT,self.params.sigF*np.sqrt(self.params.delT))

        if self.integ > self.params.aF:
            #--------- SACCADE ----------#
            if self.flipCoin(pR):
                dir = 1
            else:
                dir = -1
    
            self.dx = np.multiply(np.multiply(dir,np.random.lognormal(self.params.muS,self.params.sigmaS)),96./360)
            self.dt = self.params.dtS
            self.integ = 0

        else:
            #--------- FIXATE ----------#
            self.dx = 0
            self.dt = 1
        
        self.dx = round(self.dx)
        self.dt = round(self.dt)

        return self.dx, self.dt, self.integ
        
    def convertParams(self):
        '''converts a vector of weights into behavioral control parameters (drift rates and turn biases)'''

        # See also: GETBASISFUNCTIONS

        nb = (np.size(self.omega))/2
        omegaF = self.omega[:nb+1].T
        omegaR = self.omega[nb+1:].T

        nuF = self.sigmoid(omegaF*self.fk,self.wParams[0],self.wParams[1],self.wParams[2])
        pR  = self.sigmoid(omegaR*self.fk,self.wParams[3],self.wParams[4],self.wParams[5])

        return nuF,pR,omegaF,omegaR
    
    def sigmoid(self,x,k,fmax,offset):
        ''' = FMAX/(1+exp(-K*X))-OFFSET generates a sigmoidal function with slope K, scale FMAX , and vertical shift OFFSET ''' 

        return np.divide(fmax,(1+np.exp(-k*x))) - offset

    def flipCoin(self,p):
        # samples from a Bernoulli process with probability P
        u = np.random.rand()
        if u < p:
            return True
        else:
            return False

