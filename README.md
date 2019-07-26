# The “jump and stay” method to discover proper verb centered constructions in corpus lattices

## What is this all about?

The “jump and stay” method is described here:
[The “jump and stay” method to discover proper verb centered constructions in corpus lattices](RANLP 2019...)

The foundation, the double cube model is described here:
[A lattice based algebraic model for verb centered constructions](http://www.nytud.hu/oszt/korpusz/resources/sb_lattice_foundation.pdf)

## Usage

Please type:

`make all`

to run the algorithm (described in section 5)
 * using verb *hagy* (*allow*) on train data
   to get the full output which Fig. 4 is based on
   (in file named `hagy.train.out3`); and
 * using verbs *húz* (*draw/pull*) and *vet* (*cast/throw*) on test data
   to get the results presented in Table 1. in the [paper](RANLP 2019...)
   (in files `huz.test.out3.pVCC` and `vet.test.out3.pVCC`).

Tested on Debian Linux. (May work on other operation systems...)

Requirements:
python 3
make
uni2ascii (if not available: sudo apt-get install uni2ascii)

## License

If you want to use it, please cite the above papers and contact me. :)
No warranty, sorry.

