import numpy as np
import matplotlib.pyplot as plt

class Game:
    def __init__ (self, u00, u01, u10, u11, utility_profiles = True,
        player_names = ['Player A', 'Player B'],
        A_action_names = ['action 0', 'action 1'],
        B_action_names = ['action 0', 'action 1']):
        """Two player game with actions 0 or 1 for each player.
        Enter payoffs for players A (row player, index 0) and B (column player, index 1)
        depending on action profiles. 
        uij: (utility to A, utility to B) if A takes action i and B takes action j
        
        Use utility_profile = False to instead have interpretation
        uij = (utility to Player i if i takes action J and -i takes 0, 
                    utility to Player i if i takes action J and -i takes 1)
        """
    
        
        if utility_profiles:
            # each pair represents payoffs to each player given an outcome
            self.payoffs00 = u00
            self.payoffs01 = u01
            self.payoffs10 = u10
            self.payoffs11 = u11
            
        else:
            # each pair represents possible payoff ot player given their action 
            self.Au0 = u00
            self.Au1 = u01
            self.Bu0 = u10
            self.Bu1 = u11

            self.payoffs00 = self.Au0[0], self.Bu0[0]
            self.payoffs01 = self.Au0[1], self.Bu1[0]
            self.payoffs10 = self.Au1[0], self.Bu0[1]
            self.payoffs11 = self.Au1[1], self.Bu1[1]
        
        
            
    def best_response(self, action_profile):
        """If multiple, this chooses the action already specified."""
        
        action_profile = str(action_profile[0]) + str(action_profile[1])
        payoffs = self.__dict__['payoffs'+action_profile]

        profile_list = list(action_profile) # convert for mutability
        
        br_profile = list()
        for player in [0,1]:
            action = action_profile[player]                
            deviation = 1 - int(action)

            profile_list = list(action_profile) # convert for mutability
            profile_list[player] = str(deviation)

            deviation_profile =  ''.join(profile_list)

            dev_payoffs = self.__dict__['payoffs'+deviation_profile]

            if dev_payoffs[player] > payoffs[player]:
                br = deviation
            else:
                br = action
            br_profile.append(br)
            
        return br_profile
    
    def nash(self):
        """Returns a set pure strategy nash equilibria."""
        
        equilibria = set()
        for action_profile in ['00', '01', '10', '11']:
            
            payoffs = self.__dict__['payoffs'+action_profile]
            
            is_equilibrium = True
            # consider deviations
            profile_list = list(action_profile) # convert for mutability
            for player in [0,1]: ### Simplify this with new best response method
                action = action_profile[player]                
                deviation = 1 - int(action)
        
                profile_list = list(action_profile) # convert for mutability
                profile_list[player] = str(deviation)
        
                deviation_profile =  ''.join(profile_list)
            
                dev_payoffs = self.__dict__['payoffs'+deviation_profile]
                
                if dev_payoffs[player] > payoffs[player]:
                    
                    is_equilibrium = False
                    
            # did equilibria survive
        
            
            if is_equilibrium:
                
                # rename
                renamed = ''
                for action, player in zip(action_profile, 'AB'):
                    new = player + action
                    renamed += new
                
                equilibria.add(renamed)
                
        return equilibria
                
    def table(self, ax = None, show_solution = True):
        
        if ax == None:
            ax = plt.gca()
            
        for point in ['00', '01', '10', '11']:
            
            # point is an aciton profile
            br = self.best_response(point)
            
            A_is_br = br[0] == point[0]
            B_is_br = br[1] == point[1]
            
            xy = - int(point[0]), int(point[1])
            
            index = 1
            
            location = xy[1], xy[0]
            
            rec = plt.Rectangle(location, width = -1, height = -1, facecolor = 'white', 
                                edgecolor = 'black',
                               linewidth= 2)
            ax.add_artist(rec)
            
            payoff = self.__dict__['payoffs'+point]
            sA, sB = str(payoff[0]),  str(payoff[1])
            bbox = None
            if show_solution:
                plt.rc('text', usetex=True)
                if A_is_br:
                    sA = r"\underline{" + str(payoff[0]) + r"}"
                if B_is_br:
                    sB = r"\underline{" + str(payoff[1]) + r"}"
                if A_is_br and B_is_br:
                    bbox = dict(facecolor = 'lightyellow',
                            edgecolor = 'black', alpha = 0.85)
                
            s = sA + ", " + sB
            ax.text(xy[1] - 0.5 , xy[0] - 0.5, s, va = 'center', ha = 'center',
                   size = 31, bbox = bbox) #, font = 'Courier New')
            
        ax.set_aspect('equal')
        ax.set_ylim(-2.05,0.05)
        ax.set_xlim(-1.05,1.05)
        
        # Label players and actions
        ax.text(-0.08, 0.5, "Player A", rotation = 90,
               transform = ax.transAxes, 
                ha = 'right', 
                va = 'center',
                size = 20)
        
        ax.text(0, 0.25, "action 1", rotation = 90,
               transform = ax.transAxes, 
                ha = 'right', 
                va = 'center',
                size = 12)
        
        ax.text(0, 0.75, "action 0", rotation = 90,
               transform = ax.transAxes, 
                ha = 'right', 
                va = 'center',
                size = 12)
        
        ax.text(0.5, 1.08, "Player B", rotation = 0,
               transform = ax.transAxes, 
                ha = 'center', 
                va = 'bottom',
                size = 20)
        
        ax.text(0.75, 1, "action 1", rotation = 0,
               transform = ax.transAxes, 
                ha = 'center', 
                va = 'bottom',
                size = 12)
        
        ax.text(0.25, 1, "action 0", rotation = 0,
               transform = ax.transAxes, 
                ha = 'center', 
                va = 'bottom',
                size = 12)
        
        ax.axis('off')
                    

        
    def weakly_dominant_strategies(self, players = ['A','B']):
        
        players = [x.lower() for x in players]
        
        a_doms = set()
        b_doms = set()
        
        if 'a' in players:
            
            # does 0 dominate 1
            
            dominates0 = (self.payoffs00[0] >= self.payoffs10[0]) and (self.payoffs01[0] >= self.payoffs11[0])
            dominates1 = (self.payoffs00[0] <= self.payoffs10[0]) and (self.payoffs01[0] <= self.payoffs11[0])
            
            if dominates0:
                a_doms.add(0)
            if dominates1:
                a_doms.add(1)
           
        if 'b' in players:
            
            # does 0 dominate 1
            
            dominates0 = (self.payoffs00[1] >= self.payoffs01[1]) and (self.payoffs10[1] >= self.payoffs11[1])
            dominates1 = (self.payoffs00[1] <= self.payoffs01[1]) and (self.payoffs10[1] <= self.payoffs11[1])
            
            if dominates0:
                b_doms.add(0)
            if dominates1:
                b_doms.add(1)
        
        
        
        return {'A': a_doms, "B": b_doms}
        
