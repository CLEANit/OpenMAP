2021-04-14
------------------
- Fix ImportError: cannot import name 'edward2' from 'tensorflow_probability'
    - Edward2 is no longer supported by the TensorFlow Probability team
    - the "official" repo for it is https://github.com/google/edward2/tree/master/edward2
    - phoenics_inc/BayesianNetwork/TfprobInterface/tfprob_interface.py, line 16
    - from tensorflow_probability import edward2 as ed [deleted]
    - pip install "git+https://github.com/google/edward2.git#egg=edward2"
    - import edward2 as ed