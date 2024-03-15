import unittest
from random import randrange
from copy import deepcopy
from web.db_utils import *
# WARNING: these currently run on our production database which is NOT ideal! Be very careful when running tests so they don't leave behind data
# or delete data we need.

# TODO: create a development DB (out of scope for assignment right now)
class TestStationDBUtils(unittest.TestCase):
    filtered_api_response = {
            "number": 999,
            "name": "Aprils Stand New Name",
            "latitude": 123,
            "longitude": 456,
            "address": "Main St",
            "city": "Dublin",
            "accepts_cards": True,
            "total_stands": 100,
            "status": "OPEN",
            "mechanical_available": 10,
            "electric_available": 5,
            "stands_available": 5,
            "last_updated": 9372934,
        }
    test_station_row = StationRow(filtered_api_response)

    def setUp(self) -> None:
        disable_caching() # Disable caching unless explicitly testing it
        return super().setUp()

    def clean_up_stations(self, ids: list[int], table: sqla.Table):
        conn.execute(sqla.delete(table).where(table.c.Id.in_(ids)))
        conn.commit()

    def test_insert_station(self):
        print("==== TEST INSERT STATION ====")
        station = deepcopy(self.test_station_row)
        station.Id = randrange(1000, 2000)
        res = insert_station(station)
        self.assertEqual(res, station)

        # Check that it was added
        table = StationRow.table

        stmnt = sqla.select(StationRow.table).where(table.c.Id == station.Id)
        rows = conn.execute(stmnt).all()
        print("Got rows: ", rows)
        self.assertEqual(len(rows), 1)
        
        self.assertEqual(StationRow(rows[0], True), station)
        self.clean_up_stations([station.Id], StationRow.table)

    def test_update_station(self):
        print("==== TEST UPDATE STATION ====")
        station = deepcopy(self.test_station_row)
        station.Id = randrange(1000, 2000)
    
        self.clean_up_stations([station.Id], StationRow.table) # Just in case

        # Insert a station
        table = StationRow.table
        conn.execute(sqla.insert(table), station.values())
        conn.commit()

        # Update the station name
        updated_row = deepcopy(station)
        updated_row.Name = "Aprils Stand Even Newer Name"
        update_station(updated_row)
        
        # Check that it was updated to the same name
        stmnt = sqla.select(StationRow.table).where(table.c.Id == station.Id)
        rows = conn.execute(stmnt).all()
        self.assertEqual(len(rows), 1)
        
        self.assertEqual(StationRow(rows[0], True), updated_row)
        self.clean_up_stations([station.Id], StationRow.table)

    def test_delete_station(self):
        print("==== TEST DELETE STATION ====")
        station = deepcopy(self.test_station_row)
        station.Id = randrange(1000, 2000)
        self.clean_up_stations([station.Id], StationRow.table) # Just in case

        # Insert a station
        table = StationRow.table
        conn.execute(sqla.insert(table), station.values())
        conn.commit()
        
        delete_station(station.Id)

        # Check that it no longer exists
        stmnt = sqla.select(StationRow.table).where(table.c.Id == station.Id)
        rows = conn.execute(stmnt).all()
        self.assertEqual(len(rows), 0)

    def test_get_station(self):
        print("==== TEST GET STATION ====")
        station = deepcopy(self.test_station_row)
        station.Id = randrange(1000, 2000)
        self.clean_up_stations([station.Id], StationRow.table) # Just in case

        # Insert a station
        table = StationRow.table
        conn.execute(sqla.insert(table), station.values())
        conn.commit()
        
        station = get_station(station.Id)

        self.assertEqual(station, station)
        self.clean_up_stations([station.Id], StationRow.table)
class TestAvailabilityDBUtils(unittest.TestCase):
    filtered_api_response = {
            "number": 999,
            "name": "Aprils Stand New Name",
            "latitude": 123,
            "longitude": 456,
            "address": "Main St",
            "city": "Dublin",
            "accepts_cards": True,
            "total_stands": 100,
            "status": "OPEN",
            "mechanical_available": 10,
            "electric_available": 5,
            "stands_available": 5,
            "last_updated": 9372934,
        }
    test_availability_row = AvailabilityRow(filtered_api_response)
    created_ids = []

    def setUp(self) -> None:
        disable_caching() # Disable caching unless explicitly testing it
        return super().setUp()
    
    def tearDown(self) -> None:
        table = AvailabilityRow.table
        conn.execute(sqla.delete(table).where(table.c.StationId.in_(self.created_ids)))
        conn.commit()
        return super().tearDown()

    def test_insert_availability(self):
        print("==== TEST INSERT AVAILABILITY ====")
        availability = deepcopy(self.test_availability_row)
        availability.StationId = randrange(1000, 2000)
        self.created_ids.append(availability.StationId)
        print("test_insert_availability making station {}".format(availability.StationId))

        res = insert_availability(availability)
        self.assertEqual(res, availability)

        # Check that it was added
        table = AvailabilityRow.table

        stmnt = sqla.select(AvailabilityRow.table).where(table.c.StationId == availability.StationId)
        rows = conn.execute(stmnt).all()
        self.assertEqual(len(rows), 1)
        
        self.assertEqual(AvailabilityRow(rows[0], True), availability)

    def test_delete_multiple_availabilities(self):
        print("==== TEST DELETE MULTIPLE AVAILABILITIES ====")
        availability = deepcopy(self.test_availability_row)
        availability.StationId = randrange(1000, 2000)
        self.created_ids.append(availability.StationId)
    
        table = AvailabilityRow.table

        # Insert 5 availabilities with last updated ranging from 1000 - 2000
        for timestamp in range(1000, 2001, 200):
            availability = deepcopy(availability)
            availability.LastUpdated = timestamp
            conn.execute(sqla.insert(table), availability.values())      
        
        conn.commit()
        # Should delete two of the availabilities
        res = delete_availabilities(availability.StationId, 1000, 1200)
        self.assertEqual(res, 2)

        # Check that only 4 availability rows are left
        stmnt = sqla.select(AvailabilityRow.table).where(table.c.StationId == availability.StationId)
        rows = conn.execute(stmnt).all()
        self.assertEqual(len(rows), 4)
    
        # Try deleting availabilities for a non-existent Station
        res = delete_availabilities(12345, 1000, 1200)
        self.assertEqual(res, 0)
    
        # Check that still only 3 availability rows are left
        stmnt = sqla.select(AvailabilityRow.table).where(table.c.StationId == availability.StationId)
        rows = conn.execute(stmnt).all()
        self.assertEqual(len(rows), 4)
    
        # Try deleting availabilities for timestamps that don't exist
        res = delete_availabilities(availability.StationId, 2200, 4000)
        self.assertEqual(res, 0)
    
        # Check that still only 4 availability rows are left
        stmnt = sqla.select(AvailabilityRow.table).where(table.c.StationId == availability.StationId)
        rows = conn.execute(stmnt).all()
        self.assertEqual(len(rows), 4)
    
        # Try deleting availabilities for a single timestamp
        res = delete_availabilities(availability.StationId, 1800, 1800)
        self.assertEqual(res, 1)
    
        # Check that 3 availability rows are left
        stmnt = sqla.select(AvailabilityRow.table).where(table.c.StationId == availability.StationId)
        rows = conn.execute(stmnt).all()
        self.assertEqual(len(rows), 3)

    def test_get_availability(self):
        print("==== TEST GET AVAILABILITY ====")
        availability = deepcopy(self.test_availability_row)
        availability.StationId = randrange(1000, 2000)
        self.created_ids.append(availability.StationId)
        table = AvailabilityRow.table

        # Insert 5 availabilities with last updated ranging from 1000 - 2000
        for timestamp in range(1000, 2001, 200):
            availability = deepcopy(availability)
            availability.LastUpdated = timestamp
            conn.execute(sqla.insert(table), availability.values())      
        
        conn.commit()

        availability_rows = get_availability(availability.StationId, 1000, 2000)
        self.assertEqual(len(availability_rows), 6)

        availability_rows = get_availability(availability.StationId, 1000, 1000)
        self.assertEqual(len(availability_rows), 1)

        availability_rows = get_availability(availability.StationId, None, None)
        self.assertEqual(len(availability_rows), 6)

        availability_rows = get_availability(availability.StationId, 1400, None)
        self.assertEqual(len(availability_rows), 4)
    
        availability_rows = get_availability(availability.StationId, None, 1400)
        self.assertEqual(len(availability_rows), 3)

    def test_caching(self):
        pass

if __name__ == '__main__':
    unittest.main(verbosity=2)