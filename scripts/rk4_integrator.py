from drone import Drone

class RK4():
    def __init__(self, drone, step_size):
        super(RK4, self).__init__()
        self.h = step_size
        self.drone = drone

    def step(self, x_k, t_k):
        temp_k1 = [0] * len(x_k)
        temp_k2 = [0] * len(x_k)
        temp_k3 = [0] * len(x_k)
        output = [0] * len(x_k)

        k1 = self.drone.ode(x_k, t_k)
        for i in range(len(x_k)):
            temp_k1[i] = x_k[i] + self.h * k1[i]/2

        k2 = self.drone.ode(temp_k1, t_k + self.h/2)
        for i in range(len(x_k)):
            temp_k2[i] = x_k[i] + self.h * k2[i]/2
        
        k3 = self.drone.ode(temp_k2, t_k + self.h/2)
        for i in range(len(x_k)):
            temp_k3[i] = x_k[i] + self.h * k3[i]

        k4 = self.drone.ode(temp_k3, t_k + self.h)
        for i in range(len(x_k)):
            output[i] = x_k[i] + self.h/6 * (k1[i] + 2*k2[i] + 2*k3[i] + k4[i])
        self.drone.states = output
        return output