class RLCore:
    def __init__(self, learning_rate=0.1, discount_factor=0.9):
        self.q_table = {}
        self.lr = learning_rate
        self.gamma = discount_factor

    def get_q(self, state, action):
        if (state, action) not in self.q_table:
            self.q_table[(state, action)] = 0.0
        return self.q_table[(state, action)]

    def update_q(self, state, action, reward, next_state):

        # Ensure state and action are hashable
        if not isinstance(state, tuple):
            raise TypeError("State must be a tuple.")
        if not isinstance(action, str):
            raise TypeError("Action must be a string.")

        # Current Q value
        old_q = self.get_q(state, action)

        # Max future Q
        future_qs = [
            self.get_q(next_state, a)
            for a in ["BUY", "SELL", "HOLD"]
        ]
        max_future_q = max(future_qs)

        # Q-learning formula
        new_q = old_q + self.lr * (reward + self.gamma * max_future_q - old_q)

        # Save updated Q
        self.q_table[(state, action)] = new_q

        return new_q
