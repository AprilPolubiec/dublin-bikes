# Dublin Bikes

## File Structure

/data
- contains sample data to be used in place of API or DB queries

/models
- /stands-and-bikes
  - pkl files for the currently used model which predicts stands and bikes available
- /stands-available
  - pkl files for a previous model predicting stands available

/scripts
- scripts that were used for DB creation - mostly for record-keeping

/tests
- files for testing code

/web
- all web app code including API scraping scripts

## Running locally
In your command line, run

```
export DBIKE_DEV=True 
```

This creates an environment variable called "DBIKE_DEV" which we can then use at various parts in the code to determine whether somebody is running this script locally or from the EC2 instance.

## Testing
All tests are contained in the `tests` directory. To run tests, run the following command: `python3 -m unittest tests.[NAME_OF_TEST_FOLDER]`

```
<!-- Examples: -->
python3 -m unittest tests.test_db_utils
python3 -m unittest tests.test_utils
```