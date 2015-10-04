import unittest

if __name__ == '__main__':
    import test_wintersun
    import test_atom_generator
    import test_transformers
    all_tests = unittest.TestSuite()
    all_tests.addTests(unittest.TestLoader().loadTestsFromModule(
        test_wintersun))
    all_tests.addTests(unittest.TestLoader().loadTestsFromModule(
        test_atom_generator))
    all_tests.addTests(unittest.TestLoader().loadTestsFromModule(
        test_transformers))

    unittest.TextTestRunner().run(all_tests)
