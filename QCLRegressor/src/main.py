import qsharp
#import azure.quantum

from typing import List, Optional, Tuple
from numpy.typing import NDArray

import numpy as np
from numpy.random import default_rng
import matplotlib.pyplot as plt

from sklearn.metrics import mean_squared_error

from scipy.optimize import minimize

qsharp.init(project_root = './QCLRegressor')

n_qubit = 4
depth = 2
param_size = 32
seed = 0
n_shots = 100
#n_shots = 10

# maxiter = 2000
# maxiter = 1000
maxiter = 100
#maxiter = 2

def _predict_inner(
    x_scaled: NDArray[np.float_], theta: List[float]
) -> NDArray[np.float_]:
    res = []
    for x in x_scaled:
        # qsharpをshotで呼び出してもよいが遅いので、qsharp側でループ回す
        # x_scaledごとqsharpで実行する方がよいかもしれない
        theta_str = ", ".join([str(t) for t in theta])
        theta_str = f"[{theta_str}]"
        result = qsharp.run(f"QCL.Predict({n_qubit}, {depth}, {n_shots}, {x}, {theta_str})", shots=1)
        #print("result:", result)
        result_value = result[0][0] / n_shots
        #print("result_value:", result_value)
        res.append(result_value)

    return np.array(res)


def predict(x_test: NDArray[np.float_], theta: List[float]) -> NDArray[np.float_]:
    y_pred = _predict_inner(x_test, theta)
    return y_pred


def cost_func(
    theta: List[float],
    x_scaled: NDArray[np.float_],
    y_scaled: NDArray[np.float_],
) -> float:
    y_pred = _predict_inner(x_scaled, theta)
    cost = mean_squared_error(y_pred, y_scaled)
    return cost


iter = 0


def callback(xk):
    global iter
    # print("callback {}: xk={}".format(iter, xk))
    iter += 1


def run(
    theta: List[float],
    x: NDArray[np.float_],
    y: NDArray[np.float_],
    maxiter: Optional[int],
) -> Tuple[float, List[float]]:
    result = minimize(
        cost_func,
        theta,
        args=(x, y),
        method="Nelder-Mead",
        options={"maxiter": maxiter},
        callback=callback,
    )
    loss = result.fun
    theta_opt = result.x
    return loss, theta_opt


def fit(
    x_train: NDArray[np.float_],
    y_train: NDArray[np.float_],
    maxiter_or_lr: Optional[int] = None,
) -> Tuple[float, List[float]]:
    rng = default_rng(seed)
    theta_init = []
    for _ in range(param_size):
        theta_init.append(2.0 * np.pi * rng.random())

    return run(
        theta_init,
        x_train,
        y_train,
        maxiter_or_lr,
    )


def generate_noisy_sine(x_min, x_max, num_x):
    rng = default_rng(0)
    x_train = [[rng.uniform(x_min, x_max)] for _ in range(num_x)]
    y_train = [np.sin(np.pi * x[0]) for x in x_train]
    mag_noise = 0.01
    y_train += mag_noise * rng.random(num_x)
    # return np.array(x_train), np.array(y_train)
    return np.array(x_train).flatten(), np.array(y_train)


x_min = -1.0
x_max = 1.0
num_x = 80
x_train, y_train = generate_noisy_sine(x_min, x_max, num_x)
x_test, y_test = generate_noisy_sine(x_min, x_max, num_x)


opt_loss, opt_params = fit(x_train, y_train, maxiter)
print("trained parameters", opt_params)
print("loss", opt_loss)

y_pred = predict(x_test, opt_params)

plt.plot(x_test, y_test, "o", label="Test")
plt.plot(
    np.sort(np.array(x_test).flatten()),
    np.array(y_pred)[np.argsort(np.array(x_test).flatten())],
    label="Prediction",
)
plt.legend()
# plt.show()
plt.savefig("qclr-qdk.png")
