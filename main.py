from datetime import datetime, timedelta

class Airplane:
    def __init__(self, name, capacity, fuel_capacity):
        if capacity <= 0:
            raise ValueError("Вместимость не может быть отрицательной")
        if fuel_capacity < 0:
            raise ValueError("Вместимость не может быть отрицательной")

        self.name = name
        self.capacity = capacity
        self.fuel_level = 0
        self.fuel_capacity = fuel_capacity

    def refuel(self, amount):
        self.fuel_level = min(self.fuel_level + amount, self.fuel_capacity)

    def is_enough_fuel(self, distance):
        return self.fuel_level >= distance

    def __str__(self):
        return f"Самолет {self.name} (Вместимость: {self.capacity}, Топливо: {self.fuel_level}/{self.fuel_capacity})"


class Airport:
    def __init__(self, name, num_hangars, num_runways):
        self.name = name
        self.hangars = [None] * num_hangars
        self.runways = [True] * num_runways

    def park_airplane(self, airplane):
        for i, hangar in enumerate(self.hangars):
            if hangar is None:
                self.hangars[i] = airplane
                return True
        return False

    def remove_airplane(self, airplane):
        for i, hangar in enumerate(self.hangars):
            if hangar == airplane:
                self.hangars[i] = None
                return True
        return False

    def is_runway_available(self):
        return any(self.runways)

    def acquire_runway(self):
        for i, runway in enumerate(self.runways):
            if runway:
                self.runways[i] = False
                return i
        return -1

    def release_runway(self, runway_index):
        if 0 <= runway_index < len(self.runways):
            self.runways[runway_index] = True

    def __str__(self):
        return f"Аэропорт {self.name} (Ангары: {len([h for h in self.hangars if h is not None])}/{len(self.hangars)}, Полосы: {[i for i, r in enumerate(self.runways) if r]})"


class Flight:
    def __init__(self, departure_airport, arrival_airport, distance, airplane, scheduled_departure=None):
        self.scheduled_departure = scheduled_departure  # Время вылета
        self.departure_airport = departure_airport
        self.arrival_airport = arrival_airport
        self.distance = distance
        self.airplane = airplane
        self.passengers = 0

    def get_capacity(self):
        return self.airplane.capacity

    def add_passengers(self, num_passengers):
        if self.passengers + num_passengers <= self.get_capacity():
            self.passengers += num_passengers
            return True
        else:
            print("Рейс заполнен")
            return False

    def remove_passengers(self, num_passengers):
        if self.passengers - num_passengers >= 0:
            self.passengers -= num_passengers
            return True
        else:
            print("Нельзя удалить больше пассажиров")
            return False

    def perform_flight(self):
        if self.scheduled_departure is None: # Если рейс не запланирован
            print(f"Flight {self.airplane.name} not scheduled!")
            return False

        if self.departure_airport.remove_airplane(self.airplane):
            if self.airplane.is_enough_fuel(self.distance):
                runway_index = self.departure_airport.acquire_runway() #Пытаемся получить полосу
                if runway_index != -1:
                    print(f"Flight departing from {self.departure_airport.name} to {self.arrival_airport.name}...")
                    self.departure_airport.release_runway(runway_index)
                    self.airplane.refuel(-self.distance)
                    if self.arrival_airport.park_airplane(self.airplane):
                        print(f"Flight arrived at {self.arrival_airport.name}")
                        return True
                    else:
                        print(f"No hangar available at {self.arrival_airport.name}")
                        self.departure_airport.park_airplane(self.airplane)
                else:
                     # Возвращаем самолет, т.к. полосы нет
                    print(f"No runway available at {self.departure_airport.name}")
                    self.departure_airport.park_airplane(self.airplane)
            else:
                print("Not enough fuel for the flight!")
                self.departure_airport.park_airplane(self.airplane)
        else:
            print("Airplane not found at departure airport.")
        return False

    def __str__(self):
        return f"Перелет (Из: {self.departure_airport.name}, В: {self.arrival_airport.name}, Дистанция: {self.distance}, Самолет: {self.airplane.name}, Вместимость: {self.get_capacity()})"

def schedule_flights(flights, airport, start_time=datetime.now()):

    sorted_flights = sorted(flights, key=lambda flight: flight.distance, reverse=True) # Сортировка по убыванию дистанции: сначала длинные рейсы
    scheduled_flights = []
    current_time = start_time
    runway_available_time = start_time

    for flight in sorted_flights:
        departure_time = max(runway_available_time, current_time)
        flight.scheduled_departure = departure_time  # Назначаем время вылета
        scheduled_flights.append(flight)

        flight_duration = timedelta(minutes=flight.distance / 2)
        runway_available_time = departure_time + flight_duration + timedelta(minutes=30) #30 минут на обслуживание


        current_time += timedelta(minutes=15) # Интервал между вылетами: 15 минут

    return scheduled_flights
