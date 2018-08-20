#! /usr/bin/env /opt/local/bin/python

"""
Description:
  Clean up a latex .bib record on the clipboard or retrieved from the doi.

Usage:
  cleanbib   [--doi=<doi>] 
  cleanbib -h | --help

Options:
  -h --help                Show this screen.
  -d <doi> --doi=<doi>     A valid doi.
"""

# Adrian Del Maestro
# 11.21.2017

# We use bibtexparser: https://github.com/sciunto-org/python-bibtexparser for
# parsing the .bib file and pyperclip for reading/writing to the clipboard and
# docopt for the command line.

from __future__ import print_function
import bibtexparser
from docopt import docopt
import pyperclip
import requests
import re
from string import ascii_letters
from random import choice

# -----------------------------------------------------------------------------
journal_abbreviations = {'AIAA Journal': 'AIAA J.',
 'AIChE Journal': 'AIChE J.',
 'AIP Conference Proceedings': 'AIP Conf. Proc.',
 'Accounts of Chemical Research': 'Acc. Chem. Res.',
 'Acta Chemica Scandinavica': 'Acta Chem. Scand.',
 'Acta Crystallographica': 'Acta Crystallogr.',
 'Acta Crystallographica, Section A: Crystal Physics, Diffraction, Theoretical and General Crystallography': 'Acta Crystallogr. Sec. A',
 'Acta Crystallographica, Section B: Structural Crystallography and Crystal Chemistry': 'Acta Crystallogr. Sec. B',
 'Acta Mathematica Academiae Scientiarum Hungaricae': 'Acta Math. Acad. Sci. Hung.',
 'Acta Metallurgica': 'Acta Metall.',
 'Acta Physica': 'Acta Phys.',
 'Acta Physica Austriaca': 'Acta Phys. Austriaca',
 'Acta Physica Polonica': 'Acta Phys. P01.',
 'Acustica': 'Acustica',
 'Advances in Applied Mechanics': 'Adv. Appl. Mech.',
 'Advances in Atomic and Molecular Physics': 'Adv. At. Mol. Phys.',
 'Advances in Chemical Physics': 'Adv. Chem. Phys.',
 'Advances in Magnetic Resonance': 'Adv. Magn. Reson.',
 'Advances in Nuclear Physics': 'Adv. Nucl. Phys.',
 'Advances in Physics': 'Adv. Phys.',
 'Advances in Quantum Chemistry': 'Adv. Quantum Chem.',
 'Akusticheskii Zhurnal [Soviet PhysicsAcoustics]': 'Akust. Zh. [Sov. Phys. Acoust.]',
 'American J ournal of Physics': 'Am. J. Phys.',
 'Analytical Chemistry': 'Anal. Chem.',
 'Annalen der Physik (Leipzig)': 'Ann. Phys. (Leipzig)',
 'Annales de Chimie et de Physique': 'Ann. Chim. Phys.',
 'Annales de Geophysique': 'Ann. Geophys.',
 'Annales de Physique (Paris)': 'Ann. Phys. (Paris)',
 "Annales de llnstitut Henri Poincar{\\'e}": "Ann. Inst. Henri Poincar{\\'e}",
 "Annales de llnstitut Henri Poincar{\\'e}, Section A: Physique Theorique": "Ann. Inst. Henri Poincar{\\'e}, A",
 "Annales de llnstitut Henri Poincar{\\'e}, Section B: Calculdes Probabilit{\\'e}s et Statistique": "Ann. Inst. Henri Poincar{\\'e}, B",
 'Annals of Fluid Dynamics': 'Ann. Fluid Dyn.',
 'Annals of Mathematics': 'Ann. Math.',
 'Annals of Physics (New York)': 'Ann. Phys. (N.Y.)',
 'Annals of Physics': 'Ann. Phys.',
 'Annual Review of Astronomy and Astrophysics': 'Annu. Rev. Astron. Astrophys.',
 'Annual Review of Atomic and Molecular Physics': 'Annu. Rev. At. Mol. Phys.',
 'Annual Review of Fluid Mechanics': 'Annu. Rev. Fluid Mech.',
 'Annual Review of Nuclear Science': 'Annu. Rev. Nucl. Sci.',
 'Applied Optics': 'Appl. Opt.',
 'Applied Physics Letters': 'Appl. Phys. Lett.',
 'Applied Spectroscopy': 'Appl. Spectrosc.',
 'Arkiv foer Fysik': 'Ark. Fys.',
 'Astronomical Journal': 'Astron. J.',
 'Astronomicheskii Zhurnal [Soviet Astronomy]': 'Astron. Zh. [Sov. Astron.]',
 'Astronomische Nachrichten': 'Astron. Nachr.',
 'Astronomy and Astrophysics': 'Astron. Astrophys.',
 'Astroparticle Physics': 'Astropart. Phys.',
 'Astrophysical Journal': 'Astrophys. J.',
 'Astrophysical Journal, Letters to the Editor': 'Astrophys. J. Lett.',
 'Astrophysical Journal, Supplement Series': 'Astrophys. J. Suppl. Ser.',
 'Astrophysical Letters': 'Astrophys. Lett.',
 'Astrophysics and Space Science': 'Astrophy. Space Sci.',
 'Atomic Data and Nuclear Data Tables': 'At. Data. Nucl. Data Tables',
 'Atomnaya Energiya [Soviet Journal of Atomic Energy]': 'At. Energ. [Sov. J. At. Energy]',
 'Australian Journal of Physics': 'Aust. J. Phys.',
 'Bell System Technical Journal': 'Bell Syst. Tech. J.',
 'Berichte der Bunsengesellschaft f{\\"u}r Physikalische Chemie': 'Ber. Bunsenges. Phys. Chem.',
 'British Journal of Applied Physics': 'Br. J. Appl. Phys.',
 'Bulletin of The American Physical Society': 'Bull. Am. Phys. Soc.',
 'Bulletin of the Academy of Sciences of the USSR, Physical Series [translation of Izvestiya Akademii Nauk SSSR, Seriya Fizicheskaya]': 'Bull. Acad. Sci. USSR, Phys. Ser.',
 'Bulletin of the American Astronomical Society': 'Bull. Am. Astron. Soc.',
 'Bulletin of the Astronomical Institutes of the Netherlands': 'Bull. Astron. Inst. Neth.',
 'Bulletin of the Chemical Society of Japan': 'Bull. Chem. Soc. Jpn.',
 'Bulletin of the Seismological Society of America': 'Bull. Seismol. Soc. Am.',
 'Canadian Journal of Chemistry': 'Can. J. Chem.',
 'Canadian Journal of Physics': 'Can. J. Phys.',
 'Canadian Journal of Research': 'Can. J. Res.',
 'Chaos': 'Chaos',
 'Chemical Physics': 'Chem. Phys.',
 'Chemical Physics Letters': 'Chem. Phys. Lett.',
 'Chemical Reviews': 'Chem. Rev.',
 'Chinese Journal of Physics [translation of Wuli Xuebao (Acta Physica Sinica)]': 'Chin. J. Phys.',
 'Classical and Quantum Gravity': 'Class. Quantum Gravity',
 'Comments on Astrophysics and Space Physics': 'Comments Astrophys. Space Phys.',
 'Comments on Atomic and Molecular Physics': 'Comments At. Mol. Phys.',
 'Comments on Nuclear and Particle Physics': 'Comments Nucl. Part. Phys.',
 'Comments on Plasma Physics and Controlled Fusion': 'Comments Plasma Phys. Controlled Fusion',
 'Comments on Solid State Physics': 'Comments Solid State Phys.',
 'Communications 0n Pure and Applied Mathematics': 'Commun. Pure Appl. Math.',
 'Communications in Mathematical Physics': 'Commun. Math. Phys.',
 'Complex Systems': 'Complex Syst.',
 "Comptes Rendus Hebdomadaires des S{\\'e}ances de l'Acad{\\'e}mie des Sciences, Serie B: Sciences Physiques": 'C. R. Acad. Sci. Ser. B',
 "Comptes Rendus Hebdomadaires des S{\\'e}ances de l'Acad{\\'e}mie des Sciences": 'C. R. Acad. Sci.',
 "Comptes Rendus Hebdomadaires des S{\\'e}ances de l'Acad{\\'e}mie des Sciences, Serie A: Sciences Math{\\'e}matiques": 'C. R. Acad. Sci. Ser. A',
 'Cryogenics': 'Cryogenics',
 'Czechoslovak Journal of Physics': 'Czech. J. Phys.',
 'Discussions of the Faraday Society': 'Discuss. Faraday Soc.',
 'Doklady Akademii Nauk SSSR [Soviet PhysicsiDoklady]': 'Dokl. Akad. Nauk SSSR [Sov. Phys. Dokl.]',
 'Earth Planets Space [formerly Journal of Geomagnetism and Geoelectricity]': 'Earth Planets Space',
 'Earth and Planetary Science Letters': 'Earth Planet. Sci. Lett.',
 'Electronics Letters': 'Electron. Lett.',
 'European Journal of Physics': 'Eur. J. Phys.',
 'European Physical Journal A: Hadrons and Nuclei': 'Eur. Phys. J. A',
 'European Physics Journal B: Condensed Matter': 'Eur. Phys. J. B',
 'European Physics Journal C: Particles and Fields': 'Eur. Phys. J. C',
 'European Physics Journal D: Atomic, Molecular, and Optical Physics': 'Eur. Phys. J. D',
 'European Physics Journal E: Soft Matter': 'Eur. Phys. J. E',
 'Europhysics Letters': 'Europhys. Lett.',
 'Ferroelectrics': 'Ferroelectrics',
 'Few-Body Systems': 'Few-Body Syst.',
 'Fields and Quanta': 'Fields Quanta',
 'Fizika Elementarnykh Chastits i Atomnogo Yadra [Soviet Journal of Particles and Nuclei]': 'Fiz. Elem. Chastits At. Yadra [Sov. J. Part. Nucl.]',
 'Fizika Metallov i Metallovedenie [Physics of Metals and Metallography (USSR)]': 'Fiz. Met. Metalloved. [Phys Met. Metallogr. (USSRH',
 'Fizika Nizkikh Temperatur [Soviet Journal of Low Temperature Physics]': 'Fiz. Nizk. Temp. [Sov. J. Low Temp. Phys]',
 'Fizika Plazmy [Soviet Journal of Plasma Physics]': 'Fiz. Plazmy [Sov. J. Plasma Phys]',
 'Fizika Tverdogo Tela (Leningrad) [Soviet Physics-Solid State]': 'Fiz. Tverd. Tela (Leningrad) [Sov. Phys. Solid State]',
 'Fizika i Tekhnika Poluprovodnikov [Soviet Physicsisemiconductors]': 'Fiz. Tekh. Poluprovodn. [Sov. Phys. Semicond]',
 'Fortschritte der Physik': 'Fortschr. Phys.',
 'Foundations of Physics': 'Found. Phys.',
 'General Relativity and Gravitation': 'Gen. Relativ. Gravit.',
 'Geochimica et Cosmochimica Acta': 'Geochim. Cosmochim. Acta',
 'Helvetica Chimica Acta': 'Helv. Chim. Acta',
 'Helvetica Physica Acta': 'Helv. Phys. Acta',
 'High Temperature (USSR) [translation of Teplofizika Vysokikh Temperatur]': 'High Temp. (USSR)',
 'Hyperfine Interactions': 'Hyperfine Interact.',
 'IBM Journal of Research and Development': 'IBM J. Res. Dev.',
 'IEEE Journal of Quantum Electronics': 'IEEE J. Quantum Electron.',
 'IEEE Transactions on Electron Devices': 'IEEE Trans. Electron Devices',
 'IEEE Transactions on Information Theory': 'IEEE Trans. Inf. Theory',
 'IEEE Transactions on Instrumentation and Measurement': 'IEEE Trans. Instrum. Meas.',
 'IEEE Transactions on Magnetics': 'IEEE Trans. Magn.',
 'IEEE Transactions on Microwave Theory and Techniques': 'IEEE Trans. Microwave Theory Tech.',
 'IEEE Transactions on Nuclear Science': 'IEEE Trans. Nucl. Sci.',
 'IEEE Transactions on Sonics and Ultrasonics': 'IEEE Trans. Sonics Ultrason.',
 'Icarus': 'Icarus',
 'Industrial and Engineering Chemistry': 'Ind. Eng. Chem.',
 'Infrared Physics': 'Infrared Phys.',
 'Inorganic Chemistry': 'Inorg. Chem.',
 'Inorganic Materials (USSR) [translation of Izvestiya Akademii Nauk SSSR, Neorganicheskie Materialy]': 'Inorg. Mater. (USSR)',
 'Instruments and Experimental Techniques (USSR) [translation of Pribory i Tekhnika Eksperimenta]': 'Instrum. Exp. Tech. (USSR)',
 'International Journal of Energy Research': 'Int. J . Energy Res.',
 'International Journal of Magnetism': 'Int. J . Magn.',
 'International Journal of Quantum Chemistry': 'Int. J . Quantum Chem.',
 'International Journal of Quantum Chemistry, Part 1': 'Int. J. Quantum Chem. 1',
 'International Journal of Quantum Chemistry, Part 2': 'Int. J. Quantum Chem. 2',
 'International Journal of Quantum Information': 'Int. J . Quantum Inf.',
 'International Journal of Theoretical Physics': 'Int. J. Theor. Phys.',
 'Izvestiya Akademii Nauk SSSR, Fizika Atmosfery i Okeana [Izvestiya, Academy of Sciences, USSR, Atmospheric and Oceanic Physics]': 'Izv. Acad. Nauk SSSR, Fiz. Atmos. Okeana [Izv. Acad. Sci. USSR, Atmos. Oceanic Phys]',
 'Izvestiya Akademii Nauk SSSR, Fizika Zemli [Izvestiya, Academy of Sciences, USSR, Physics of the Solid Earth]': 'Izv. Acad. Nauk SSSR, Fiz. Zemli.  [Izv. Acad. Sci. USSR, Phys. Solid Earth]',
 'Izvestiya Akademii Nauk SSSR, Neorganicheskie Materialy [Inorganic Materials (USSR)]': 'Izv. Akad. Nauk SSSR, Neorg. Mater.  [Inorg. Mater. (USSR)]',
 'Izvestiya Akademii Nauk SSSR, Seriya Fizicheskaya [Bulletin of the Academy of Sciences of the USSR, Physical Series]': 'Izv. Acad. Nauk SSSR, Ser. Fiz.  [Bull. Acad. Sci. USSR, Phys. Sen]',
 'Izvestiya Vysshikh Uchebnykh Zavedenii, Fizika [Soviet Physics Journal]': 'Izv. Vyssh. Uchebn. Zavad. Fiz. [Sov. Phys. J ]',
 'Izvestiya Vysshikh Uchebnykh Zavedenii, Radiofizika [Soviet Radiophysics]':
     'Izv. Vyssh. Uchebn. Zaved. Radiofiz. [Sov. Radiophys.]',
 'Izvestiya, Academy of Sciences, USSR, Atmospheric and Oceanic Physics [translation of Izvestiya Akademii Nauk SSSR, Fizika Atmosfery i Okeana]': 'Izv. Acad. Sci. USSR, Atmos. Oceanic Phys.',
 'Izvestiya, Academy of Sciences, USSR, Physics of the Solid Earth [translation of Izvestiya Akademii Nauk SSSR, Fizika Zemli]': 'Izv. Acad. Sci. USSR, Phys. Solid Earth',
 'JETP Letters [translation of Pisma v Zhurnal Eksperimentalnoi i Teoreticheskoi Fiziki]': 'JETP Lett.',
 'Japanese Journal of Applied Physics': 'Jpn. J. Appl. Phys.',
 'Japanese Journal of Physics': 'Jpn. J . Phys.',
 'Journal 0f Luminescence': 'J. Lumin.',
 'Journal de Chimie Physique': 'J. Chim. Phys.',
 'Journal de Physique (Paris)': 'J. Phys. (Paris)',
 'Journal de Physique et le Radium': 'J. Phys. Radium',
 'Journal of Applied Crystallography': 'J. Appl. Crystallogr.',
 'Journal of Applied Physics': 'J. Appl. Phys.',
 'Journal of Applied Spectroscopy (USSR) [translation of Zhurnal Prikladnoi Spektroskopii]': 'J. Appl. Spectrosc. (USSR)',
 'Journal of Atmospheric Sciences': 'J. Atmos. Sci.',
 'Journal of Atmospheric and Terrestrial Physics': 'J. Atmos. Terr. Phys.',
 'Journal of Chemical Physics': 'J. Chem. Phys.',
 'Journal of Colloid and Interface Science': 'J. Colloid Interface Sci.',
 'Journal of Computational Physics': 'J. Comput. Phys.',
 'Journal of Crystal Growth': 'J. Cryst. Growth',
 'Journal of Electron Spectroscopy and Related Phenomenon': 'J. Electron. Spectrosc. Relat. Phenom.',
 'Journal of Electronic Materials': 'J. Electron. Mater.',
 'Journal of Fluid Mechanics': 'J. Fluid Mech.',
 'Journal of Geophysical Research': 'J. Geophys. Res.',
 'Journal of High Energy Physics': 'J. High Energy Phys.',
 'Journal of Inorganic and Nuclear Chemistry': 'J. Inorg. Nucl. Chem.',
 'Journal of Low Temperature Physics': 'J. Low Temp. Phys.',
 'Journal of Macromolecular Science, [Part B] Physics': 'J. Macromol. Sci. Phys.',
 'Journal of Magnetism and Magnetic Materials': 'J. Magn. Magn. Mater.',
 'Journal of Mathematical Physics (New York)': 'J. Math. Phys. (N.Y.)',
 'Journal of Molecular Spectroscopy': 'J. Mol. Spectrosc.',
 'Journal of Non-Crystalline Solids': 'J. Non-Cryst. Solids',
 'Journal of Nonlinear Science': 'J. Nonlinear Sci.',
 'Journal of Nuclear Energy': 'J. Nucl. Energy',
 'Journal of Nuclear Energy, Part C: Plasma Physics, Accelerators, Thermonuclear Research': 'J. Nucl. Energy, Part C',
 'Journal of Nuclear Materials': 'J. Nucl. Mater.',
 'Journal of Physical Chemistry': 'J. Phys. Chem.',
 'Journal of Physical and Chemical Reference Data': 'J. Phys. Chem. Ref. Data',
 'Journal of Physics (Moscow)': 'J. Phys. (Moscow)',
 'Journal of Physics A: Mathematical and General': 'J. Phys. A',
 'Journal of Physics B: Atomic, Molecular and Optical': 'J. Phys. B',
 'Journal of Physics C: Solid State Physics': 'J. Phys. C',
 'Journal of Physics D: Applied Physics': 'J. Phys. D',
 'Journal of Physics E: Scientific Instruments': 'J. Phys. E',
 'Journal of Physics F: Metal Physics': 'J. Phys. F',
 'Journal of Physics G: Nuclear and Particle Physics': 'J. Phys. G',
 'Journal of Physics and Chemistry of Solids': 'J. Phys. Chem. Solids',
 'Journal of Physics: Condensed Matter': 'J. Phys. Condens. Matter',
 'Journal of Plasma Physics': 'J. Plasma Phys.',
 'Journal of Polymer Science': 'J. Polym. Sci.',
 'Journal of Polymer Science, Polymer Letters Edition': 'J. Polym. Sci. Polym. Lett. Ed.',
 'Journal of Polymer Science, Polymer Physics Edition': 'J. Polym. Sci. Polym. Phys. Ed.',
 'Journal of Quantitative Spectroscopy & Radiative Transfer': 'J. Quant. Spectrosc. Radiat. Transfer',
 'Journal of Research of the National Bureau of Standards': 'J. Res. Natl. Bur. Stand.',
 'Journal of Research of the National Bureau of Standards, Section A: Physics and Chemistry': 'J. Res. Natl. Bur. Stand. Sec. A',
 'Journal of Research of the National Bureau of Standards, Section B: Mathematical Sciences': 'J. Res. Natl. Bur. Stand. Sec. B',
 'Journal of Research of the National Bureau of Standards, Section C: Engineering and Instrumentation': 'J. Res. Natl. Bur. Stand. Sec. C',
 'Journal of Research of the National Institute of Standards and Technology': 'J. Res. Natl. Inst. Stand. Technol.',
 'Journal of Scientific Instruments': 'J. Sci. Instrum.',
 'Journal of Sound and Vibration': 'J. Sound Vib.',
 'Journal of Statistical Physics': 'J. Stat. Phys.',
 'Journal of Statistical Mechanics: Theory and Experiment':'J. Stat. Mech.: Theor. Exp.',
 'Journal of Superconductivity': 'J. Supercond.',
 'Journal of Theoretical Biology': 'J. Theor. Biol.',
 'Journal of Vacuum Science and Technology': 'J. Vac. Sci. Technol.',
 'Journal of the Acoustical Society of America': 'J. Acoust. Soc. Am.',
 'Journal of the American Ceramic Society': 'J. Am. Ceram. Soc.',
 'Journal of the American Chemical Society': 'J. Am. Chem. Soc.',
 'Journal of the American Institute of Electrical Engineers': 'J. Am. Inst. Electr. Eng.',
 'Journal of the Audio Engineering Society': 'J. Audio Eng. Soc.',
 'Journal of the Chemical Society': 'J. Chem. Soc.',
 'Journal of the Electrochemical Society': 'J. Electrochem. Soc.',
 'Journal of the Mechanics and Physics of Solids': 'J. Mech. Phys. Solids',
 'Journal of the Optical Society of America': 'J. Opt. Soc. Am.',
 'Journal of the Optical Society of America A: Optics, Image Science & Vision': 'J. Opt. Soc. Am. A',
 'Journal of the Optical Society of America B: Optical Physics': 'J. Opt. Soc. Am. B',
 'Journal of the Physical Society of Japan': 'J. Phys. Soc. Jpn.',
 'Kolloid Zeitschrift & Zeitschrift f\\{"u}r Polymere': 'Kolloid Z. Z. Polym.',
 'Kongelige Danske Videnskabernes Selskab, Matematisk-Fysiske Meddelelser': 'K. Dan. Vidensk. Selsk. Mat. Fys. Medd.',
 'Kristallografiya [Soviet PhysicsiCrystallography]': 'Kristallografiya [Sov. Phys. Crystallogr.]',
 'Kristallphysik, Kristallchemie': 'Z. Metallkd.',
 'Kvantovaya Elektronika (Moscow) [Soviet Journal of Quantum Electronics]': 'Kvant. Elektron. (Moscow) [Sov. J. Quantum Electron]',
 'Laser and Particle Beams': 'Laser Part. Beams',
 'Lettere a1 Nuovo Cimento': 'Lett. Nuovo Cimento',
 'Lick Observatory Bulletin': 'Lick Obs. Bull.',
 'Materials Research Bulletin': 'Mater. Res. Bull.',
 'Materials Science and Engineering': 'Mater. Sci. Eng.',
 'Mathematical Biosciences': 'Math. Biosci.',
 'Mathematical Physics and Applied Mathematics': 'Math. Phys. Appl. Math.',
 'Medical Physics': 'Med. Phys.',
 'Memoirs of the Royal Astronomical Society': 'Mem. R. Astron. Soc.',
 'Molecular Crystals and Liquid Crystals': 'Mol. Cryst. Liq. Cryst.',
 'Molecular Physics': 'Mol. Phys.',
 'Monthly Notices of the Royal Astronomical Society': 'Mon. Not. R. Astron Soc.',
 'National Bureau of Standards (U.S.), Circular': 'Natl. Bur. Stand. Circ. (U.S.)',
 'National Bureau of Standards (U.S.), Miscellaneous Publication': 'Natl. Bur. Stand. Misc. Publ. (U.S.)',
 'National Bureau of Standards (U.S.), Special Publication': 'Natl. Bur. Stand. Spec. Publ. (U.S.)',
 'Nature (London)': 'Nature ',
 'Naturwissenschaften': 'Naturwissenschaften',
 'New Journal of Physics': 'New J. Phys.',
 'Nuclear Data, Section A': 'Nucl. Data, Sec. A',
 'Nuclear Data, Section B': 'Nucl. Data, Sec. B',
 'Nuclear Fusion': 'Nucl. Fusion',
 'Nuclear Instruments': 'Nucl. Instrum.',
 'Nuclear Instruments & Methods': 'Nucl. Instrum. Methods',
 'Nuclear Physics': 'Nucl. Phys.',
 'Nuclear Physics A': 'Nucl. Phys. A',
 'Nuclear Physics B': 'Nucl. Phys. B',
 'Nuclear Science and Engineering': 'Nucl. Sci. Eng.',
 'Nukleonika': 'Nukleonika',
 'Nuovo Cimento': 'Nuovo Cimento',
 'Nuovo Cimento A': 'Nuovo Cimento A',
 'Nuovo Cimento B': 'Nuovo Cimento B',
 'Optica Acta': 'Opt. Acta',
 'Optics Communications': 'Opt. Commun.',
 'Optics Letters': 'Opt. Lett.',
 'Optics News': 'Opt. News',
 'Optics and Spectroscopy (USSR) [translation of Optika i Spektroskopiya]': 'Opt. Spectrosc.',
 'Optik (Stuttgart)': 'Optik (Stuttgart)',
 'Optika i Spektroskopiya [Optics and Spectroscopy (USSR)]': 'Opt. Spektrosk. [Opt. Spectrosc. (USSR)]',
 'Optiko-Mekhanicheskaya Promyshlennost [Soviet Journal of Optical Technology]': 'OptrMekh. Prom. [Sov. J. Opt. Technol.]',
 'Phase Transition and Critical Phenomena': 'Phase Transit. Crit. Phenom.',
 'Phase Transitions': 'Phase Transit.',
 'Philips Research Reports': 'Philips Res. Rep.',
 'Philosophical Magazine': 'Philos. Mag.',
 'Philosophical Transactions of the Royal Society of London': 'Philos. Trans. R. Soc. London',
 'Philosophical Transactions of the Royal Society of London, Series A: Mathematical and Physical Sciences': 'Philos. Trans. R. Soc. London, Ser. A',
 'Physica (Utrecht)': 'Physica (Utrecht)',
 'Physica A': 'Physica A',
 'Physica B': 'Physica B',
 'Physica Scripta': 'Phys. Scr.',
 'Physica Status Solidi': 'Phys. Status Solidi',
 'Physica Status Solidi A: Applied Research': 'Phys. Status Solidi A',
 'Physica Status Solidi B: Basic Research': 'Phys. Status Solidi B',
 'Physical Chemistry Chemical Physics': 'Phys. Chem. Chem. Phys.',
 'Physical Review': 'Phys. Rev.',
 'Physical Review A: Atomic, Molecular, and Optical Physics': 'Phys. Rev. A',
 'Physical Review A': 'Phys. Rev. A',
 'Physical Review B: Condensed Matter': 'Phys. Rev. B',
 'Physical Review B': 'Phys. Rev. B',
 'Physical Review C: Nuclear Physics': 'Phys. Rev. C',
 'Physical Review C': 'Phys. Rev. C',
 'Physical Review D: Particles and Fields': 'Phys. Rev. D',
 'Physical Review D': 'Phys. Rev. D',
 'Physical Review E: Statistical Physics, Plasmas, Fluids, and Related Interdisciplinary Topics': 'Phys. Rev. E',
 'Physical Review E': 'Phys. Rev. E',
 'Physical Review X': 'Phys. Rev. X',
 'Physical Review Letters': 'Phys. Rev. Lett.',
 'Physical Review Special Topics 7 Accelerators and Beams': 'Phys. Rev. Spec. Top. Accel. Beams',
 'Physics (New York)': 'Physics (N.Y.)',
 'Physics Letters': 'Phys. Lett.',
 'Physics Letters A': 'Phys. Lett. A',
 'Physics Letters B': 'Phys. Lett. B',
 'Physics Reports': 'Phys. Rep.',
 'Physics Teacher': 'Phys. Teach.',
 'Physics Today': 'Phys. Today',
 'Physics and Chemistry of Solids': 'Phys. Chem. Solids',
 'Physics of Fluids': 'Phys. Fluids',
 'Physics of Metals and Metallography (USSR) [translation of Fizika Metallovi Metallovedenie]': 'Phys. Met. Metallogr. (USSR)',
 'Physics of Plasmas': 'Phys. Plasmas',
 'Physik der Kondensierten Materie': 'Phys. Kondens. Mater.',
 'Physikalische Zeitschrift': 'Phys. Z.',
 'Physikalische Zeitschrift der Sowjetunion': 'Phys. Z. Sowjetunion',
 "Pis'ma v Astronomicheskii Zhurnal [Soviet Astronomy Letters]": "Pis'ma Astron. Zh. [Sov. Astron. Lett.]",
 "Pis'ma v Zhurnal Eksperimentalnoi i Teoreticheskoi Fiziki [JETP Letters]": "Pis'ma Zh. Eksp. Teor. Fiz. [JETP Lett.]",
 "Pis'ma v Zhurnal Tekhnicheskoi Fiziki [Soviet Technical Physics Letters]": "Pis'ma Zh. Tekh. Fiz. [Sov. Tech. Phys. Lett.]",
 'Planetary and Space Science': 'Planet. Space Sci.',
 'Plasma Physics': 'Plasma Phys.',
 'Plasma Physics and Controlled Fusion': 'Plasma Phys. Control. Fusion',
 'Pribory i Tekhnika Eksperimenta [Instruments and Experimental Techniques (USSR)]': 'Prib. Tekh. E ksp. [Instrum. Exp. Tech. (USSRH',
 'Proceedings of the Cambridge Philosophical Society': 'Proc. Cambridge Philos. Soc.',
 'Proceedings of the IEEE': 'Proc. IEEE',
 'Proceedings of the IRE': 'Proc. IRE',
 'Proceedings of the National Academy of Sciences of the United States of America': 'Proc. Natl. Acad. Sci. USA',
 'Proceedings of the Physical Society, London': 'Proc. Phys. Soc. London',
 'Proceedings of the Physical Society, London, Section A': 'Proc. Phys. Soc. London, Sec. A',
 'Proceedings of the Physical Society, London, Section B': 'Proc. Phys. Soc. London, Sec. B',
 'Proceedings of the Royal Society of London': 'Proc. R. Soc. London',
 'Proceedings of the Royal Society of London, Series A: Mathematical and Physical Sciences': 'Proc. R. Soc. London, Ser. A',
 'Progress of Theoretical Physics': 'Prog. Theor. Phys.',
 'Publications of the Astronomical Society of the Pacific': 'Publ. Astron. Soc. Pac.',
 'Quantum Electronics': 'Quantum Electron. (UK) or Quantum Electron. (USA)',
 'Quantum Optics': 'Quantum Opt.',
 'RCA Review': 'RCA Rev.',
 'Radiation Effects': 'Radiat. Eff.',
 'Radio Engineering and Electronic Physics (USSR) ': 'Radio Eng. Electron. Phys. (USSR)',
 'Radiotekhnika i Elektronika Radio Engineering and Electronics (USSR) [translation of Radiotekhnika i Elektronika]': 'Radio Eng. Electron. (USSR)',
 'Radiotekhnika i Elektronika [Radio Engineering and Electronic Physics (USSR)]': 'Radiotekh. Elektron. [Radio Eng. Electron. Phys. (USSR)]',
 'Radiotekhnika i Elektronika [Radio Engineering and Electronics (USSR)]': 'Radiotekh. Elektron. [Radio Eng. Electron. (USSR)]',
 'Reports on Progress in Physics': 'Rep. Prog. Phys.',
 'Review of Scientific Instruments': 'Rev. Sci. Instrum.',
 'Reviews of Modern Physics': 'Rev. Mod. Phys.',
 'Revista Mexicana de Astronomica y Astrofisica': 'Rev. Mex. Astron. Astrofis.',
 'Revista Mexicana de Fisica': 'Rev. Mex. Fis.',
 "Revue dOptique, Th{\\'e}orique et Instrumentale": 'Rev. Opt. Theor. Instrum.',
 'Russian Journal of Physical Chemistry [translation of Zhurnal Fizicheskoi Khimii]': 'Russ. J. Phys. Chem.',
 'Science': 'Science',
 'Scientific American': 'Sci. Am.',
 'Solar Physics': 'Sol. Phys.',
 'Solid State Communications': 'Solid State Commun.',
 'Solidistate Electronics': 'Solid-state Electron.',
 'Soviet Astronomy Letters [translation of Pisma v Astronomicheskii Zhurnal]': 'Sov. Astron. Lett.',
 'Soviet Astronomy [translation of Astronomicheskii Zhurnal]': 'Sov. Astron.',
 'Soviet Journal of Atomic Energy [translation of Atomnaya Energiya]': 'Sov. J. At. Energy',
 'Soviet Journal of Low Temperature Physics [translation of Fizika Nizkikh Temperatur]': 'Sov. J. Low Temp. Phys.',
 'Soviet Journal of Nuclear Physics [translation of Yadernaya Fizika]': 'Sov. J. Nucl. Phys.',
 'Soviet Journal of Optical Technology [translation of Optikchekhanicheskaya Promyshlennost]': 'Sov. J. Opt. Technol.',
 'Soviet Journal of Particles and Nuclei [translation of Fizika Elementarnykh Chastitsi Atomnogo Yadra]': 'Sov. J. Part. Nucl.',
 'Soviet Journal of Plasma Physics [translation of Fizika Plazmy]': 'Sov. J. Plasma Phys.',
 'Soviet Journal of Quantum Electronics [translation of Kvantovaya Elektronika (Moscow)]': 'Sov. J. Quantum Electron.',
 'Soviet Physics Journal [translation of Izvestiya Vysshikh Uchebnykh Zavedenii, Fizika]': 'Sov. Phys. J.',
 'Soviet Physics-Acoustics [translation of Akusticheskii Zhurnal]': 'Sov. Phys. Acoust.',
 'Soviet Physics-Crystallography [translation of Kristallografiya]': 'Sov. Phys. Crystallogr.',
 'Soviet Physics-Doklady [translation of Doklady Akademii Nauk SSSR]': 'Sov. Phys. Dokl.',
 'Soviet Physics-JETP [translation of Zhurnal Eksperimentalnoi i Teoreticheskoi Fiziki]': 'Sov. Phys. JETP',
 'Soviet Physics-Technical Physics [translation of Zhurnal Tekhnicheskoi Fiziki]': 'Sov. Phys. Tech. Phys.',
 'Soviet Physics-Uspekhi [translation of Uspekhi Fizicheskikh Nauk]': 'Sov. Phys. Usp.',
 'Soviet Physics-semiconductors [translation of Fizika i Tekhnika Poluprovodnikov]': 'Sov. Phys. Semicond.',
 'Soviet Physics-solid State [translation of Fizika Tverdogo Tela (Leningrad)]': 'Sov. Phys. Solid State',
 'Soviet Radiophysics [translation of Izvestiya Vysshikh Uchebnykh Zavedenii, Radiofizika]': 'Sov. Radiophys.',
 'Soviet Technical Physics Letters [translation of Pisma v Zhurnal Tekhnicheskoi Fiziki]': 'Sov. Tech. Phys. Lett.',
 'Spectrochimica Acta': 'Spectrochim. Acta',
 'Spectrochimica Acta, Part A: Molecular Spectroscopy': 'Spectrochim. Acta, Part A',
 'Spectrochimica Acta, Part B: Atomic Spectroscopy': 'Spectrochim. Acta, Part B',
 'Surface Science': 'Surf. Sci.',
 'Teplofizika Vysokikh Temperatur [High Temperature (USSR)]': 'Teplofiz. Vys. Temp. [High Temp. (USSR)]',
 'Theoretica Chimica Acta': 'Theor. Chim. Acta',
 'Thin Solid Films': 'Thin Solid Films',
 'Transactions of the American Crystallographic Association': 'Trans. Am. Crystallogr. Assoc.',
 'Transactions of the American Geophysical Union': 'Trans. Am. Geophys. Union',
 'Transactions of the American Institute of Mining, Metallurgical and Petroleum Engineers': 'Trans. Am. Inst. Min. Metall. Pet. Eng.',
 'Transactions of the American Nuclear Society': 'Trans. Am. Nucl. Soc.',
 'Transactions of the American Society for Metals': 'Trans. Am. Soc. Met.',
 'Transactions of the American Society of Mechanical Engineers': 'Trans. Am. Soc. Mech. Eng.',
 'Transactions of the British Ceramic Society': 'Trans. Br. Ceram. Soc.',
 'Transactions of the Faraday Society': 'Trans. Faraday Soc.',
 'Transactions of the Metallurgical Society of AIME': 'Trans. Metall. Soc. AIME',
 'Transactions of the Society of Rheology': 'Trans. Soc. Rheol.',
 'Ukrainian Physics Journal [translation of Ukrainskii Fizicheskii Zhurnal (Russian Edition)]': 'Ukr. Phys. J .',
 'Ultrasonics': 'Ultrasonics',
 'Uspekhi Fizicheskikh Nauk [Soviet Physics-Uspekhi]': 'Usp. Fiz. Nauk [Sov. Phys. Usp.]',
 'Vistas in Astronomy': 'Vistas Astron.',
 'Wuli Xuebao (Acta Physica Sinica) [Chinese Journal of Physics]': 'Wuli Xuebao (Acta Phys. Sin.) [Chin. J. Phys]',
 'Yadernaya Fizika [Soviet Journal of Nuclear Physics]': 'Yad. Fiz. [Sov. J. Nucl. Phys]',
 'Zeitschrift f{\\"u}r Analytische': 'Chemie Z. Anal. Chem.',
 'Zeitschrift f{\\"u}r Angewandte Physik': 'Z. Angew. Phys.',
 'Zeitschrift f{\\"u}r Anorganische und Allgemeine': 'Chemie Z. Anorg. Allg. Chem.',
 'Zeitschrift f{\\"u}r Astrophysik': 'Z. Astrophys.',
 'Zeitschrift f{\\"u}r Elektrochemie': 'Z. Elektrochem.',
 'Zeitschrift f{\\"u}r Kristallographie, Kristallgeometrie,': 'Z. Kristallogr. Kristallgeom. Kristallphys. Kristallchem.',
 'Zeitschrift f{\\"u}r Metallkunde': 'Z. Naturforsch.',
 'Zeitschrift f{\\"u}r Naturforschung': 'Z. Naturforsch. Teil A',
 'Zeitschrift f{\\"u}r Naturforschung, Teil A: Physik, Physikalische Chemie, Kosmophysik': 'Z. Phys.',
 'Zeitschrift f{\\"u}r Physik': 'Z. Phys. A',
 'Zeitschrift f{\\"u}r Physik A: Atoms and Nuclei': 'Z. Phys. B',
 'Zeitschrift f{\\"u}r Physik B: Condensed Matter and Quanta': 'Z. Phys. C',
 'Zeitschrift f{\\"u}r Physik C: Particles and Fields': 'Z. Phys. Chem. Materialforsch.',
 'Zeitschrift f{\\"u}r Physikalisch-Chemische Materialforschung': 'Z. Phys. Chem. Abt. A',
 'Zeitschrift f{\\"u}r Physikalische Chemie, Abteilung A: Chemische Thermodynamik, Kinetik, Elektrochemie, Eigenschaftslehre': 'Z. Phys. Chem. Abt. B',
 'Zeitschrift f{\\"u}r Physikalische Chemie (Leipzig)': 'Z. Phys. Chem. (Leipzig)',
 'Zeitschrift f{\\"u}r Physikalische Chemie, Abteilung B: Chemie der Elementarprozesse, Aufbau der Materie Zeitschrift f{\"u}r Physikalische Chemie (Frankfurt am Main)': 'Z. Phys. Chem. (Frankurt am Main)',
 'Zhurnal Eksperimentalnoi i Teoreticheskoi Fiziki [Soviet Physics-JETP]': 'Zh. Eksp. Teor. Fiz. [Sov. Phys. JETP]',
 'Zhurnal Fizicheskoi Khimii [Russian Journal of Physical Chemistry]': 'Zh. Fiz. Khim. [Russ J. Phys. Chem.]',
 'Zhurnal Prikladnoi Spektroskopii [Journal of Applied Spectroscopy (USSR)]': 'Zh. Prikl. Spektrosk. [J. Appl. Spectrosc. (USSR)]',
 'Zhurnal Tekhnicheskoi Fiziki [Soviet Physics-Technical Physics]': 'Zh. Tekh. Fiz. [Sov. Phys. Tech. Phys]'}

# -------------------------------------------------------------------------------
def bibtex_from_doi(doi):
    """Return a bibtex text record from a doi."""

    headers = { 'Accept': 'text/bibliography; style=bibtex', } 
    req = requests.get('http://dx.doi.org/%s'%doi, headers=headers)

    bibtex_entry = req.text.replace('},','},\n')
    bibtex_entry = bibtex_entry.replace('title','\ntitle')
    return bibtex_entry

# -------------------------------------------------------------------------------
def clean_names(names):
    """Takes a list of names and reformats them into standard bibtex format.

    :param names: a list of names
    :returns: -- a string of correctly formatted names.
    """

    authors = ''
    num_authors = len(names)

    # We want the authors to be listed as: von Last, Jr, First
    # where multiple initials are separated by a tilde, i.e A.~D.
    for i,name in enumerate(names):

        # we split the names into First, von, Last, and Jr.
        sname = bibtexparser.customization.splitname(name)

        # von names
        for vname in sname['von']:
            authors += vname + ' '

        # last names
        num_lname = len(sname['last'])
        for j,lname in enumerate(sname['last']):
            authors += lname
            if j < num_lname-1:
                authors += ' '
        authors += ', '

        # jr names
        for jname in sname['jr']:
            authors += jname
        if sname['jr']:
            authors += ', '

        # first names (could be multiple 1st names for initials)
        num_fname = len(sname['first'])
        for j,fname in enumerate(sname['first']):

            # a single initial, no period
            if len(fname) == 1:
                authors += fname + '.'

            # in case we have initials jammed together
            elif fname.count('.') > 1 and '-' not in fname:

                # split them up
                init_l = fname.split('.')

                # connect with tildes
                inits = init_l[0]
                num_init = len(init_l)-1
                for k,cinit in enumerate(init_l[1:-1]):
                    inits += '.~' + cinit.strip()
                inits += '.'
                authors += inits 
            else:
                authors += fname

            # connect separated single initials with tildes
            if j < num_fname-1:
                if fname.count('.') or len(fname)==1:
                    authors += '~'
                else:
                    authors += ' '

        # separate authors with and
        if i < num_authors-1:
            authors += ' and '

    return(authors)

# -------------------------------------------------------------------------------
def format(record):
    """Clean up record, format names, generate a new cite key, remove page
       ranges and use abbreviated journal names.

    :param record: a record
    :returns: -- formatted record
    """

    # strip any tildes from author list
    record['author'] = record['author'].replace('~',' ')

    # fix bad latex
    record = bibtexparser.customization.homogenize_latex_encoding(record)

    # split authors into list
    record = bibtexparser.customization.author(record)

    # generate a new cite-key (if appropriate)
    # standard is FirstAuthorLastName:YearXX where XX are two random 
    # characters to avoid duplicates
    if ':' not in record['ID']:
        cite_key = record['author'][0].split(',')[0] + ':' + record['year']\
            + ''.join([choice(ascii_letters[:26]) for i in range(2)])
        record['ID'] = cite_key
    
    # format author's names 
    record['author'] = clean_names(record['author'])

    # try to use abbreviated journal names
    if record['journal'] in journal_abbreviations:
        record['journal'] = journal_abbreviations[record['journal']]

    # strip multiple page numbers
    if 'pages' in record:
        if '-' in record['pages']:
            record['pages'] = record['pages'].split('-')[0]

    return record

# -------------------------------------------------------------------------------
# Begin main program
# -------------------------------------------------------------------------------

def main():

    # Get the command line arguments
    args = docopt(__doc__)

    if args['--doi']:
        bibtex_entry = bibtex_from_doi(args['--doi'])
    else:
        bibtex_entry = pyperclip.paste()

    # setup a parser customization to deal with non-english characters in Latex
    # options are needed to deal with months.
    parser = bibtexparser.bparser.BibTexParser(interpolate_strings=True, 
                                               common_strings = True, 
                                              customization=format)

    # create the bibfile object and parse to get the dictionary
    bib_database = bibtexparser.loads(bibtex_entry, parser=parser)

    # prepare a list of keys we want to delete from the entry
    remove_keys = ['month', 'keyword', 'language', 'read', 'rating',
                   'date-added', 'date-modified', 'abstract', 'local-url',
                   'file', 'uri', 'ISSN', 'issn','keywords', 'numpages']

    # Strip those keys from the dictionary
    for paper in bib_database.entries:
        for rkey in remove_keys:
            if rkey in paper:
                del paper[rkey]

    # Copy back to the pasteboard
    pyperclip.copy(bibtexparser.dumps(bib_database))

    # output to the terminal
    print(bibtexparser.dumps(bib_database))

if __name__ == '__main__':
    main()
