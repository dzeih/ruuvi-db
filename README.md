Small parser job to:
 - listen to RuuviTag messages with Bleak (wonderful device, wonderful package)
 - parse measurements
 - dumping parsed measurements into local db

Comes with zero error handling, lots of better examples around GitHub & blogs, but none of them worked on M1 ARM without Rosetta 2 (user errors quite likely!).
