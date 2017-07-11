################################################################################
#
#   RMG - Reaction Mechanism Generator
#
#   Copyright (c) 2002-2017 Prof. William H. Green (whgreen@mit.edu), 
#   Prof. Richard H. West (r.west@neu.edu) and the RMG Team (rmg_dev@mit.edu)
#
#   Permission is hereby granted, free of charge, to any person obtaining a
#   copy of this software and associated documentation files (the 'Software'),
#   to deal in the Software without restriction, including without limitation
#   the rights to use, copy, modify, merge, publish, distribute, sublicense,
#   and/or sell copies of the Software, and to permit persons to whom the
#   Software is furnished to do so, subject to the following conditions:
#
#   The above copyright notice and this permission notice shall be included in
#   all copies or substantial portions of the Software.
#
#   THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#   AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#   LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#   FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#   DEALINGS IN THE SOFTWARE.
#
################################################################################

import unittest
import mock
import os
from chemkin import *
import rmgpy


###################################################

class ChemkinTest(unittest.TestCase):
    @mock.patch('rmgpy.chemkin.logging')
    def test_readThermoEntry_BadElementCount(self, mock_logging):
        """
        Test that invalid element count logs the appropriate warning.

        This test uses the `mock` module in order to test calls to logging.
        The `mock.patch` decorator replaces the logging module instance in
        rmgpy.chemkin with a mock instance that can be accessed by this
        unit test. By using the mock instance, it is possible to assert that
        the expected logging statements are being created.
        """
        entry = """C2H6                    H   XC   X          L   100.000  5000.000  827.28      1
 2.44813916E+00 1.83377834E-02-7.25714119E-06 1.35300042E-09-9.60327447E-14    2
-1.19655244E+04 8.07917520E+00 3.50507145E+00-3.65219841E-03 6.32200490E-05    3
-8.01049582E-08 3.19734088E-11-1.15627878E+04 6.67152939E+00                   4
"""
        with self.assertRaises(ValueError):
            readThermoEntry(entry)

        mock_logging.info.assert_called_with("Trouble reading line 'C2H6                    H   XC   X          L   100.000  5000.000  827.28      1' element segment 'H   X'")

    @mock.patch('rmgpy.chemkin.logging')
    def test_readThermoEntry_NotGasPhase(self, mock_logging):
        """
        Test that non gas phase data logs the appropriate warning.

        This test uses the `mock` module in order to test calls to logging.
        The `mock.patch` decorator replaces the logging module instance in
        rmgpy.chemkin with a mock instance that can be accessed by this
        unit test. By using the mock instance, it is possible to assert that
        the expected logging statements are being created.
        """
        entry = """C2H6                    H   6C   2          L   100.000  5000.000  827.28      1
 2.44813916E+00 1.83377834E-02-7.25714119E-06 1.35300042E-09-9.60327447E-14    2
-1.19655244E+04 8.07917520E+00 3.50507145E+00-3.65219841E-03 6.32200490E-05    3
-8.01049582E-08 3.19734088E-11-1.15627878E+04 6.67152939E+00                   4
"""
        species, thermo, formula = readThermoEntry(entry)

        mock_logging.warning.assert_called_with("Was expecting gas phase thermo data for C2H6. Skipping thermo data.")
        self.assertEqual(species, 'C2H6')
        self.assertIsNone(formula)
        self.assertIsNone(thermo)

    @mock.patch('rmgpy.chemkin.logging')
    def test_readThermoEntry_NotFloat(self, mock_logging):
        """
        Test that non-float parameters log the appropriate warning.

        This test uses the `mock` module in order to test calls to logging.
        The `mock.patch` decorator replaces the logging module instance in
        rmgpy.chemkin with a mock instance that can be accessed by this
        unit test. By using the mock instance, it is possible to assert that
        the expected logging statements are being created.
        """
        entry = """C2H6                    H   6C   2          G   100.000  5000.000  827.28      1
 X.44813916E+00 1.83377834E-02-7.25714119E-06 1.35300042E-09-9.60327447E-14    2
-1.19655244E+04 8.07917520E+00 3.50507145E+00-3.65219841E-03 6.32200490E-05    3
-8.01049582E-08 3.19734088E-11-1.15627878E+04 6.67152939E+00                   4
"""
        species, thermo, formula = readThermoEntry(entry)

        mock_logging.warning.assert_called_with("could not convert string to float: X.44813916E+00")
        self.assertEqual(species, 'C2H6')
        self.assertIsNone(formula)
        self.assertIsNone(thermo)

    def test_readThermoEntry_NoTRange(self):
        """Test that missing temperature range can be handled for thermo entry."""
        entry = """C2H6                    H   6C   2          G                                  1
 2.44813916E+00 1.83377834E-02-7.25714119E-06 1.35300042E-09-9.60327447E-14    2
-1.19655244E+04 8.07917520E+00 3.50507145E+00-3.65219841E-03 6.32200490E-05    3
-8.01049582E-08 3.19734088E-11-1.15627878E+04 6.67152939E+00                   4
"""
        species, thermo, formula = readThermoEntry(entry, Tmin=100.0, Tint=827.28, Tmax=5000.0)

        self.assertEqual(species, 'C2H6')
        self.assertEqual(formula, {'H': 6, 'C': 2})
        self.assertTrue(isinstance(thermo, NASA))

    def testReadAndWriteTemplateReactionFamilyForMinimalExample(self):
        """
        This example is mainly to test if family info can be correctly
        parsed from comments like '!Template reaction: R_Recombination'.
        """
        folder = os.path.join(os.path.dirname(rmgpy.__file__), 'test_data/chemkin/chemkin_py')

        chemkinPath = os.path.join(folder, 'minimal', 'chem.inp')
        dictionaryPath = os.path.join(folder, 'minimal', 'species_dictionary.txt')

        # loadChemkinFile
        species, reactions = loadChemkinFile(chemkinPath, dictionaryPath)

        reaction1 = reactions[0]
        self.assertEqual(reaction1.family, "R_Recombination")

        reaction2 = reactions[1]
        self.assertEqual(reaction2.family, "H_Abstraction")

        # saveChemkinFile
        chemkinSavePath = os.path.join(folder, 'minimal', 'chem_new.inp')
        dictionarySavePath = os.path.join(folder, 'minimal', 'species_dictionary_new.txt')

        saveChemkinFile(chemkinSavePath, species, reactions, verbose=True, checkForDuplicates=True)
        saveSpeciesDictionary(dictionarySavePath, species, oldStyle=False)

        self.assertTrue(os.path.isfile(chemkinSavePath))
        self.assertTrue(os.path.isfile(dictionarySavePath))

        # clean up
        os.remove(chemkinSavePath)
        os.remove(dictionarySavePath)

    def testReadAndWriteTemplateReactionFamilyForPDDExample(self):
        """
        This example is mainly to ensure comments like
        '! Kinetics were estimated in this direction instead
        of the reverse because:' or '! This direction matched
        an entry in H_Abstraction, the other was just an estimate.'
        won't interfere reaction family info retrival.
        """
        folder = os.path.join(os.path.dirname(rmgpy.__file__), 'test_data/chemkin/chemkin_py')

        chemkinPath = os.path.join(folder, 'pdd', 'chem.inp')
        dictionaryPath = os.path.join(folder, 'pdd', 'species_dictionary.txt')

        # loadChemkinFile
        species, reactions = loadChemkinFile(chemkinPath, dictionaryPath)

        reaction1 = reactions[0]
        self.assertEqual(reaction1.family, "H_Abstraction")

        reaction2 = reactions[1]
        self.assertEqual(reaction2.family, "H_Abstraction")

        # saveChemkinFile
        chemkinSavePath = os.path.join(folder, 'minimal', 'chem_new.inp')
        dictionarySavePath = os.path.join(folder, 'minimal', 'species_dictionary_new.txt')

        saveChemkinFile(chemkinSavePath, species, reactions, verbose=False, checkForDuplicates=False)
        saveSpeciesDictionary(dictionarySavePath, species, oldStyle=False)

        self.assertTrue(os.path.isfile(chemkinSavePath))
        self.assertTrue(os.path.isfile(dictionarySavePath))

        # clean up
        os.remove(chemkinSavePath)
        os.remove(dictionarySavePath)

    def testTransportDataReadAndWrite(self):
        """
        Test that we can write to chemkin and recreate the same transport object
        """
        from rmgpy.species import Species
        from rmgpy.molecule import Molecule
        from rmgpy.transport import TransportData

        Ar = Species(label="Ar",
                     transportData=TransportData(shapeIndex=0, epsilon=(1134.93, 'J/mol'), sigma=(3.33, 'angstrom'),
                                                 dipoleMoment=(0, 'De'), polarizability=(0, 'angstrom^3'),
                                                 rotrelaxcollnum=0.0, comment="""GRI-Mech"""))

        Ar_write = Species(label="Ar")
        folder = os.path.join(os.path.dirname(rmgpy.__file__), 'test_data')

        tempTransportPath = os.path.join(folder, 'tran_temp.dat')

        saveTransportFile(tempTransportPath, [Ar])
        speciesDict = {'Ar': Ar_write}
        loadTransportFile(tempTransportPath, speciesDict)
        self.assertEqual(repr(Ar), repr(Ar_write))

        os.remove(tempTransportPath)

    def testUseChemkinNames(self):
        """
        Test that the official chemkin names are used as labels for the created Species objects.
        """

        folder = os.path.join(os.path.dirname(rmgpy.__file__), 'test_data/chemkin/chemkin_py')

        chemkinPath = os.path.join(folder, 'minimal', 'chem.inp')
        dictionaryPath = os.path.join(folder, 'minimal', 'species_dictionary.txt')

        # loadChemkinFile
        species, reactions = loadChemkinFile(chemkinPath, dictionaryPath, useChemkinNames=True)

        expected = [
            'Ar',
            'He',
            'Ne',
            'N2',
            'ethane',
            'CH3',
            'C2H5',
            'C'
        ]

        for spc, label in zip(species, expected):
            self.assertEqual(spc.label, label)

    def testReactantN2IsReactiveAndGetsRightSpeciesIdentifier(self):
        """
        Test that after loading chemkin files, species such as N2, which is in the default
        inert list of RMG, should be treated as reactive species and given right species
        Identifier when it's reacting in reactions.
        """
        folder = os.path.join(os.path.dirname(rmgpy.__file__), 'test_data/chemkin/chemkin_py')

        chemkinPath = os.path.join(folder, 'NC', 'chem.inp')
        dictionaryPath = os.path.join(folder, 'NC', 'species_dictionary.txt')

        # loadChemkinFile
        species, reactions = loadChemkinFile(chemkinPath, dictionaryPath, useChemkinNames=True)

        for n2 in species:
            if n2.label == 'N2':
                break
        self.assertTrue(n2.reactive)

        self.assertEqual(getSpeciesIdentifier(n2), 'N2(35)')
