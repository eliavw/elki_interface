import io
import warnings

import pandas as pd
from prefect import Flow
from prefect.tasks.shell import ShellTask

from .cte import ELKI_FILEPATH
from .Elki import Elki


class Hics(Elki):
    def __init__(
        self, verbose=False, elki=ELKI_FILEPATH, contamination=0.1, k=5, **kwargs
    ):
        super().__init__(verbose=verbose, elki=elki, contamination=contamination)

        self.k = k
        self.fit_data_fp = None

        return

    def fit(self, X):
        super().fit(X)

        self.status = self.fit_flow.run()
        raw = self.status.result[self.fit_shell_task].result
        res = self._filter_raw(raw, X.shape[0])

        # Process
        df = self._to_dataframe(res)

        # Set scores and labels
        # TODO: Make this more consistent.
        self._scores = self._to_scores(df)
        self._set_labels()

        # Sometimes it struggles to properly kill the process.
        del raw
        del res
        self.fit_shell_task = None

        return


    # --------------
    # Parameter - Properties
    # --------------
    @property
    def k(self):
        # One more setter-call to ensure the value is correct!
        self.k = self._k
        return self._k

    @k.setter
    def k(self, value):
        self._k = self._compatible_k_n_instances(value)
        return 

    def _compatible_k_n_instances(self, k):
        if self.n_instances is None:
            return k
        else:
            res = min(k, self.n_instances-1)
            if res < k:
                msg = """
                k was set to {}, but n_instances is {}.
                ELKI won't have this. Changed k to {}
                """.format(k, self.n_instances, res)
                warnings.warn(msg)
            return res

    # --------------
    # Internal Methods
    # --------------
    @staticmethod
    def _filter_raw(raw, n_instances):
        if len(raw) > n_instances:
            """
            ELKI returned some additional things.
            These are not outputs. Luckily, the last n_instances _will_ be outputs,
            therefore, we just look at those.

            This is hacky, but a lot easier than writing a custom parser, and for our purposes, it works fine.
            """
            return raw[-n_instances:]
        else:
            return raw

    @staticmethod
    def _to_dataframe(res):
        return pd.read_csv(
            io.StringIO("\n".join(res)), delim_whitespace=True, header=None, index_col=0
        )

    @staticmethod
    def _to_scores(dataframe):
        return dataframe.sort_index().values.squeeze()

    # --------------
    # CLI Properties
    # --------------
    @property
    def fit_flow(self):
        shelltask = ShellTask(return_all=True, log_stderr=True)

        with Flow("fit") as f:
            self.fit_shell_task = shelltask(command=self.fit_command)

        return f

    @property
    def fit_command(self):
        fit_cmd = "{} {} {} {} {}".format(
            self.kdd_command,
            self.i_command,
            self.hics_command,
            self.eval_command,
            self.o_command,
        )
        return fit_cmd

    @property
    def hics_command(self):
        return "-algorithm outlier.meta.HiCS -lof.k {}".format(self.k)

    @property
    def i_command(self):
        # Command snippet for input data
        return "-db HashmapDatabase -dbc.in {}".format(self.data_filepath.name)
