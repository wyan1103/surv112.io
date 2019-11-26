import numpy as np

'''
This is not actually used for anything, but may be in the future.
'''


def ReLU(x):
    return np.maximum(0, x)

def Sigmoid(x):
    return 1 / (1 + np.exp(-x))

class Net:
    def __init__(self, input, output):
        self.input = input
        self.output = output
        self.expectedOutput = np.zeros((1, self.output.shape[1]))

        self.layers = 2
        self.dims = [9, 15, 1]

        self.params = {}
        self.cache = {}
        self.grad = {}

        self.loss = []
        self.learnRate = 0.005
        self.samples = self.output.shape[1]

    def init(self):
        np.random.seed(1)
        # w represents weights and b represents biases
        self.params['w1'] = np.random.randn(self.dims[1], self.dims[0]) / np.sqrt(self.dims[0])
        self.params['b1'] = np.zeros((self.dims[1], 1))
        self.params['w2'] = np.random.randn(self.dims[2], self.dims[1]) / np.sqrt(self.dims[1])
        self.params['b2'] = np.zeros((self.dims[2], 1))


    def forwardProp(self):
        # z represents output sums and a represents output of activation functions
        z1 = self.params['w1'].dot(self.input) + self.params['b1']
        a1 = ReLU(z1)
        self.cache['z1'] = z1
        self.cache['a1'] = a1

        z2 = self.params['w2'].dot(self.input) + self.params['b2']
        a2 = ReLU(z2)
        self.cache['z2'] = z2
        self.cache['a2'] = a2

        self.expectedOutput = a2
        # loss = self.nloss(a2)
        return self.expectedOutput

