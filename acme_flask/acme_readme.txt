Acme Wine Company Demo App Read Me
w.mechem
4/6/2016

!!!!!!!! !!!!!!!! !!!!!! SEE INSTRUCTIONS.TXT for an explanation of what this demo does. !!!!!!!!!! !!!!!!!!!! !!!!!

Application runs a VERY basic flask http server on 127.0.0.1:5000


REST-like ENDPOINTS:
----------------------------------

/ -> welcome page

/orders -> list orders, options are: valid=1, limit=n, offset=n

/orders/<order_id> -> details on a single order (order_id)

/orders/import - uploads, validates and imports a ".csv" file

/orders/import also:

Creates orders.db if not exists.
creates orders table with columns from header from file.
Adds any columns in header from imported file that do not already exist in the orders table.


NOTES:
----------------------------------

SqLite creates a database in ./DATA 

Uploaded files are saved to ./UPLOADS

Uploaded file names are prepended with the current date and time to minimize the possibility of overwriting existing files.

Email validation could be stronger using external python libraries or regex.
Current function only tests for existence of name with minimum of two charaters (checks length of string preceding @ sign), and ensures tld is at least 2 characters.  Also checks .net / NY rule.

Zip Sum >20 rule was unclear whether to include + 4 in sum so error on side of conservative and included all 9 digits.  This is probably not what is needed.

Look ahead processing (rule 7) is done in process.processWorkFile and hands off validation of other rules to validate.validateOrder if rule 7 not applicable.  Cleaner code would be to move the processing of rule 7 to validateOrder function.

Validation is done via validateOrder function as each row is imported.  This function is essentially a pipeline of the rules functions.  

Active rules, banned states, rule messages, zipcode sum max and legal age are defined in acme_rules.py, however there is a corresponding list in validate.py that correlates the rules to the functions.  There is probably a cleaner way to do this.




TESTS:
Tests on the validation rules can be done simply by running validate.py which will fire off 12 unittest tests.


INSTALLATION:
----------------------------------

1) mkdir acme (NOTE:OR CLONE REPO)
2) cd acme
3*) virtualenv env1
4*) source env1/bin/activate
5) cp path/to/acme_mechem.zip . (NOTE:OR CLONE REPO)
6) unzip acme_wmechem.zip (NOTE:OR CLONE REPO)
7) python -m pip install -r acme_requirements.txt

*optional but reccomended.  Step 7 will install libraries into your environment

TO RUN:
----------------------------------
cd acme
python acme.py


FROM BROWSER:
http://127.0.0.1:5000/ loads "Welcome to Acme Wines"





 
