from sys import argv

##### Define the number of games in the ticket plan #####

GamesInPlan = 81

# Read in the priorities

f = open (argv[1], 'r')
filedata = f.readlines ()
priority = []
for line in filedata:
  if (len (priority) == GamesInPlan):
    continue
  splitline = line.split ()
  priority.append (float (splitline[0]))
f.close ()

# Renumber the priorities so that consecutive integers are used

nprior = list (range (GamesInPlan))
for ix in range (len (priority)):
  smallest = 1000
  for iy in range (len (priority)):
    if priority[iy] < smallest:
      iz = iy
      smallest = priority[iy]
  nprior[iz] = ix + 1
  priority[iz] = 1000

# Print out the results

print (nprior)
