class Pipeline:
    def __init__(self):
        self.steps = []

    def add(self, func, **kwargs):
        self.steps.append((func, kwargs))

    def run(self, df):
        for func, kwargs in self.steps:
            df = func(df, **kwargs)
        return df