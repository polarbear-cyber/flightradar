import requests
import pandas as pd
import sqlite3


class FlightPlayback:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.kk = 0
    def get_flight_playback_data(self, flight_id, timestamp):
        url = "https://api.flightradar24.com/common/v1/flight-playback.json"
        params = {
            "flightId": str(flight_id),
            "timestamp": str(timestamp)
        }
        headers = {
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.flightradar24.com/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.1661.44",
            "Origin": "https://www.flightradar24.com",
            "Sec-Fetch-Site": "same-site",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty"
        }

        response = requests.get(url, params=params, headers=headers)
        try:
            data_list = response.json()
        except:
            print(response)
        return data_list

    def fetch_flights_from_db(self):
        query = "SELECT timestamp, flight_hex FROM flights"
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def process_flight_data(self):
        flights = self.fetch_flights_from_db()
        for a, B in flights:
            if self.kk >= 1270:
                d = self.get_flight_playback_data(B, a)
                try:
                    # print((d.keys()))
                    data_list = d["result"]["response"]['data']['flight']["track"]
                    aircraft = d["result"]["response"]['data']['flight']["aircraft"]["model"]["text"]
                    try:
                        identification = d["result"]["response"]['data']['flight']["aircraft"]["identification"]["registration"]
                    except:
                        print(data_list)
                    df = pd.DataFrame(columns=['latitude', 'longitude', 'altitude_feet', 'altitude_meters', 'speed_kmh', 'speed_kts', 'speed_mph', 'verticalSpeed_fpm', 'verticalSpeed_ms', 'heading', 'squawk', 'timestamp', 'ems'])
        
                    for data in data_list:
                        result = {'latitude': data['latitude'],
                                  'longitude': data['longitude'],
                                  'altitude_feet': data['altitude']['feet'],
                                  'altitude_meters': data['altitude']['meters'],
                                  'speed_kmh': data['speed']['kmh'],
                                  'speed_kts': data['speed']['kts'],
                                  'speed_mph': data['speed']['mph'],
                                  'verticalSpeed_fpm': data['verticalSpeed']['fpm'],
                                  'verticalSpeed_ms': data['verticalSpeed']['ms'],
                                  'heading': data['heading'],
                                  'squawk': data['squawk'],
                                  'timestamp': data['timestamp'],
                                  'ems': data['ems']}
                        df = pd.concat([df, pd.DataFrame([result])], ignore_index=True)
                    df['model']=aircraft
                    df['identification']=identification
                    # appending to flight_data table in the db
                    df.to_sql("flight_data", self.conn, if_exists="append", index=False)
                    print('Done '+str(self.kk))
                    self.kk+=1
                except:
                    print(d['errors'])
            else:
                print(self.kk)
                self.kk+=1
    def close_connection(self):
        self.conn.close()


if __name__ == "__main__":
    flight_playback = FlightPlayback("flights.db")
    flight_playback.process_flight_data()
    flight_playback.close_connection()
