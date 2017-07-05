#!flask/bin/python
from myapp import app_obj

# Just write from file import function, and then call the function using function(a, b). 
#The reason why this may not work, is because file is one of Python's core modules, so I 
#suggest you change the name of your file.

app_obj.run(debug=False)