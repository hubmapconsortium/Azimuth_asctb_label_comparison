import difflib
 
# define original text
# taken from: https://en.wikipedia.org/wiki/Internet_Information_Services
original = 'IIS 8.5 has several improvements related'

# define modified text
edited = 'About the IIS It has several improvements related'

# initiate the Differ object

 
# calculate the difference between the two texts
diff = difflib.get_close_matches('tcell',['mesothelialcell','t'],cutoff=0.1)
 
# output the result
print (diff)