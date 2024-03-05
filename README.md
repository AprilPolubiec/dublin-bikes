# Dublin Bikes

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