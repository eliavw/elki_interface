from .Elki import Elki
from prefect.tasks.shell import ShellTask
from prefect import Flow
import pandas as pd
import io

from .cte import ELKI_FILEPATH


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
