import sys
sys.path.insert(1,"../../")
import h2o
from tests import pyunit_utils


def empty_strings():

  #dictionary
  d = h2o.H2OFrame(
    {'e':["",""]
    ,'c':["",""]
    ,'f':["",""]
     }
  )
  assert d.isna().sum() == 0
  assert (d == '').sum() == d.nrow * d.ncol

  #single list
  d = h2o.H2OFrame([""]*4)
  assert d.isna().sum() == 0
  assert (d == '').sum() == d.nrow * d.ncol

  #list of lists
  d = h2o.H2OFrame([[""]*4]*3)
  assert d.isna().sum() == 0
  assert (d == '').sum() == d.nrow * d.ncol


if __name__ == "__main__":
  pyunit_utils.standalone_test(empty_strings)
else:
  empty_strings()
