import numpy as np
import pandas as pd
import prefect

import tempfile

from .cte import ELKI_FILEPATH


class Elki:
    def __init__(self, verbose=False, elki=ELKI_FILEPATH, contamination=0.1, **kwargs):
        # General params
        self.verbose = verbose

        # Metadata
        self.n_instances = None
        self.n_attributes = None

        # Data
        self.data_filepath = None

        # Outcomes
        self.contamination = contamination
        self._scores = None
        self._labels = None

        # CLI
        self.elki = elki
        return

    def fit(self, X):
        self._init_metadata(X)
        self._init_data(X)
        self._init_labels()
        return

    def predict(self):
        return self.labels

    # --------------
    # Internal Methods
    # --------------
    def _init_metadata(self, X):
        self.n_instances, self.n_attributes = X.shape
        return

    def _init_data(self, data):
        filepath = tempfile.NamedTemporaryFile(suffix=".csv")
        np.savetxt(filepath.name, data, delimiter=",")
        self.data_filepath = filepath
        return

    def _init_labels(self):
        self._labels = np.zeros(self.n_instances)
        return

    def _set_labels(self):
        anomaly_idxs = np.argpartition(self.scores, -self.integer_contamination)[
            -self.integer_contamination :
        ]
        self._labels[anomaly_idxs] = 1
        return

    # --------------
    # Properties
    # --------------
    @property
    def contamination(self):
        return self._contamination

    @contamination.setter
    def contamination(self, value):
        assert (
            0.0 <= value <= 1.0
        ), "Contamination must be a percentage, expressed as a float in [0.0, 1.0]."
        self._contamination = value
        return

    @property
    def decision_scores_(self):
        return self.scores

    @property
    def scores(self):
        return self._scores

    @property
    def labels(self):
        return self._labels

    @labels.setter
    def labels(self, value):
        assert isinstance(value, np.ndarray)
        assert value.shape[0] == self.n_instances
        self._labels == value
        return

    @property
    def n_anomalies(self):
        return np.sum(self.labels)

    @property
    def integer_contamination(self):
        # Contamination in integer.
        return int(self.contamination * self.n_instances)

    # CLI properties
    @property
    def kdd_command(self):
        kddcli = "KDDCLIApplication"
        return "{} {}".format(self.javacall, kddcli)

    @property
    def javacall(self):
        return "java -jar {}".format(self.elki)

    @property
    def eval_command(self):
        # Command snippet for evaluation
        return "-evaluator NoAutomaticEvaluation"

    @property
    def o_command(self):
        # Command snippet for output data
        return "-resulthandler tutorial.outlier.SimpleScoreDumper"

    # --------------
    # Static Methods
    # --------------
