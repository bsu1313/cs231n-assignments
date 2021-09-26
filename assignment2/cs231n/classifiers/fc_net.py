from builtins import range
from builtins import object
import numpy as np

from ..layers import *
from ..layer_utils import *


class FullyConnectedNet(object):
    """Class for a multi-layer fully connected neural network.

    Network contains an arbitrary number of hidden layers, ReLU nonlinearities,
    and a softmax loss function. This will also implement dropout and batch/layer
    normalization as options. For a network with L layers, the architecture will be

    {affine - [batch/layer norm] - relu - [dropout]} x (L - 1) - affine - softmax

    where batch/layer normalization and dropout are optional and the {...} block is
    repeated L - 1 times.

    Learnable parameters are stored in the self.params dictionary and will be learned
    using the Solver class.
    """

    def __init__(
        self,
        hidden_dims,
        input_dim=3 * 32 * 32,
        num_classes=10,
        dropout_keep_ratio=1,
        normalization=None,
        reg=0.0,
        weight_scale=1e-2,
        dtype=np.float32,
        seed=None,
    ):
        """Initialize a new FullyConnectedNet.

        Inputs:
        - hidden_dims: A list of integers giving the size of each hidden layer.
        - input_dim: An integer giving the size of the input.
        - num_classes: An integer giving the number of classes to classify.
        - dropout_keep_ratio: Scalar between 0 and 1 giving dropout strength.
            If dropout_keep_ratio=1 then the network should not use dropout at all.
        - normalization: What type of normalization the network should use. Valid values
            are "batchnorm", "layernorm", or None for no normalization (the default).
        - reg: Scalar giving L2 regularization strength.
        - weight_scale: Scalar giving the standard deviation for random
            initialization of the weights.
        - dtype: A numpy datatype object; all computations will be performed using
            this datatype. float32 is faster but less accurate, so you should use
            float64 for numeric gradient checking.
        - seed: If not None, then pass this random seed to the dropout layers.
            This will make the dropout layers deteriminstic so we can gradient check the model.
        """
        self.normalization = normalization
        self.use_dropout = dropout_keep_ratio != 1
        self.reg = reg
        self.num_layers = 1 + len(hidden_dims)
        self.dtype = dtype
        self.params = {}

        ############################################################################
        # TODO: Initialize the parameters of the network, storing all values in    #
        # the self.params dictionary. Store weights and biases for the first layer #
        # in W1 and b1; for the second layer use W2 and b2, etc. Weights should be #
        # initialized from a normal distribution centered at 0 with standard       #
        # deviation equal to weight_scale. Biases should be initialized to zero.   #
        #                                                                          #
        # When using batch normalization, store scale and shift parameters for the #
        # first layer in gamma1 and beta1; for the second layer use gamma2 and     #
        # beta2, etc. Scale parameters should be initialized to ones and shift     #
        # parameters should be initialized to zeros.                               #
        ############################################################################
        # *****START OF YOUR CODE (DO NOT DELETE/MODIFY THIS LINE)*****

        self.params['W1'] = np.random.randn(input_dim, hidden_dims[0]) * weight_scale
        self.params['b1'] = np.zeros(hidden_dims[0])


        if self.normalization != None:
          self.params['gamma1'] = np.ones(hidden_dims[0])
          self.params['beta1'] = np.zeros(hidden_dims[0])
        
        hidden_num = len(hidden_dims)

        for i in range(hidden_num-1):
          IN = hidden_dims[i]
          OUT = hidden_dims[i+1]
          self.params['W'+str(i+2)] = np.random.randn(IN, OUT) * weight_scale
          self.params['b'+str(i+2)] = np.zeros(OUT)
          
          if self.normalization != None:
            self.params['gamma'+str(i+2)] = np.ones(OUT)
            self.params['beta'+str(i+2)] = np.zeros(OUT)
        
        self.params['W'+str(hidden_num+1)] = np.random.randn(hidden_dims[hidden_num-1], num_classes) * weight_scale
        self.params['b'+str(hidden_num+1)] = np.zeros(num_classes)


        # *****END OF YOUR CODE (DO NOT DELETE/MODIFY THIS LINE)*****
        ############################################################################
        #                             END OF YOUR CODE                             #
        ############################################################################

        # When using dropout we need to pass a dropout_param dictionary to each
        # dropout layer so that the layer knows the dropout probability and the mode
        # (train / test). You can pass the same dropout_param to each dropout layer.
        self.dropout_param = {}
        if self.use_dropout:
            self.dropout_param = {"mode": "train", "p": dropout_keep_ratio}
            if seed is not None:
                self.dropout_param["seed"] = seed

        # With batch normalization we need to keep track of running means and
        # variances, so we need to pass a special bn_param object to each batch
        # normalization layer. You should pass self.bn_params[0] to the forward pass
        # of the first batch normalization layer, self.bn_params[1] to the forward
        # pass of the second batch normalization layer, etc.
        self.bn_params = []
        if self.normalization == "batchnorm":
            self.bn_params = [{"mode": "train"} for i in range(self.num_layers - 1)]
        if self.normalization == "layernorm":
            self.bn_params = [{} for i in range(self.num_layers - 1)]

        # bn_params[1]["mode"] 두번째 레이어의 bn 파라미터 : 이런식으로 사용하는듯.
        # bn_params[1]["running_mean"] 두번째 레이어의 이동평균을 계산해서 저장하느 곳.
        # 일단 default로 mode를 train으로 지정하는듯.

        # Cast all parameters to the correct datatype.
        for k, v in self.params.items():
            self.params[k] = v.astype(dtype)
      

    def loss(self, X, y=None):
        """Compute loss and gradient for the fully connected net.
        
        Inputs:
        - X: Array of input data of shape (N, d_1, ..., d_k)
        - y: Array of labels, of shape (N,). y[i] gives the label for X[i].

        Returns:
        If y is None, then run a test-time forward pass of the model and return:
        - scores: Array of shape (N, C) giving classification scores, where
            scores[i, c] is the classification score for X[i] and class c.

        If y is not None, then run a training-time forward and backward pass and
        return a tuple of:
        - loss: Scalar value giving the loss
        - grads: Dictionary with the same keys as self.params, mapping parameter
            names to gradients of the loss with respect to those parameters.
        """
        X = X.astype(self.dtype)
        mode = "test" if y is None else "train"

        # Set train/test mode for batchnorm params and dropout param since they
        # behave differently during training and testing.
        if self.use_dropout:
            self.dropout_param["mode"] = mode
        if self.normalization == "batchnorm":
            for bn_param in self.bn_params:
                bn_param["mode"] = mode
        scores = None
        ############################################################################
        # TODO: Implement the forward pass for the fully connected net, computing  #
        # the class scores for X and storing them in the scores variable.          #
        #                                                                          #
        # When using dropout, you'll need to pass self.dropout_param to each       #
        # dropout forward pass.                                                    #
        #                                                                          #
        # When using batch normalization, you'll need to pass self.bn_params[0] to #
        # the forward pass for the first batch normalization layer, pass           #
        # self.bn_params[1] to the forward pass for the second batch normalization #
        # layer, etc.                                                              #
        ############################################################################
        # *****START OF YOUR CODE (DO NOT DELETE/MODIFY THIS LINE)*****

        affine_caches = [0]
        relu_caches = [0]
        bn_caches = [0]
        ln_caches =[0]
        drop_caches =[0]

        IN = X
        for i in range(1, self.num_layers):
          out1, affine_cache = affine_forward(IN, self.params['W'+str(i)], self.params['b'+str(i)])
          affine_caches.append(affine_cache)

          if self.normalization == 'batchnorm':
            out1, bn_cache = batchnorm_forward(out1, self.params['gamma'+str(i)], self.params['beta'+str(i)], self.bn_params[i-1])
            bn_caches.append(bn_cache)
          
          if self.normalization == 'layernorm':
            out1, ln_cache = layernorm_forward(out1, self.params['gamma'+str(i)], self.params['beta'+str(i)], self.bn_params[i-1])
            ln_caches.append(ln_cache)

          out2, relu_cache = relu_forward(out1)
          relu_caches.append(relu_cache)

          if self.use_dropout:
            out2, drop_cache = dropout_forward(out2, self.dropout_param)
            drop_caches.append(drop_cache)

          IN = out2
        
        score, affine_cache = affine_forward(IN, self.params['W'+str(self.num_layers)], self.params['b'+str(self.num_layers)])
        affine_caches.append(affine_cache)

        # *****END OF YOUR CODE (DO NOT DELETE/MODIFY THIS LINE)*****
        ############################################################################
        #                             END OF YOUR CODE                             #
        ############################################################################
        # If test mode return early.
        if mode == "test":
            return score
        loss, grads = 0.0, {}
        ############################################################################
        # TODO: Implement the backward pass for the fully connected net. Store the #
        # loss in the loss variable and gradients in the grads dictionary. Compute #
        # data loss using softmax, and make sure that grads[k] holds the gradients #
        # for self.params[k]. Don't forget to add L2 regularization!               #
        #                                                                          #
        # When using batch/layer normalization, you don't need to regularize the   #
        # scale and shift parameters.                                              #
        #                                                                          #
        # NOTE: To ensure that your implementation matches ours and you pass the   #
        # automated tests, make sure that your L2 regularization includes a factor #
        # of 0.5 to simplify the expression for the gradient.                      #
        ############################################################################
        loss, ds = softmax_loss(score, y)

        for i in range(1, self.num_layers+1):
          W = self.params['W'+str(i)]
          loss += np.sum(W*W) * 0.5 * self.reg

        dx, dw, db = affine_backward(ds, affine_caches[self.num_layers])
        grads['W'+str(self.num_layers)] = dw + self.reg* self.params['W'+str(self.num_layers)]
        grads['b'+str(self.num_layers)] = db

        dOUT = dx
        for i in range(self.num_layers-1, 0, -1):
          if self.use_dropout:
            dOUT = dropout_backward(dOUT, drop_caches[i])

          dout1 = relu_backward(dOUT, relu_caches[i])

          if self.normalization == 'batchnorm':
            dout1, dgamma, dbeta = batchnorm_backward(dout1, bn_caches[i])
            grads['gamma'+str(i)] = dgamma
            grads['beta'+str(i)] = dbeta

          if self.normalization == 'layernorm':
            dout1, dgamma, dbeta = layernorm_backward(dout1, ln_caches[i])
            grads['gamma'+str(i)] = dgamma
            grads['beta'+str(i)] = dbeta

          dx, dw, db = affine_backward(dout1, affine_caches[i])
          grads['W'+str(i)] = dw + self.reg* self.params['W'+str(i)]
          grads['b'+str(i)] = db
          dOUT = dx

        # *****END OF YOUR CODE (DO NOT DELETE/MODIFY THIS LINE)*****
        ############################################################################
        #                             END OF YOUR CODE                             #
        ############################################################################

        return loss, grads