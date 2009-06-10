import baconfile

# Let's fetch a folder
folder_items = baconfile.fetch_folder('someuser', 'somefolder')

# Iterate over the folder and print the name and size
for i in items:
  print 'name: %s  size: %i' % (i.name, i.size)

# Let's download a file
file = baconfile.fetch_file('someuser', 'somefolder/somefile.txt')
raw_data = file.read_file()

# Let's save the same file to our local system
file.save_file('somefile.txt')
