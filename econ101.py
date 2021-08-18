class Curve:

    def __init__ (self, a, b, inverse = True):
        
        if inverse:
            self.intercept = a
            self.slope = b
            
        else:
            self.slope = -1/b
            self.intercept = -a/b
            
    #def horizontal_shift(delta):
        
    def vertical_shift(self, delta):
        self.intercept += delta      
        

    def equilibrium(self, other_curve):
        """Returns a tuple (p, q)."""
        
        v1 = np.array([1, -self.slope])
        v2 = np.array([1, -other_curve.slope])
        
        b = self.intercept, other_curve.intercept

        A = np.matrix((v1, v2))
        b = np.matrix(b).T

        x = np.linalg.inv(A) * b
        x = x.squeeze()
        return x[0,0], x[0,1] # p, q