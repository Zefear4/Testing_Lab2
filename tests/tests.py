import unittest

from main import Airplane, Airport, Flight


class AirplaneTest(unittest.TestCase):
    def test_refuel_normal(self):
        airplane = Airplane("Boeing 747", 150, 1000)
        airplane.refuel(500)
        self.assertEqual(airplane.fuel_level, 500)

    def test_refuel_overflow(self):
        airplane = Airplane("Boeing 747", 150, 1000)
        airplane.refuel(1500)
        self.assertEqual(airplane.fuel_level, 1000)

    def test_is_enough_fuel_true(self):
        airplane = Airplane("Airbus A380", 200, 1000)
        airplane.refuel(700)
        self.assertTrue(airplane.is_enough_fuel(500))

    def test_is_enough_fuel_false(self):
        airplane = Airplane("Airbus A380", 200, 1000)
        airplane.refuel(700)
        self.assertFalse(airplane.is_enough_fuel(800))

    def test_negative_refuel(self):
        airplane = Airplane("Boeing 747", 150, 1000)
        airplane.refuel(500)
        airplane.refuel(-200)
        self.assertEqual(airplane.fuel_level, 300)

    def test_zero_capacity(self):
        with self.assertRaises(ValueError):
            Airplane("Invalid Plane", 0, 1000)

    def test_negative_fuel_capacity(self):
       with self.assertRaises(ValueError):
            Airplane("Invalid Plane", 100,-1)

class AirportTest(unittest.TestCase):
    def test_park_and_remove_airplane(self):
        airport = Airport("SVO", 2, 1)
        airplane1 = Airplane("Boeing 777", 150, 1000)
        airplane2 = Airplane("Airbus A330", 200, 800)
        self.assertTrue(airport.park_airplane(airplane1))
        self.assertTrue(airport.park_airplane(airplane2))
        self.assertFalse(airport.park_airplane(airplane1))  # Нет места

        self.assertTrue(airport.remove_airplane(airplane1))
        self.assertTrue(airport.park_airplane(airplane1))

    def test_runway_availability_true(self):
        airport = Airport("JFK", 1, 2)
        self.assertTrue(airport.is_runway_available())

    def test_runway_availability_false(self):
        airport = Airport("JFK", 1, 1)
        airport.acquire_runway()
        self.assertFalse(airport.is_runway_available())


    def test_acquire_release_runway(self):
        airport = Airport("JFK", 1, 2)
        runway_index = airport.acquire_runway()
        self.assertEqual(runway_index, 0)
        airport.release_runway(runway_index)
        self.assertTrue(airport.is_runway_available())

    def test_acquire_release_multiple_runways(self):
        airport = Airport("JFK", 2, 3)
        runway1 = airport.acquire_runway()
        runway2 = airport.acquire_runway()
        runway3 = airport.acquire_runway()  # Занимаем все полосы
        self.assertIsNotNone(runway1)
        self.assertIsNotNone(runway2)
        self.assertIsNotNone(runway3)  # Проверяем что вернулись индексы полос
        self.assertFalse(airport.is_runway_available())  # все полосы заняты


    def test_release_invalid_runway(self):
        airport = Airport("SVO", 1, 1)
        airport.release_runway(1)



class FlightTest(unittest.TestCase):
    def setUp(self):
        self.airport1 = Airport("SVO", 2, 1)
        self.airport2 = Airport("JFK", 1, 1)
        self.airplane = Airplane("Boeing 787", 100, 1000)
        self.airplane.refuel(700)
        self.airport1.park_airplane(self.airplane)

    def test_successful_flight(self):
        flight = Flight(self.airport1, self.airport2, 500, self.airplane)
        self.assertTrue(flight.perform_flight())
        self.assertEqual(self.airplane.fuel_level, 200)
        self.assertTrue(self.airport2.remove_airplane(self.airplane))

    def test_not_enough_fuel(self):
        flight = Flight(self.airport1, self.airport2, 800, self.airplane)
        self.assertFalse(flight.perform_flight())
        self.assertEqual(self.airplane.fuel_level, 700)

    def test_no_hangar_at_arrival(self):
        airplane2 = Airplane("Airbus 320", 50, 500)
        self.airport2.park_airplane(airplane2)
        flight = Flight(self.airport1, self.airport2, 500, self.airplane)
        self.assertFalse(flight.perform_flight())
        self.assertEqual(self.airplane.fuel_level, 200)
        self.assertTrue(self.airport1.remove_airplane(self.airplane))

    def test_no_runway_available_at_departure(self):
        self.airport1.acquire_runway()
        flight = Flight(self.airport1, self.airport2, 500, self.airplane)
        self.assertFalse(flight.perform_flight())
        self.assertEqual(self.airplane.fuel_level, 700)
        self.assertTrue(self.airport1.remove_airplane(self.airplane))

    def test_same_departure_and_arrival_airports(self):
        flight = Flight(self.airport1, self.airport1, 100, self.airplane)
        self.assertTrue(flight.perform_flight())
        self.assertEqual(self.airplane.fuel_level, 600)

    def test_zero_distance_flight(self):
        flight = Flight(self.airport1, self.airport2, 0, self.airplane)
        self.assertTrue(flight.perform_flight())
        self.assertEqual(self.airplane.fuel_level, 700)

    def test_add_passengers_success(self):
        flight = Flight(self.airport1, self.airport2, 500, self.airplane)
        self.assertTrue(flight.add_passengers(50))
        self.assertEqual(flight.passengers, 50)

    def test_add_passengers_fail(self):
        flight = Flight(self.airport1, self.airport2, 500, self.airplane)
        self.assertTrue(flight.add_passengers(100))
        self.assertFalse(flight.add_passengers(1)) # Мест нет
        self.assertEqual(flight.passengers, 100) # Пассажиров все еще 100


    def test_remove_passengers_success(self):
        flight = Flight(self.airport1, self.airport2, 500, self.airplane)
        flight.add_passengers(70)
        self.assertTrue(flight.remove_passengers(30))
        self.assertEqual(flight.passengers, 40)

    def test_remove_passengers_fail(self):
        flight = Flight(self.airport1, self.airport2, 500, self.airplane)
        flight.add_passengers(50)
        self.assertFalse(flight.remove_passengers(60))
        self.assertEqual(flight.passengers, 50)




if __name__ == '__main__':
    unittest.main()