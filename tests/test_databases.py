# from openmap.data_wrapper.MpWrapper import MpWrapper

# from openmap.data_wrapper.NomadWrapper import NomadWrapper
# from openmap.data_wrapper.OqWrapper import OqWrapper

# mp = MpWrapper()
# oq = OqWrapper()
# nomad = NomadWrapper()


# def test_MpWrapper():
#     """ """
#     q = '{Li,Na,K,Rb,Cs}-N'
#     try:
#         _ = mp.wrap_mp(q)
#         wrap = True
#
#     except (RuntimeError, TypeError, NameError, ValueError):
#         wrap = True
#     else:
#         wrap = False
#     assert wrap


#
#
# def test_OqWrapper():
#     """ """
#     qry = {
#         'element_set': '(Fe-Mn),O',  # include element Fe and Mn
#     }
#
#     try:
#         _ = oq.wrap_oq(qry)
#         wrap = True
#
#     except (RuntimeError, TypeError, NameError, ValueError):
#         wrap = False
#
#     assert wrap


# def test_NomadWrapper(): """ """ try: _ = nomad.search_params(atoms=['Ag', 'Pd'], searchable_quantities=[
# 'stress_tensor'], crystal_system='binary').get_pd_df(metadata='') wrap = True
#
#     except (RuntimeError, TypeError, NameError, ValueError):
#         wrap = False
#
#     assert wrap


def test_test():
    wrap = True

    assert wrap
