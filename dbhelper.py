import mysql.connector
from mysql.connector import Error
import os
from datetime import datetime
import pandas as pd

class DB:
    def __init__(self):
        try:
            self.conn = mysql.connector.connect(
                host=os.getenv('DB_HOST', '127.0.0.1'),
                user=os.getenv('DB_USER', 'root'),
                password=os.getenv('DB_PASSWORD', ''),
                database=os.getenv('DB_NAME', 'flights')
            )
            self.mycursor = self.conn.cursor(dictionary=True)
            print('Connection established')
        except Error as e:
            print(f'Connection error: {e}')
            raise

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        if hasattr(self, 'mycursor') and self.mycursor:
            self.mycursor.close()
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()

    def fetch_city_names(self):
        try:
            self.mycursor.execute("""
                SELECT DISTINCT(Destination) as city FROM flights.flights
                UNION 
                SELECT DISTINCT(Source) as city FROM flights.flights
                ORDER BY city
            """)
            return [row['city'] for row in self.mycursor.fetchall()]
        except Error as e:
            print(f"Error fetching cities: {e}")
            return []

    def fetch_all_flights(self, source, destination, sort_by='Price'):
        try:
            query = """
                SELECT Airline, Route, Dep_time, Duration, Price, Date_of_Journey 
                FROM flights
                WHERE Source = %s AND Destination = %s
                ORDER BY {}
            """.format(sort_by)
            self.mycursor.execute(query, (source, destination))
            return self.mycursor.fetchall()
        except Error as e:
            print(f"Error fetching flights: {e}")
            return []

    def fetch_airline_freq(self):
        try:
            self.mycursor.execute("""
            SELECT Airline, COUNT(*) as count 
            FROM flights
            GROUP BY Airline
            """)
            data = self.mycursor.fetchall()
            airline = [row['Airline'] for row in data]
            frequency = [row['count'] for row in data]
            return airline, frequency
        except Error as e:
            print(f"Error fetching airline frequency: {e}")
            return [], []

    def busy_airport(self):
        try:
            self.mycursor.execute("""
            SELECT Source as city, COUNT(*) as count 
            FROM (
                SELECT Source FROM flights
                UNION ALL
                SELECT Destination FROM flights
            ) t
            GROUP BY t.Source
            ORDER BY COUNT(*) DESC
            """)
            
            data = self.mycursor.fetchall()
            city = [row['city'] for row in data]
            frequency = [row['count'] for row in data]
            return city, frequency
        except Error as e:
            print(f"Error fetching busy airports: {e}")
            return [], []

    def daily_num_flights(self):
        try:
            self.mycursor.execute("""
            SELECT Date_of_Journey, COUNT(*) as count 
            FROM flights
            GROUP BY Date_of_Journey 
            ORDER BY Date_of_Journey
            """)
            
            data = self.mycursor.fetchall()
            date = [row['Date_of_Journey'] for row in data]
            frequency = [row['count'] for row in data]
            return date, frequency
        except Error as e:
            print(f"Error fetching daily flights: {e}")
            return [], []