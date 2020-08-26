import rospy
import numpy as np
from std_msgs.msg import Float32MultiArray
from Model import Model
from . import PDController
from sensor_msgs.msg import JointState
from . import ControllerBase
from ilqr import iLQR, RecedingHorizonController
from ilqr.cost import QRCost, PathQRCost, PathQsRCost
from GaitAnaylsisToolkit.LearningTools.Runner import TPGMMRunner
from ilqr.dynamics import AutoDiffDynamics, BatchAutoDiffDynamics, FiniteDiffDynamics
import matplotlib.pyplot as plt

class LQRController(ControllerBase.BaseController):

    def __init__(self, model, runner):
        """

        :param model:
        :param kp:
        :param kd:
        """
        super(LQRController, self).__init__(model)
        self.runner = runner
        self.setup()

    def setup(self):

        J_hist = []

        def on_iteration(iteration_count, xs, us, J_opt, accepted, converged):
            J_hist.append(J_opt)
            info = "converged" if converged else ("accepted" if accepted else "failed")
            print("iteration", iteration_count, info, J_opt)

        def f(x, u, i):
            y = Model.runge_integrator(self._model.get_rbdl_model(), x, 0.01, u)

            return np.array(y)

        dynamics = FiniteDiffDynamics(f, 12, 6)


        x_path = []
        u_path = []
        count = 0
        while count < self.runner.get_length():
            count += 1
            self.runner.step()
            u_path.append(self.runner.ddx.flatten().tolist())
            x = self.runner.x.flatten().tolist() + self.runner.dx.flatten().tolist()
            x_path.append(x)

        u_path = u_path[:-1]
        expSigma = self.runner.get_expSigma()
        size = expSigma[0].shape[0]
        Q = [np.zeros((size * 2, size * 2))] * len(expSigma)
        for ii in range(len(expSigma) - 2, -1, -1):
            Q[ii][:size, :size] = np.linalg.pinv(expSigma[ii])

        x0 = x_path[0]
        x_path = np.array(x_path)
        u_path = np.array(u_path)
        R = 0.00005 * np.eye(dynamics.action_size)
        #
        cost2 = PathQsRCost(Q, R, x_path=x_path, u_path=u_path)
        #
        # # Random initial action path.
        us_init = np.random.uniform(-1, 1, (99, dynamics.action_size))
        #
        J_hist = []
        ilqr = iLQR(dynamics, cost2, 99)
        self.xs, self.us = ilqr.fit(x0, us_init, on_iteration=on_iteration)
        plt.plot(self.xs[:,0])
        plt.show()

    def calc_tau(self, q=None, qd=None, qdd=None, other=None ):
        """

        :param q:
        :param qd:
        :param qdd:
        :return:
        """
        print(other)
        tau = np.append(self.us[int(other[0])], [0.0])
        print(tau)
        return tau