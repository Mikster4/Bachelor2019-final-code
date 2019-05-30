#!/usr/bin/python3
import numpy
import sys

def rmse(t, tp):
    """ Computes the RMSE for two
    input arrays 't' and 'tp'.
    """

    # sanity check: both shapes have to be the same!
    assert tp.shape == tp.shape

    return numpy.sqrt(numpy.mean((t - tp)**2))

class LinearRegression():

    def __init__(self):
        pass

    def fit(self, X, t):
        # Computes the linear function.
        # X : matrix of n samples and m features
        # t : vector of n t-values

        # make sure that we have numpy arrays; also
        # reshape the array X to ensure that we have
        # a multidimensional numpy array (ndarray)
        X = numpy.array(X).reshape((X.shape[0], -1))
        t = numpy.array(t)

        ones = numpy.ones((len(X),1))
        X = numpy.concatenate((ones,X),axis=1)
        print(numpy.concatenate(X,t))

        xTx_inv = numpy.linalg.inv(numpy.dot(numpy.transpose(X),X))
        self.w = numpy.dot(numpy.dot(xTx_inv,numpy.transpose(X)),t)
        print(self.w)

    def predict(self, X):
        # Computes predictions for new points from the input variables.
        # X : matrix of n samples and m features

        # make sure that we have numpy arrays; also
        # reshape the array X to ensure that we have
        # a multidimensional numpy array (ndarray)
        X = numpy.array(X).reshape((X.shape[0], -1))

        ones = numpy.ones(len(X),1)
        X = numpy.concatenate(ones,X)

        predictions = numpy.dot(numpy.transpose(self.w),X)

        return predictions

if len(sys.argv) != 2:
    print("Usage: ./linreg.py path")

stress_data = numpy.loadtxt(sys.argv[1], delimiter=",")
X_train, t1_train = stress_data[:,:2], stress_data[:,2]
X2_train = X_train ** 2
print("X_train:")
print(X_train)
print("\nX2_train:")
print(X2_train)
print("\n")
X_train = numpy.concatenate((X_train,X2_train),axis=1)
print("NEW X_train:")
print(X_train)

model_all = LinearRegression()
model_all.fit(X_train[:,:], t1_train)

#plt.scatter(t_test, model_single.predict(X_test[:,0]))
