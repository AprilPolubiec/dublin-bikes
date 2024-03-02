import unittest
from copy import deepcopy
from web.db_utils import *

class TestUtils(unittest.TestCase):
    filtered_api_response = {
            "number": 999,
            "name": "Aprils Stand New Name",
            "latitude": 123,
            "longitude": 456,
            "address": "Main St",
            "zip": "D9ghwf",
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
    test_availability_row = AvailabilityRow(filtered_api_response)

    def setUp(self) -> None:
        disable_caching() # Disable caching unless explicitly testing it
        return super().setUp()

    def clean_up_stations(self, ids: list[int], table: sqla.Table):
        conn.execute(sqla.delete(table).where(table.c.Id.in_(ids)))
        conn.commit()

    def clean_up_availability(self, ids: list[int], table: sqla.Table):
        conn.execute(sqla.delete(table).where(table.c.StationId.in_(ids)))
        conn.commit()
    
    def test_insert_station(self):
        print("==== TEST INSERT STATION ====")
        self.clean_up_stations([self.test_station_row.Id], StationRow.table) # Just in case
        res = insert_station(self.test_station_row)
        self.assertEqual(res, self.test_station_row)

        # Check that it was added
        table = StationRow.table

        stmnt = sqla.select(StationRow.table).where(table.c.Id == self.test_station_row.Id)
        rows = conn.execute(stmnt).all()
        print("Got rows: ", rows)
        self.assertEqual(len(rows), 1)
        
        self.assertEqual(StationRow(rows[0], True), self.test_station_row)
        self.clean_up_stations([self.test_station_row.Id], StationRow.table)

    def test_update_station(self):
        print("==== TEST UPDATE STATION ====")
        self.clean_up_stations([self.test_station_row.Id], StationRow.table) # Just in case

        # Insert a station
        table = StationRow.table
        conn.execute(sqla.insert(table), self.test_station_row.values())
        conn.commit()

        # Update the station name
        updated_row = deepcopy(self.test_station_row)
        updated_row.Name = "Aprils Stand Even Newer Name"
        update_station(updated_row)
        
        # Check that it was updated to the same name
        stmnt = sqla.select(StationRow.table).where(table.c.Id == self.test_station_row.Id)
        rows = conn.execute(stmnt).all()
        self.assertEqual(len(rows), 1)
        
        self.assertEqual(StationRow(rows[0], True), updated_row)
        self.clean_up_stations([self.test_station_row.Id], StationRow.table)

    def test_delete_station(self):
        print("==== TEST DELETE STATION ====")
        self.clean_up_stations([self.test_station_row.Id], StationRow.table) # Just in case

        # Insert a station
        table = StationRow.table
        conn.execute(sqla.insert(table), self.test_station_row.values())
        conn.commit()
        
        delete_station(self.test_station_row.Id)

        # Check that it no longer exists
        stmnt = sqla.select(StationRow.table).where(table.c.Id == 999)
        rows = conn.execute(stmnt).all()
        self.assertEqual(len(rows), 0)

    def test_get_station(self):
        print("==== TEST GET STATION ====")
        self.clean_up_stations([self.test_station_row.Id], StationRow.table) # Just in case

        # Insert a station
        table = StationRow.table
        conn.execute(sqla.insert(table), self.test_station_row.values())
        conn.commit()
        
        station = get_station(self.test_station_row.Id)

        self.assertEqual(station, self.test_station_row)
    
    def test_insert_availability(self):
        print("==== TEST INSERT AVAILABILITY ====")
        self.clean_up_availability([self.test_availability_row.StationId], AvailabilityRow.table) # Just in case
        res = insert_availability(self.test_availability_row)
        self.assertEqual(res, self.test_availability_row)

        # Check that it was added
        table = AvailabilityRow.table

        stmnt = sqla.select(AvailabilityRow.table).where(table.c.StationId == self.test_availability_row.StationId)
        rows = conn.execute(stmnt).all()
        print("Got rows: ", rows)
        self.assertEqual(len(rows), 1)
        
        self.assertEqual(AvailabilityRow(rows[0], True), self.test_availability_row)
        self.clean_up_availability([self.test_availability_row.StationId], AvailabilityRow.table)

    def test_delete_single_availability(self):
        print("==== TEST DELETE SINGLE AVAILABILITY ====")
        self.clean_up_availability([self.test_availability_row.StationId], AvailabilityRow.table) # Just in case

        # Insert an availability
        table = AvailabilityRow.table
        conn.execute(sqla.insert(table), self.test_availability_row.values())
        conn.commit()
        
        delete_availabilities(self.test_availability_row.StationId, self.test_availability_row.LastUpdated, self.test_availability_row.LastUpdated)

        # Check that it no longer exists
        stmnt = sqla.select(AvailabilityRow.table).where(table.c.StationId == 999)
        rows = conn.execute(stmnt).all()
        self.assertEqual(len(rows), 0)

    def test_delete_multiple_availabilities(self):
        print("==== TEST DELETE SINGLE AVAILABILITY ====")
        self.clean_up_availability([self.test_availability_row.StationId], AvailabilityRow.table) # Just in case
        table = AvailabilityRow.table

        # Insert 5 availabilities with last updated ranging from 1000 - 2000
        for timestamp in range(1000, 2001, 200):
            availability = deepcopy(self.test_availability_row)
            availability.LastUpdated = timestamp
            conn.execute(sqla.insert(table), availability.values())      
        
        conn.commit()
        
        # Should delete two of the availabilities
        res = delete_availabilities(self.test_availability_row.StationId, 1000, 1200)
        self.assertEqual(res, 2)
    
        # Check that only 3 availability rows are left
        stmnt = sqla.select(AvailabilityRow.table).where(table.c.StationId == self.test_availability_row.StationId)
        rows = conn.execute(stmnt).all()
        self.assertEqual(len(rows), 3)
    
        # Try deleting availabilities for a non-existent Station
        res = delete_availabilities(12345, 1000, 1200)
        self.assertEqual(len(res), 0)
    
        # Check that still only 3 availability rows are left
        stmnt = sqla.select(AvailabilityRow.table).where(table.c.StationId == self.test_availability_row.StationId)
        rows = conn.execute(stmnt).all()
        self.assertEqual(len(rows), 3)
    
        # Try deleting availabilities for timestamps that don't exist
        res = delete_availabilities(12345, 2200, 4000)
        self.assertEqual(len(res), 0)
    
        # Check that still only 3 availability rows are left
        stmnt = sqla.select(AvailabilityRow.table).where(table.c.StationId == self.test_availability_row.StationId)
        rows = conn.execute(stmnt).all()
        self.assertEqual(len(rows), 3)
    
        # Try deleting availabilities for a single timestamp
        res = delete_availabilities(12345, 1800, 1800)
        self.assertEqual(len(res), 1)
    
        # Check that 2 availability rows are left
        stmnt = sqla.select(AvailabilityRow.table).where(table.c.StationId == self.test_availability_row.StationId)
        rows = conn.execute(stmnt).all()
        self.assertEqual(len(rows), 2)

    def test_get_availability(self):
        print("==== TEST GET AVAILABILITY ====")
        self.clean_up_availability([self.test_availability_row.StationId], AvailabilityRow.table) # Just in case
        table = AvailabilityRow.table

        # Insert 5 availabilities with last updated ranging from 1000 - 2000
        for timestamp in range(1000, 2001, 200):
            availability = deepcopy(self.test_availability_row)
            availability.LastUpdated = timestamp
            conn.execute(sqla.insert(table), availability.values())      
        
        conn.commit()

        availability = get_availability(self.test_availability_row.StationId, 1000, 2000)
        self.assertEqual(len(availability), 6)

        availability = get_availability(self.test_availability_row.StationId, 1000, 1000)
        self.assertEqual(len(availability), 1)

        availability = get_availability(self.test_availability_row.StationId, None, None)
        self.assertEqual(len(availability), 6)

        availability = get_availability(self.test_availability_row.StationId, 1400, None)
        self.assertEqual(len(availability), 4)
    
        availability = get_availability(self.test_availability_row.StationId, None, 1400)
        self.assertEqual(len(availability), 3)

        self.clean_up_availability([self.test_availability_row.StationId], AvailabilityRow.table)

if __name__ == '__main__':
    unittest.main(verbosity=2)