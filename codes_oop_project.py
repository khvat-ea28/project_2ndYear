

import numpy as np

# базовый актив
class asset():
    def __init__(self, S0):
        self.S0 = S0

    def price(self, t):
        pass

    def log_return(self, t):
        return np.log(self.price(t) / self.S0)

# банковский счет
class bank_account(asset):
    def __init__(self, B0, r):
        super().__init__(B0)
        self.r = r

    def price(self, t):
        return self.S0 * (1 + self.r) ** t

    def price_continuous(self, t):
        return self.S0 * np.exp(self.r * t)

# рисковый актив
class stock(asset):
    def __init__(self, S0, mu, sigma):
        super().__init__(S0)
        self.mu = mu
        self.sigma = sigma

    def price(self, t):
        W = np.random.randn() * np.sqrt(t)
        return self.S0 * np.exp((self.mu - self.sigma**2 / 2) * t + self.sigma * W)

    def price_path(self, T, n_steps):
        dt = T / n_steps
        prices = np.zeros(n_steps + 1)
        prices[0] = self.S0
        for i in range(1, n_steps + 1):
            W = np.random.randn() * np.sqrt(dt)
            prices[i] = prices[i-1] * np.exp(
                (self.mu - self.sigma**2 / 2) * dt + self.sigma * W
            )
        return prices

# портфель
class portfolio():
    def __init__(self, a, b, bank, risky):
        self.a = a
        self.b = b
        self.bank = bank
        self.risky = risky

    def value(self, t):
        pass

    def value_at(self, t):
        return self.value(t)

# статический портфель
class static_portfolio(portfolio):
    def __init__(self, a, b, bank, risky):
        super().__init__(a, b, bank, risky)

    def value(self, t):
        return self.a * self.bank.price(t) + self.b * self.risky.price(t)


# мультиактивный портфель
class multi_portfolio(portfolio):
    def __init__(self, a, b_list, bank, risky_list):
        super().__init__(a, b_list, bank, risky_list[0])
        self.b_list     = b_list
        self.risky_list = risky_list

    def value(self, t):
        result = self.a * self.bank.price(t)
        for b_i, s_i in zip(self.b_list, self.risky_list):
            result += b_i * s_i.price(t)
        return result

# условное требование
class contingent_claim():
    def __init__(self, K, T):
        self.strike = K
        self.maturity = T

    def payoff(self, S):
        pass

# деривативы
class forward_contract(contingent_claim):
    def __init__(self, K, T):
        super().__init__(K, T)

    def payoff(self, S):
        return S - self.strike


class call_option(contingent_claim):
    def __init__(self, K, T):
        super().__init__(K, T)

    def payoff(self, S):
        return max(S - self.strike, 0)


class put_option(contingent_claim):
    def __init__(self, K, T):
        super().__init__(K, T)

    def payoff(self, S):
        return max(self.strike - S, 0)

# репликация
class replication_engine():
    def __init__(self, claim, portfolio):
        self.claim = claim
        self.portfolio = portfolio

    def terminal_payoff(self, S_T):
        return self.claim.payoff(S_T)

    def pv(self):
        return self.portfolio.value_at(0)

    def replication_error(self, S_T):
        return abs(self.portfolio.value_at(1) - self.terminal_payoff(S_T))

# хеджирование
class hedging_engine():
    def __init__(self, portfolio, h=0.01):
        self.portfolio = portfolio
        self.h = h

    def delta(self, S_current):
        original = self.portfolio.risky.S0
        self.portfolio.risky.S0 = S_current + self.h
        v_up = self.portfolio.value(1)
        self.portfolio.risky.S0 = S_current - self.h
        v_dn = self.portfolio.value(1)
        self.portfolio.risky.S0 = original
        return (v_up - v_dn) / (2 * self.h)

    def gamma(self, S_current):
        original = self.portfolio.risky.S0
        self.portfolio.risky.S0 = S_current + self.h
        v_up = self.portfolio.value(1)
        self.portfolio.risky.S0 = S_current
        v_mid = self.portfolio.value(1)
        self.portfolio.risky.S0 = S_current - self.h
        v_dn = self.portfolio.value(1)
        self.portfolio.risky.S0 = original
        return (v_up - 2 * v_mid + v_dn) / (self.h ** 2)


# риск менеджмент
class risk_manager():
    def __init__(self, stock, T, n_sim=10000):
        self.stock = stock
        self.T = T
        self.simulated = np.array([stock.price(T) for _ in range(n_sim)])

    def tail_probability(self, A):
        return float(np.mean(self.simulated > A))

    def quantile(self, alpha):
        return float(np.quantile(self.simulated, 1 - alpha))

# игрушечная модель
class risky_asset_toy():
    def __init__(self, S0, S_H, S_L):
        self.S0  = S0
        self.S_H = S_H
        self.S_L = S_L

    def price(self, omega):
        if omega == 'H':
            return self.S_H
        if omega == 'L':
            return self.S_L

# арбитраж
class arbitrage_check():
    def __init__(self, V0, V1_H, V1_L):
        self.V0 = V0
        self.V1_H = V1_H
        self.V1_L = V1_L

    def is_arbitrage(self):
        cond_1 = self.V0 == 0
        cond_2 = self.V1_H >= 0 and self.V1_L >= 0
        cond_3 = self.V1_H > 0 or self.V1_L > 0
        return cond_1 and cond_2 and cond_3

# риск нейтральность
class risk_neutral_measure():
    def __init__(self, S0, S_H, S_L, r):
        self.S0 = S0
        self.S_H = S_H
        self.S_L = S_L
        self.r = r

    def q(self):
        return ((1 + self.r) * self.S0 - self.S_L) / (self.S_H - self.S_L)

    def q_L(self):
        return 1 - self.q()

    def expected_S1(self):
        return self.q() * self.S_H + self.q_L() * self.S_L

    def is_valid(self):
        cond_1 = self.q() > 0 and self.q_L() > 0
        cond_2 = abs(self.expected_S1() - (1 + self.r) * self.S0) < 1e-10
        return cond_1 and cond_2

# цена через риск нейтральность
class pv_risk_neutral():
    def __init__(self, claim, measure):
        self.claim = claim
        self.measure = measure

    def pv(self, S_H, S_L):
        X_H = self.claim.payoff(S_H)
        X_L = self.claim.payoff(S_L)
        EQ_X = self.measure.q() * X_H + self.measure.q_L() * X_L
        return EQ_X / (1 + self.measure.r)

# условное ожидание и мартингал
class conditional_expectation():
    def __init__(self, r):
        self.r = r

    def discounted_price(self, S_t, t):
        return S_t / (1 + self.r) ** t

    def check_martingale(self, S_t, t, S_T, T):
        left  = self.discounted_price(S_T, T)
        right = self.discounted_price(S_t, t)
        return round(left, 6), round(right, 6)
